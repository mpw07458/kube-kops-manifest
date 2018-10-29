#!/usr/bin/env bash
export NAME="diamondbacksolutionsllc.com"
export KOPS_STATE_STORE="s3://k8s-state-07458"
kops validate cluster \
	       $NAME \
	      --state=$KOPS_STATE_STORE \