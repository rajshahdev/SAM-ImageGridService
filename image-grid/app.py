import asyncio
import math
import io
import os
from PIL import Image
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from functools import partial
import boto3
from concurrent.futures import ThreadPoolExecutor
import tempfile
from mangum import Mangum
import os

table_name = os.environ['TABLE_NAME']
source_bucket = os.environ['SOURCE_BUCKET']
destination_bucket = os.environ['DESTINATION_BUCKET']

tile_size = 100
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize boto3 clients
s3 = boto3.client("s3")
dynamodb = boto3.client("dynamodb")

# Initialize thread pool
executor = ThreadPoolExecutor(max_workers=10)


@app.post("/add_image")
async def add_image(request: Request):
    loop = asyncio.get_running_loop()
    unique_grid_id = request.query_params.get("uniqueGridId")
    if not unique_grid_id:
        return {"message": "Missing uniqueGridId query parameter"}

    image_bytes = await request.body()
    print(image_bytes)
    object_key = os.urandom(16).hex() + ".jpg"

    put_object_partial = partial(s3.put_object, Bucket=source_bucket, Key=object_key, Body=image_bytes,
                                 ContentType='image/jpg')
    await loop.run_in_executor(executor, put_object_partial)

    put_item_partial = partial(dynamodb.put_item, TableName=table_name,
                               Item={"uniqueGridId": {"S": unique_grid_id}, "s3Key": {"S": object_key}})
    await loop.run_in_executor(executor, put_item_partial)

    return {"message": "Image saved", "image_size": len(image_bytes)}
    # except Exception as e:
    #     return {"message": "An error occurred", "error": str(e)}


@app.post("/generate_grid")
async def build_grid(request: Request):
    loop = asyncio.get_running_loop()
    # try:
    uniqueGridId = str(request.query_params.get("uniqueGridId"))

    query_partial = partial(dynamodb.query,
                            TableName=table_name,
                            KeyConditions={"uniqueGridId": {"AttributeValueList": [{"S": uniqueGridId}],
                                                            'ComparisonOperator': 'EQ'}})

    response = await loop.run_in_executor(executor, query_partial)

    source_images = [item["s3Key"]["S"] for item in response["Items"]]
    image_count = len(source_images)

    tiles_width = math.floor(math.sqrt(image_count))
    tiles_height = math.ceil(image_count / tiles_width)

    destination_image = Image.new(mode="RGB", size=(tiles_width * tile_size, tiles_height * tile_size))

    for y in range(tiles_height):
        for x in range(tiles_width):
            if source_images:
                filename = source_images.pop()

                get_object_partial = partial(s3.get_object, Bucket=source_bucket, Key=filename)
                response = await loop.run_in_executor(executor, get_object_partial)

                image_data = response['Body'].read()

                img = Image.open(io.BytesIO(image_data))
                img = img.resize((tile_size, tile_size))
                destination_image.paste(img, (x * tile_size, y * tile_size))

    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg').name
    destination_image.save(temp_file)

    destination_key = os.urandom(16).hex() + ".jpg"

    with open(temp_file, 'rb') as data:
        put_object_partial = partial(s3.put_object, Bucket=destination_bucket, Key=destination_key, Body=data,
                                     ContentType='image/jpg')
        await loop.run_in_executor(executor, put_object_partial)

    response_out_url = s3.generate_presigned_url('get_object',
                                                 Params={'Bucket': destination_bucket,
                                                         'Key': destination_key},
                                                 ExpiresIn=5 * 60)
    return {"message": "built grid", "presigned_url": response_out_url}

    # except Exception as e:
    #     return {"message": "An error occurred", "error": str(e)}


# Wrap the FastAPI app with Mangum for AWS Lambda compatibility
handler = Mangum(app, lifespan="auto")
