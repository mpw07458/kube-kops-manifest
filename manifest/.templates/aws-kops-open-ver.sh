#!/usr/bin/env bash
export AWS_REGION=us-east-1
aws s3api put-bucket-versioning --bucket diamond-state-07458  --versioning-configuration Status=Enabled