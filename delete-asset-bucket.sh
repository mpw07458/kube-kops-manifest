#!/usr/bin/env bash
# export AWS_REGION=us-gov-west-1
source vault_env
aws s3 rb s3://$(ASSET_BUCKET) --force
