#!/usr/bin/env bash
export AWS_REGION=us-east-1
kops create secret sshpublickey admin \
-i ~/.ssh/id_rsa.pub \
--name diamondbacksolutionsllc.com \
--state s3://diamond-state-07458