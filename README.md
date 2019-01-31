# Offline k8s-kops-manifest

## Offline Framework to install KOPS cluster in private subnets with HA using KOPS manifests and Jinja2 Injection / Python

## Pre-requisites
---

### Setup Steps for AWS and CHEF
```
1. Create s3 bucket: ns2-<ENV>1-kube
This is where the k8s state store will be saved.

2. Create a Chef user k8s_svc add to the Admin group.  The PEM key for this user will be checked into vault later in the install.  chef-client-key

3. In the VPC Update the DNS hostnames, disable it

4. Create the workload and utility k8s subnets, ensure that these subnets are associated to the right route table, utility will be using the Edge Load-Balancer Route Table - AZ1
```
### Before running the scripts below you must install KOPS, Kubectl, Docker and Python 3.6
```
On the CHEF Workstation - I.e. c98pacm01w01 or c97qacm01w01
Download the source-addons from the offline-kops folder in Artifactory.

$ wget https://artifactory.devs.ns2.priv/artifactory/list/ns2-custom-generic/offline-kops/source-addons.tar.gz

$ tar zxvf source-addons.tar
```
> KUBECTL
```
$ cd source-addons/kubectl-client
$ tar zxvf kubectl.tar.gz
$ chmod +x kubectl
$ cp -pR kubectl /usr/local/bin/.

Verify the kubectl command comes back with Usage and Available Commands
```
> KOPS
```
$ cd ../kops-client
$ tar zxvf kops.tar.gz
$ chmod +x kops
$ cp -pR kops /usr/local/bin/.

Verify the kops command comes back with Usage and Available Commands
```
> PYTHON 3.6
```
$ vi /etc/yum.conf
Change gpgcheck=1 to gpgcheck=0

$ cd ../python36
$ rpm -ivh *.rpm

Verify that python36 can be executed and you get back 3.6.6
```
> DOCKER
```
$ cd ../docker1806
$ rpm -ivh *.rpm

Verify that docker version is 18.06.1-ce, ‘docker -v’
```
> HELM
```
$ cd ../helm
$ tar zxvf helm.tar.gz 
$ chmod +x helm
$ cp -pR helm /usr/local/bin/.

Verify the helm command comes back with Usage and Available Commands
```
### Transfer the BIZX and LMS K8S repos
```
From https://git.devs.ns2.priv/ns2-k8s move over the following repos: bizx-qa, bizx-upgrade, helm-bizx-logging, lms-helm
```

## QUICK START
---
### Clone the k8s-kops-manifest from Github and move it to the environment you  want to install the k8s cluster to.  You will have to SFTP it up.

```
$ git clone git@git.devs.ns2.priv:ns2-k8s/k8s-kops-manifest.git
```
> Once you have the k8s-kops-manifest folder in the right workstation, change to it.
```
$ cd k8s-kops-manifest
```
> Update the "vault.env" file and ensure proper settings exist for the cluster you are deploying.  The KUBERNETES_CLUSTER and the KOPS_STATE_BUCKET will be modified when working on the difference environments.
```
$ vi vault.env

export OFFLINE_INSTALL=1
export KUBERNETES_VERSION="v1.10.11"
export KOPS_VERSION="1.11.0-alpha.1"
export ASSET_BUCKET="offline-kops"
export ASSET_PREFIX=""
export KOPS_STATE_BUCKET="ns2-qa1-kube"
export AWS_REGION=us-gov-west-1
export KOPS_STATE_STORE=s3://$KOPS_STATE_BUCKET
export KUBERNETES_CLUSTER=qaworkload 
export VAULT_ADDR=http://vault.dccx.ns2.priv
export NODEUP_URL=http://artifactory.dccx.ns2.priv
/artifactory/list/offline-kops
/kops/1.11.0-alpha.1/linux/amd64/nodeup
```
> Ensure data feed and template files exist for your cluster, including chef_template.  These will have to be created or modified according to the environment you are working on.
```
$ ls Manifest/.data_files/*-feed.yaml
Manifest/.data_files/devsmscluster-feed.yaml  Manifest/.data_files/qaworkload-feed.yaml

$ ls Manifest/.templates/*-template.yaml
Manifest/.templates/chef-template.yaml           Manifest/.templates/qaworkload-template.yaml
Manifest/.templates/devsmscluster-template.yaml
```
   > When you are building ACE, the files would be named ace-stg-feed.yaml and ace-stg-template.yaml, ensure that the settings are correct for the ACE environment.
   
   > Make sure that the ami that you are using in your yaml is the newest working one.  As of Jan 11, 2019 that was 
   ami-c75237a6 (2018-V3.8-LINUX-RHEL7-K8S)

   > Make sure that the ssh key is in the correct format, KOPS needs to have it in mPKCS8.
```
$ ssh-keygen -y -f qa-key.pem  > k8s_qa_key.pub
$ ssh-keygen -f k8s_qa_key.pub -I -mPKCS8 > k8s_qa_key2.pub
$ cp k8s_qa_key2.pub k8s_qa_key.pub
```
> k8s_qa_key.pub is the key that is used by Kubernetes, we set it in the *-feed.yaml

> If you want to modify the Chef Runlist, you can edit it in the 
chef-template.yaml and chef-template-nofips.yaml

## Ensure Hashicorp Vault is working and connecting correctly

> Log into Vault and print vault token

```
$ source vault.env
$ vault login -method=ldap username=$USER
$ ls -a ~/.vault-token
$ cat ~/.vault-token
```
> Print the Chef client key and chef ca cert
```
$ vault kv get secret/chef_client_key
$ vault kv get secret/chef_ca_cert
```
> If the above step fails to print ca cert and client key you must add them to vault
```
$ vault write secret/chef_client_key value=@chef_client.pem
$ vault write secret/chef_ca_cert value=@chef_key.pem
```

> Make sure that the format is correct, without modifying the PEM file.  Uploading from the GUI to Vault will cause error and the formatting with be broken.  User the Vault CLI from the workstation.

## Creating a KOPS Kubernetes cluster

> The script "create-kops-cluster.sh" sets up python virtualenv and jinja2 and PyYaml tools to ensure k8s-kops-manifest works correctly and installs the kops cluster
```
$  chmod +x *.sh
$ ./create-kops-cluster.sh

```
> Once the script has completed successfully, login into govcloud console
```
1. go to EC2 and search for {cluster name}
2. go to load balancers search for {cluster name}
3. see if load balancer for has joined the cluster masters
```
> Login to one of the master server via ssh
```
$ cd /var/log

$ less messages
$ less cloud-init.log
$ cd /etc/chef
$ less STDOUT
```
> After the cluster is completed and load balancer is working test kubectl and kops
```
$ source vault.env
```
or
```
$ export AWS_REGION=us-gov-west-1
$ export KOPS_STATE_STORE=s3://ns2-qa1-kube
```
> then these commands
```
$ kubectl get nodes
$ kubectl config view
```
> If kube config is empty run this command
```
$ kops get clusters
NAME                    CLOUD   ZONES
workload01.k8s.local    aws     us-gov-west-1a,us-gov-west-1b,us-gov-west-1c
```
> Run the following command to export the kube config
```
$ kops export kubecfg --name workload01.k8s.local --state s3://ns2-qa1-kube
$ kubectl config view
$ kubectl get nodes
$ kops edit cluster --name workload01.k8s.local --state s3://ns2-qa1-kube
```

### Deleting a KOPS Kubernetes cluster
>If for some reason step 4 above fails and the cluster does not create in AWS, run the delete command below to delete the cluster, then after making any configuration changes run step 5 above again

```
$ ./delete-kops-cluster.sh
```

### Install no-fips instance group
```
$ kops create ig -f no-fips.yaml

$ kops get ig
```
### Install helm, tiller, and RBAC for cluster administrator
```
$ cat install-rbac-helm-tiller.sh
source vault.env
kubectl create -f k8s-cls-admin.yaml
kubectl create -f helm-tiller-rbac.yaml
helm init --service-account tiller

$ chown +x install-rbac-helm-tiller.sh
$ ./install-rbac-helm-tiller.sh
```
> Install Ingress Controller
```
$ cd ingress-controller
$ cat ingress-helm-deploy.sh
 helm install stable/nginx-ingress --name internal --namespace ingress-nginx -f values.yaml --set controller.replicaCount=3 --set rbac.create=true

$ chmod +x *.sh
$ ./ingress-helm-deploy.sh
$ kubectl apply -f patch-configmap-l4.yaml
$ cd ..
```
>Install SFTP server
```
$ cd sftp
$ source set_env
$ make
$ chmod +x s3fs-tls-secret.sh
$ ./s3fs-tls-secret.sh
$ kubectl create -f s3fs-ingress.yaml
```
> Install ETCD Backup and Restore
```
$ cd etcd-backup-restore
$ chmod +x *.sh
$ etcd-backup-tls-secret.sh
$ helm-etcd-operator.sh
$ cd ..
```

> Replacing the template and feed for a new cluster manifest

The kops installer k8s-kops-manifest takes templates with jinja syntax and injest from feeds, each cluster must have a feed and a template file. 

> Below are examples of Feed and template files, (partial section) Key Value pair Feed file

> Feed files are stored in Manifest/.data_files directory and named for {{ cluster_name }}-feed.yaml and provide the Key Value pairs for the jinja syntax injection

```
cluster_name: devsmscluster.k8s.local
asset_bucket: ns2-assets-kube3
state_root: s3://ns2-dev-kube3
state_base: s3://ns2-dev-kube3/devsmscluster.k8s.local
additional_sg_base: sg-e3ca5186
additional_sg_ssh: sg-e2ca5187
master_internal_name: api.internal.devsmscluster.k8s.local
master_public_name: api.devsmscluster.k8s.local
master_zone: us-gov-west-1a, us-gov-west-1b, us-gov-west-1c
network_cidr: 10.23.0.0/16
non_masq_cidr: 100.64.0.0/10
registry_mirror: https://docker.artifactory.devs.ns2.priv
network_id: vpc-b508add0
subnet_cidr: 10.23.0.0/16
subnet_zone: us-gov-west-1a, us-gov-west-1b, us-gov-west-1c
pub_priv: Private
pub_priv_zone: private
master_image: ami-c75237a6
master_type: m5.large
master_min: 1
master_max: 1
node_image: ami-c75237a6
node_type: m5.2xlarge
node_min: 3
node_max: 3
node_zone: us-gov-west-1a, us-gov-west-1b, us-gov-west-1c
bucket_name: ns2-dev-kube3
bucket_region: us-gov-west-1
ssh_key_file: ~/.ssh/id_rsa.pub
manifest_name: Manifest/.scripts/devsmscluster-manifest.yaml
chef_script_name: chef-boot.sh
http_proxy: proxy.devs.ns2.priv
http_proxy_exclude: "chef,repo,repo.devs.ns2.priv,gems,satellite,s3-us-gov-west-1.amazonaws.com,localhost,localhost.localdomain,*.devs.ns2.priv,*.devw.ns2.priv,chef.devs.ns2.priv,127.0.0.1,trend.devs.ns2.priv,c02dasm01d01.devs.ns2.priv,169.254.169.254,*.ns2.priv"
private_1a_cidr: 10.23.6.0/23
private_1a_id: subnet-e4e63b92
private_1a_egress: nat-025282436e67bec6b
private_1a_name: us-gov-west-1a
private_1a_type: Private
private_1a_zone: us-gov-west-1a
private_1b_cidr: 10.23.8.0/23
private_1b_id: subnet-f9f1549d
private_1b_egress: nat-025282436e67bec6b
private_1b_name: us-gov-west-1b
private_1b_type: Private
private_1b_zone: us-gov-west-1b
private_1c_cidr: 10.23.10.0/23
private_1c_id: subnet-7beaea3d
private_1c_egress: nat-025282436e67bec6b
private_1c_name: us-gov-west-1c
private_1c_type: Private
private_1c_zone: us-gov-west-1c
utility_1a-cidr: 10.23.0.0/23
utility_1a_id: subnet-3aed304c
utility_1a_name: utility-us-gov-west-1a
utility_1a_type: Utility
utility_1a_zone: us-gov-west-1a
utility_1b_cidr: 10.23.2.0/23
utility_1b_id: subnet-43fb5e27
utility_1b_name: utility-us-gov-west-1b
utility_1b_type: Utility
utility_1b_zone: us-gov-west-1b
utility_1c_cidr: 10.23.4.0/23
utility_1c_id: subnet-2bf7f76d
utility_1c_name: utility-us-gov-west-1c
utility_1c_type: Utility
utility_1c_zone: us-gov-west-1c

```
> Example template or templated manifest:
> Template files are stored in Manifest/.templates directory and named for {{ cluster_name }}-template.yaml
Templates have jinja synatx and are injected with KV values in the feed file.

```
apiVersion: kops/v1alpha2
kind: Cluster
metadata:
  creationTimestamp: null
  name: {{ cluster_name }}
spec:
  api:
    loadBalancer:
      type: Internal
  authorization:
    rbac: {}
  channel: stable
  cloudProvider: aws
  clusterDNSDomain: cluster.local
  configBase: {{ state_base }}
  configStore: {{ state_base }}
  docker:
    registryMirrors:
    - {{ registry_mirror }}
  egress:
    httpProxy:
      host: {{ http_proxy }}
      port: 80
    excludes: {{ http_proxy_exclude }}
  etcdClusters:
  - etcdMembers:
    - instanceGroup: master-us-gov-west-1a
      name: a
    - instanceGroup: master-us-gov-west-1b
      name: b
    - instanceGroup: master-us-gov-west-1c
      name: c
    image: docker.artifactory.devs.ns2.priv/etcd-amd64:3.2.24
    name: main
    version: 3.2.24
  - etcdMembers:
    - instanceGroup: master-us-gov-west-1a
      name: a
    - instanceGroup: master-us-gov-west-1b
      name: b
    - instanceGroup: master-us-gov-west-1c
      name: c
    image: docker.artifactory.devs.ns2.priv/etcd-amd64:3.2.24
    name: events
    version: 3.2.24
  fileAssets:
  - content: "apiVersion: audit.k8s.io/v1beta1 # This is required.\nkind: Policy\n#
      Don't generate audit events for all requests in RequestReceived stage.\nomitStages:\n
      \ - \"RequestReceived\"\nrules:\n  # Log pod changes at RequestResponse level\n
      \ - level: RequestResponse\n    resources:\n    - group: \"\"\n      # Resource
      \"pods\" doesn't match requests to any subresource of pods,\n      # which is
      consistent with the RBAC policy.\n      resources: [\"pods\"]\n  # Log \"pods/log\",
      \"pods/status\" at Metadata level\n  - level: Metadata\n    resources:\n    -
      group: \"\"\n      resources: [\"pods/log\", \"pods/status\"]\n\n  # Don't log
      requests to a configmap called \"controller-leader\"\n  - level: None\n    resources:\n
      \   - group: \"\"\n      resources: [\"configmaps\"]\n      resourceNames: [\"controller-leader\"]\n\n
      \ # Don't log watch requests by the \"system:kube-proxy\" on endpoints or services\n
      \ - level: None\n    users: [\"system:kube-proxy\"]\n    verbs: [\"watch\"]\n
      \   resources:\n    - group: \"\" # core API group\n      resources: [\"endpoints\",
      \"services\"]\n\n  # Don't log authenticated requests to certain non-resource
      URL paths.\n  - level: None\n    userGroups: [\"system:authenticated\"]\n    nonResourceURLs:\n
      \   - \"/api*\" # Wildcard matching.\n    - \"/version\"\n\n  # Log the request
      body of configmap changes in kube-system.\n  - level: Request\n    resources:\n
      \   - group: \"\" # core API group\n      resources: [\"configmaps\"]\n    #
      This rule only applies to resources in the \"kube-system\" namespace.\n    #
      The empty string \"\" can be used to select non-namespaced resources.\n    namespaces:
      [\"kube-system\"]\n\n  # Log configmap and secret changes in all other namespaces
      at the Metadata level.\n  - level: Metadata\n    resources:\n    - group: \"\"
      # core API group\n      resources: [\"secrets\", \"configmaps\"]\n\n  # Log
      all other resources in core and extensions at the Request level.\n  - level:
      Request\n    resources:\n    - group: \"\" # core API group\n    - group: \"extensions\"
      # Version of group should NOT be included.\n\n  # A catch-all rule to log all
      other requests at the Metadata level.\n  - level: Metadata\n    # Long-running
      requests like watches that fall under this rule will not\n    # generate an
      audit event in RequestReceived.\n    omitStages:\n      - \"RequestReceived\"
      \   \n"
    name: audit.yaml
    path: /srv/kubernetes/audit.yaml
    roles:
    - Master
    - Node
    - Bastion
  iam:
    allowContainerRegistry: true
    legacy: false
  keyStore: {{ state_base }}/pki
  kubeAPIServer:
    auditLogMaxAge: 10
    auditLogMaxBackups: 1
    auditLogMaxSize: 100
    auditLogPath: /var/log/kube-apiserver-audit.log
    auditPolicyFile: /srv/kubernetes/audit.yaml
    runtimeConfig:
      autoscaling/v2beta1: "true"
  kubeControllerManager:
    horizontalPodAutoscalerUseRestClients: true
  kubelet:
    enableCustomMetrics: true
  kubernetesApiAccess:
  - 10.0.0.0/8
  kubernetesVersion: 1.12.3
  masterInternalName: {{ master_internal_name }}
  masterPublicName: {{ master_public_name }}
  networkCIDR: {{ network_cidr }}
  networkID: {{ network_id }}
  networking:
    canal: {}
  nonMasqueradeCIDR: {{ non_masq_cidr }}
  sshAccess:
  - 10.0.0.0/8
  subnets:
  - cidr: {{ private_1a_cidr }}
    id: {{ private_1a_id }}
    egress: {{ private_1a_egress }}
    name: {{ private_1a_name }}
    type: {{ private_1a_type }}
    zone: {{ private_1a_zone}}
  - cidr: {{ private_1b_cidr }}
    id: {{ private_1b_id }}
    egress: {{ private_1b_egress }}
    name: {{ private_1b_name }}
    type: {{ private_1b_type }}
    zone: {{ private_1b_zone }}
  - cidr: {{ private_1c_cidr }}
    id: {{ private_1c_id }}
    egress: {{ private_1c_egress }}
    name: {{ private_1c_name }}
    type: {{ private_1c_type }}
    zone: {{ private_1c_zone }}
  - cidr: {{ utility_1a_cidr }}
    id: {{ utility_1a_id }}
    name: {{ utility_1a_name }}
    type: {{ utility_1a_type }}
    zone: {{ utility_1a_zone }}
  - cidr: {{ utility_1a_cidr }}
    id: {{ utility_1b_id }}
    name: {{ utility_1b_name }}
    type: {{ utility_1b_type }}
    zone: {{ utility_1b_zone }}
  - cidr: {{ utility_1c_cidr }}
    id: {{ utility_1c_id }}
    name: {{ utility_1c_name }}
    type: {{ utility_1c_type }}
    zone: {{ utility_1c_zone }}
  topology:
    dns:
      type: Public
    masters: private
    nodes: private

---

apiVersion: kops/v1alpha2
kind: InstanceGroup
metadata:
  creationTimestamp: null
  labels:
    kops.k8s.io/cluster: {{ cluster_name }}
  name: master-us-gov-west-1a
spec:
  additionalUserData:
  - name: {{ chef_script_name }}
    type: text/x-shellscript
    content: {% include 'chef-manifest.yaml' %}
  associatePublicIp: false
  image: {{ master_image }}
  machineType: {{ master_type }}
  maxSize: {{ master_max }}
  minSize: {{ master_min }}
  nodeLabels:
    kops.k8s.io/instancegroup: master-us-gov-west-1a
  cloudLabels:
    type: k8s
    subtype: master
  role: Master
  rootVolumeSize: 128
  subnets:
  - us-gov-west-1a

---

apiVersion: kops/v1alpha2
kind: InstanceGroup
metadata:
  creationTimestamp: null
  labels:
    kops.k8s.io/cluster: {{ cluster_name }}
  name: master-us-gov-west-1b
spec:
  additionalUserData:
  - name: {{ chef_script_name }}
    type: text/x-shellscript
    content: {% include 'chef-manifest.yaml' %}
  associatePublicIp: false
  image: {{ master_image }}
  machineType: {{ master_type }}
  maxSize: {{ master_max }}
  minSize: {{ master_min }}
  nodeLabels:
    kops.k8s.io/instancegroup: master-us-gov-west-1b
  cloudLabels:
    type: k8s
    subtype: master
  role: Master
  rootVolumeSize: 128
  subnets:
  - us-gov-west-1b

---

apiVersion: kops/v1alpha2
kind: InstanceGroup
metadata:
  creationTimestamp: null
  labels:
    kops.k8s.io/cluster: {{ cluster_name }}
  name: master-us-gov-west-1c
spec:
  additionalUserData:
  - name: {{ chef_script_name }}
    type: text/x-shellscript
    content: {% include 'chef-manifest.yaml' %}
  associatePublicIp: false
  image: {{ master_image }}
  machineType: {{ master_type }}
  maxSize: {{ master_max }}
  minSize: {{ master_min }}
  nodeLabels:
    kops.k8s.io/instancegroup: master-us-gov-west-1c
  cloudLabels:
    type: k8s
    subtype: master
  role: Master
  rootVolumeSize: 128
  subnets:
  - us-gov-west-1c

---

apiVersion: kops/v1alpha2
kind: InstanceGroup
metadata:
  creationTimestamp: null
  labels:
    kops.k8s.io/cluster: {{ cluster_name }}
  name: nodes
spec:
  additionalUserData:
  - name: {{ chef_script_name }}
    type: text/x-shellscript
    content: {% include 'chef-manifest.yaml' %}
  associatePublicIp: false
  image: {{ node_image }}
  machineType: {{ node_type }}
  maxSize: {{ node_max }}
  minSize: {{ node_min }}
  nodeLabels:
    kops.k8s.io/instancegroup: nodes
  cloudLabels:
    type: k8s
    subtype: worker
  role: Node
  rootVolumeType: standard
  subnets:
  - us-gov-west-1a
  - us-gov-west-1b
  - us-gov-west-1c
```

1)  Chef feed, templates and client key and CA cert file

Each environment in NS2 has a chef environment and a chef script that is used in nodeup to join servers to the AD domain, each environment has a specific set of chef client key and ca cert. These need to be replaced so that the chef script that runs on each server will have the client key and ca cert.

In order for the scripts to run correctly copy the current client key environment in Manifest/.templates and rename it "chef-client-key.yaml" and copy the ca cert into Manifest/.templates and rename it "chef-ca-cert.yaml"
The yaml files are key value pair files and they are stored in a key value format, the certificates are stored as strings.

Here is the chef ca cert file in a yaml key-value format

```
chef_ca_cert: '-----BEGIN CERTIFICATE-----\nMIIDlTCCAn2gAwIBAgIQfb34Z5Q+uo5IbVoByC1xOzANBgkqhkiG9w0BAQUFADBd\nMRQwEgYKCZImiZPyLGQBGRYEcHJpdjETMBEGCgmSJomT8ixkARkWA25zMjEUMBIG\nCgmSJomT8ixkARkWBGRldnMxGjAYBgNVBAMTEWRldnMtQzAyRFNBVTAxLUNBMB4X\nDTE3MDUwNjAzMzQzOFoXDTIyMDUwNjAzNDQzOFowXTEUMBIGCgmSJomT8ixkARkW\nBHByaXYxEzARBgoJkiaJk/IsZAEZFgNuczIxFDASBgoJkiaJk/IsZAEZFgRkZXZz\nMRowGAYDVQQDExFkZXZzLUMwMkRTQVUwMS1DQTCCASIwDQYJKoZIhvcNAQEBBQAD\nggEPADCCAQoCggEBAK1yY02ghUrivjihy49B+9KV4Ccq7hX/9ewEr4jCy0M2bhKl\nPFBPIm56VuCZMJ3tnEXGlz5VSjRSEGf4zhbwZWvH+Z7cGIWtXrTxy9nU8V9sToob\nZco8CAHl4OBfAfr14QPFG0KpGWBEqiQr7MjWKxKa5dgRjc6sCLQ3o6MOHJEs9dI+\nmCAZtrFRk5n7mRTGthDiua6dPlxponR9uM5LkZ2IHJMpZkjbU2JmyWxf7vxigOrd\n7UUbzn5V+5rNZXsA7Jz3mDPCqtrhkxhAUy3j6xzXr419GcmmaEF1+PzCbxkFovlm\n6R4UIKr+F0ds7FA+wzzp5wE7GXN3tYy5PVHKv0ECAwEAAaNRME8wCwYDVR0PBAQD\nAgGGMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFHrEkzPgg83+/cBNXTSbjPmc\naSenMBAGCSsGAQQBgjcVAQQDAgEAMA0GCSqGSIb3DQEBBQUAA4IBAQBd/nApPLYN\nr6JQRne4rHEmsdOC93OxCWhqT5xattEhcgUhfeFKgMhH9HNS8tcT09P5er3R2+iT\n+k/C2DTgh7obgbQdsoqPhZeYYrTzVgV/cUiawLi4jGuO5KSlXektjnBwdB6CJdY8\n7rb8+3lBHXigjFZxABiFNgx7d8lkkOjgkvH/+CJtJtVNCUfuvH9J7MxYfdRliyJR\ntNp0hH1YVSUmMW+nMhg5X4QPy/pys2gzEMVf5IbMG7DRftW/ZzM56kYDaSIsnD25\nHJ8sS27uRO6uK4+aYRfIDLO3h10p0rjzbO0vftAKbgO0aG784ILA2SS5TR6+cBvt\nilhgTGlkwUZg\n-----END
CERTIFICATE-----'
```

Here is the chef client key file in a yaml key-value format

```
chef_client_key: '----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA19ZXMZVMTY/IwMX08aIP5Cb6soeX0JELqKI2+Ye1eBoWqx7B\nA2PVsjLTgqToZa7uHaAkWm/ynwq+Zltk9qrPuhIvffCiZD5MI1qUknhXCA2QuTA6\nA49UB4eOvtry+1PYfbjGLYXmUVFwNGJof6ag50HybHyacJ5OwQprN4+EAIU61WmP\nzczUjjN0szFcCT7wFD2dS/Jnuz5IDzHoK8UOlFP+/a9sPmvgrl8aNrvVkFxo4qUA\nNfY+wzrYxZKFWCaBIq87KhZffm4SF0AIZftx+MTKPrglQ9UZb7hjta4jjazSiQca\nG52H7seqyaitCBA9viTo2pmF1kUfkKfnkimohwIDAQABAoIBAQChVdq/eXYb1Aqf\n7lj19cojJO/oW2qjwIgSeY7WXxbKu9WN++MTAaFPHqbz1QjSWTwscPQ7lcqqD4Hb\nSR3jNDMqR0WwwhrhC6AmHSNJiSKlJl6zztTOrGiHaFDPYSKXs0j0URXyGVDcIB/b\nSGQMZyWHN8haR5m57Nu5eGxEj8aAC7c65D5wOcOorFeavhZXjfvKSpU+7hSxedLz\n5BLzCjH5jfZDX7AnoTkl4R1/sahd87cqSmLMt0hc1D5d0O5QRSC94iEz36ARbOIa\nqFRm1ao1boFfp3FIEn7xVM+ywu69y6lREPO6QS+5mU5+AFQ2TsYj/euj3lU7UNu9\nRAysRHwhAoGBAPAxQ+CsnNFNM7n1XYKEG8p/3bIB3IqPsrhgJbbfs3/ANpfZKdMt\nv7QXVGm7Pd0tO1vtA94NKmOf/lTw3n1lCUSU21oLAuQV5yH7iBtcT2i8lLdENAji\nslZh+VmKRy3ZJkRU3mYcFpbk7axSxWEsCG9fv3er1H12DfEOotCUZl49AoGBAOYK\nvgTPFEZhwQooNyI2X29IS8VdAZcFjRW/RgQ8F7gSV/lqWU6HP57UfCeQILin4P9s\nuiC4xA2znFwasL+jv4XTEIYkBpsnk4YnKR76xzm8JxeQ43c/Zj4BqmHRgVTk3KOV\nc3LI4baZjgggEAnKv7rfY4q3hzdw4qI3Wu26F/ITAoGAf9ppfD3Fl6/VmeXe6aty\ns57OnoNZJrSI+JXNXYPEI3toU/n3xn5yreVBPKq7qnD6SNtoFJnDd5Zhpks002Cl\nx0jJXivAVTLHfpJKh+3iIylGrCr028n4Df1G4n+1ldUiBnt6irXm3Fltni3M/QWY\nU9iOrZ/ckw/1KdyVlBt6Ri0CgYAtyS2Q33Z1m7dEQkTW9mOATq9mFODgIia2kV9q\nMFu4M053QgeMbbbn8frUFQeuORu7OvTA1oWPBJS2cEmFmx3fkObVDA6Uiwf9x4WT\nuO42O5C8TAY6EdBTvxkeZwiK0RJpLLHRwtHJ+j4et+L5T/VhSF0Tmvu6uSkiiEn8\nzvE9KQKBgAG7BryNb2fDbY2hE1P02geZISeDO/XMZ8Crw+0I6R/64PpCwTqDTHz8\nCWQ0hKtYMNeGRYGFp94njhAzqh7RkXf9GrHWLteYusL6ZnIvj704KXlwrzKDy5J4\ngBF9Bc+MHMd5GK9ybqc2jD14AG6QfGBgsUAkB4hzIev2Nk0oTnHY\n-----END
      RSA PRIVATE KEY-----'

```
There is a section of the {{ cluster_name }}-feed.yaml that contains other chef feed key value pairs

```
chef_script_name: chef-boot.sh
chef_rpm: "https://packages.chef.io/files/stable/chef/12.21.31/el/7/chef-12.21.31-1.el7.x86_64.rpm"
chef_val_name: "i831737"
chef_key_fname: "etc/chef/i831737.pem"
chef_cert_fname: "/etc/chef/ca-cert.pem"
chef_env: "dev-k8s"
chef_domain: "devs.ns2.priv"
chef_server_url: "https://chef.devs.ns2.priv//organizations/development"
chef_http_proxy: "http://proxy:80"
chef_https_proxy: "http://proxy:80"
chef_http_noproxy: "chef,repo,gems,satellite,s3-us-gov-west-1.amazonaws.com,localhost,localhost.localdomain,*.devs.ns2.priv,*.devw.ns2.priv,chef.devs.ns2.priv,127.0.0.1,trend.devs.ns2.priv"


```
> Run offline setup script for RHEL (this is a one time event and occurs in DEV environment for the benefit of offline environments)

> The script "k8s-kops-aws-offline-setup.sh" sets up the offline tools to ensure all images and tools for kops and kubernetes are setup in a s3 asset bucket in AWS

```
$  chmod +x ./*.sh

$ ./k8s-kops-aws-offline-setup.sh

$ ./cleanup-kops-bin.sh
```
> If the offline bucket create fails, please make sure the "aws client" and "curl" are working correctly and run the script "cleanup-kops-bin.sh" and "delete-asset-bucket.sh" before recreating the asset bucket

```
$ ./delete-asset-bucket.sh

```
