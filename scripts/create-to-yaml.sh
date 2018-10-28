export NAME=k8s.example.com
export KOPS_STATE_STORE=s3://example-state-store
 kops create cluster $NAME \
    --zones "us-east-2a,us-east-2b,us-east-2c" \
    --master-zones "us-east-2a,us-east-2b,us-east-2c" \
    --networking weave \
    --topology private \
    --bastion \
    --node-count 3 \
    --node-size m4.xlarge \
    --kubernetes-version v1.6.6 \
    --master-size m4.large \
    --vpc vpc-6335dd1a \
    --dry-run \
    -o yaml > $NAME.yaml
