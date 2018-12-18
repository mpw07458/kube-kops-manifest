#!/usr/bin/env bash
export KUBERNETES_VERSION=1.12.3
export AWS_REGION=us-east-1
export NAME=diamondbacksolutionsllc.com
export KOPS_STATE_STORE=s3://diamond-state-07458
kops create cluster diamondbacksolutionsllc.com \
	--cloud aws \
	--node-count 3 \
	--admin-access '10.0.0.0/8' \
	--ssh-access '10.0.0.0/8' \
	--zones="us-east-1a,us-east-1b,us-east-1c" \
	--master-zones "us-east-1a,us-east-1b,us-east-1c" \
	--ssh-public-key "~/.ssh/id_rsa.pub" \
	--node-size t2.micro \
	--master-size t2.medium \
	--networking canal \
	--dns-zone diamondbacksolutionsllc.com \
    --topology private \
    --api-loadbalancer-type internal \
	--master-volume-size 128 \
	--dry-run \
	-o yaml > $NAME.yaml
