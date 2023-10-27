#!/bin/bash

# AWS CLI command to create an S3 bucket named "lab-sam-cli" in the "ap-south-1" region
aws s3api create-bucket --bucket lab-sam-cli --region ap-south-1 --create-bucket-configuration LocationConstraint=ap-south-1

# Output message for confirmation
echo "S3 bucket 'lab-sam-cli' has been created in the 'ap-south-1' region."
