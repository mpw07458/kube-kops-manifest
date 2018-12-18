# Offline k8s-kops-manifest

## Offline Framework to install KOPS cluster in private subnets with HA using KOPS manifests and Jinja2 Injection / Python

## QUICK START

1. Clone the k8s-kops-manifest on a machine that has F5 access to the AWS GovCloud

```
$ git clone

$ cd k8s-kops-manifest

```
2. Check "vault.env" file and ensure proper settings exist for the cluster you are deploying
```
$ cat vault.env
export KUBERNETES_CLUSTER=devcluster
export VAULT_ADDR=http://
```
3. Ensure data feed and template files exist for your cluster, along with chef template
```
$ ls Manifest/.data_files/*-feed.yaml
Manifest/.data_files/devcluster-feed.yaml
```
```
$ ls Manifest/.templates/*-template.yaml
Manifest/.templates/devcluster-template.yaml
```
4.  Run offline setup script for RHEL (this is a one time event and occurs in DEV environment for the benefit of offline environments)

The script "k8s-kops-aws-offline-setup.sh" sets up the offline tools to ensure all images and tools for kops and kubernetes are setup in a s3 asset bucket in AWS

```
$  chmod +x ./*.sh

$ ./k8s-kops-aws-offline-setup.sh

$ ./cleanup-kops-bin.sh
```
If the offline bucket create fails, please make sure the "aws client" and "curl" are working correctly and run the script "cleanup-kops-bin.sh" and "delete-asset-bucket.sh" before recreating the asset bucket

```
$ ./delete-asset-bucket.sh

```

5.  Run setup script

The script "k8s-kops-manifest-setup.sh" sets up python virtualenv and jinja2 and PyYaml tools to ensure k8s-kops-manifest works correctly

```
$  chmod +x ./k8s-kops-manifest-setup.sh

$  ./k8s-kops-manifest-setup.sh
```
    
6. Creating a KOPS Kubernetes cluster
   
```
$ ./venv/bin/python3.6 create_k8s_cluster.py
```
    
7. Deleting a KOPS Kubernetes cluster

```

$ ./venv/bin/python3.6 create-k8s-cluster.py --delete

```

