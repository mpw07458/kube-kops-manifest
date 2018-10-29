#!/usr/bin/env bash
kops create cluster \
--node-count 6 \
--admin-access '10.0.0.0/8' \
--ssh-access '10.0.0.0/8' \
--zones us-gov-west-1a,us-gov-west-1b \
--master-zones us-gov-west-1a \
--ssh-public-key ~/.ssh/sbx2-key.pub \
--node-size t2.xlarge \
--master-size m3.medium \
--associate-public-ip=false \
--api-loadbalancer-type internal \
--network-cidr 172.20.0.0/16 \
--topology private \
--networking canal \
--image ami-799b0518 \
--master-volume-size 128 \
ns2devcluster1.k8s.local