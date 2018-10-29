#!/usr/bin/env bash
export NAME="diamondbacksolutionsllc.com"
export KOPS_STATE_STORE="s3://k8s-state-07458"
kops rolling-update cluster \
	       $NAME \
	      --state=$KOPS_STATE_STORE \
	      --v 10 \
          --yes