# 🖼️ Grid Maker: AWS SAM Application

Welcome to the Grid Maker project. Built on AWS Serverless Application Model (SAM), this application seamlessly merges services like Lambda, API Gateway, DynamoDB, and S3 to provide an efficient solution for managing image grids.

## 📚 Table of Contents

- [🌟 Features](#-features)
- [🛠️ Requirements](#-requirements)
- [🚀 Initial Setup](#-initial-setup)
- [🌐 Deployment](#-deployment)
- [🖥️ Usage](#-usage)
- [🧹 Cleanup](#-cleanup)

## 🌟 Features

- **S3 Buckets**: Source and destination for image storage.
- **API Gateway**: Provides a RESTful interface for our application.
- **Lambda Function**: Processes and manages image grids.
- **DynamoDB Table**: A NoSQL database to hold metadata of the grids.

## 🛠️ Requirements

- AWS Command Line Interface (CLI)
- AWS SAM Command Line Interface (SAM CLI)
- Proper AWS IAM permissions

## 🚀 Initial Setup

### Create Essential S3 Bucket

To accommodate deployment artifacts, you need an S3 bucket:

1. Make the provided script executable:

   ```bash
   chmod +x create_s3_bucket.sh
    ```
2. Execute the script to create the bucket:
    ```bash
    ./create_s3_bucket.sh
    ```

This action establishes an S3 bucket titled `lab-sam-cli`.

## 🌐 Deployment

1. **Build the App**: Compile the application with SAM:
```bash
sam build
```

2. **Deploy**: Utilizing the SAM CLI, initiate the deployment:
```bash
sam deploy --guided
```

The `--guided flag` ensures you're walked through the deployment process, adopting configurations from `samconfig.toml`.

## 🖥️ Usage

After a successful deployment, an API Gateway endpoint URL will be presented for the Prod stage. This URL serves as the main entry point to your application.

## 🧹 Cleanup
To ensure no lingering resources:

1. Erase the CloudFormation stack:
```bash
aws cloudformation delete-stack --stack-name lab-sam
```
2. Purge the S3 bucket, `lab-sam-cli`, if it's no longer in use.
