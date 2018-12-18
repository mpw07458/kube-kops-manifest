#!/usr/bin/env bash
export AWS_REGION=us-east-1
kops create -f diamondbacksolutionsllc.com.yaml \
--state s3://diamond-state-07458