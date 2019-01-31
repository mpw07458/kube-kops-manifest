#!/usr/bin/env bash
# export AWS_REGION=us-gov-west-1a
source vault_env
aws s3 mb s3://$(ASSET_BUCKET)
