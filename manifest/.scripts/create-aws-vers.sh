#!/usr/bin/env bash
aws s3api put-bucket-versioning \
--bucket diamond-state-07458 \
 --versioning-configuration \
 Status=Enabled
