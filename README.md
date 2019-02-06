# Offline k8s-kops-manifest

## Offline Framework to install KOPS cluster in private subnets with HA using KOPS manifests and Jinja2 Injection / Python

## Pre-requisites
---

```
### Before running the scripts below you must install KOPS, Kubectl, Docker and Python 3.6
```

$ tar zxvf addons.tar
```
> KUBECTL
```
$ cd addons/kubectl-client
$ tar zxvf kubectl.tar.gz
$ chmod +x kubectl
$ cp -pR kubectl /usr/local/bin/.
```
> Verify the kubectl command comes back with Usage and Available Commands
> KOPS
```
$ cd ../kops-client
$ tar zxvf kops.tar.gz
$ chmod +x kops
$ cp -pR kops /usr/local/bin/.
```
> Verify the kops command comes back with Usage and Available Commands
> PYTHON 3.6
```
$ vi /etc/yum.conf
```
> Change gpgcheck=1 to gpgcheck=0
```
$ cd ../python36
$ rpm -ivh *.rpm
```
> Verify that python36 can be executed and you get back 3.6.6
> DOCKER
```
$ cd ../docker1806
$ rpm -ivh *.rpm
```
> Verify that docker version is 18.06.1-ce, ‘docker -v’
> HELM
```
$ cd ../helm
$ tar zxvf helm.tar.gz 
$ chmod +x helm
$ cp -pR helm /usr/local/bin/.
```
## QUICK START
---
### Clone the kube-kops-manifest from Github and move it to the environment you  want to install the k8s cluster to.  You will have to SFTP it up.

```
$ git clone << repo >>
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
export KOPS_STATE_BUCKET=<<state bucket>>
export AWS_REGION=<< aws region >>
export KOPS_STATE_STORE=s3://$KOPS_STATE_BUCKET
export KUBERNETES_CLUSTER=<< cluster name>> 
export VAULT_ADDR=<<vault URI>>
export NODEUP_URL=<<artifactory URI>>
/artifactory/list/offline-kops
/kops/1.11.0-alpha.1/linux/amd64/nodeup
```
> Ensure data feed and template files exist for your cluster, including chef_template.  These will have to be created or modified according to the environment you are working on.
```
$ ls Manifest/.data_files/*-feed.yaml
Manifest/.data_files/<<cluster-name>>-feed.yaml  Manifest/.data_files/<<cluster-name>>-feed.yaml

$ ls Manifest/.templates/*-template.yaml
Manifest/.templates/chef-template.yaml           Manifest/.templates/<<cluster-name>>-template.yaml
Manifest/.templates/<<cluster-name>>-template.yaml
```
```
$ ssh-keygen -y -f qa-key.pem  > k8s_qa_key.pub
$ ssh-keygen -f k8s_qa_key.pub -I -mPKCS8 > k8s_qa_key2.pub
$ cp k8s_qa_key2.pub k8s_qa_key.pub
```
> k8s_qa_key.pub is the key that is used by Kubernetes, we set it in the *-feed.yaml


## Ensure Hashicorp Vault is working and connecting correctly

> Log into Vault and print vault token

```
$ source vault.env
$ vault login -method=ldap username=$USER
$ ls -a ~/.vault-token
$ cat ~/.vault-token
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
$ export AWS_REGION=<< cluster name>>
$ export KOPS_STATE_STORE=s3://<< s3 store>>
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
<<cluster name>>   aws     << zones>>
```
> Run the following command to export the kube config
```
$ kops export kubecfg --name <<cluster store>> --state s3://<< cluster store>>
$ kubectl config view
$ kubectl get nodes
$ kops edit cluster ---name <<cluster store>> --state s3://<< cluster store>>
```

### Deleting a KOPS Kubernetes cluster
>If for some reason step 4 above fails and the cluster does not create in AWS, run the delete command below to delete the cluster, then after making any configuration changes run step 5 above again

```
$ ./delete-kops-cluster.sh
```

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
cluster_name: << cluster name >>
asset_bucket:<< bucket name>>
state_root: s3://<< bucket name>>
state_base: s3://<< bucket name>>/<< cluster name>>
additional_sg_base: sg-XXXXXXXX
additional_sg_ssh: sg-XXXXXXXX
master_internal_name: api.internal.<< cluster name >>
master_public_name: api.<< cluster name >>
master_zone: <<zones>>
network_cidr: XXX.XXX.XXX.XXX/XX
non_masq_cidr: XXX.XXX.XXX.XXX/XX
registry_mirror: https://<<artifactory uri>>
network_id: vpc-XXXXXXXX
subnet_cidr: XXX.XXX.XXX.XXX/XX
subnet_zone: << zones >>
pub_priv: Private
pub_priv_zone: private
master_image: ami-XXXXXX
master_type: m5.large
master_min: 1
master_max: 1
node_image: ami-XXXXXX
node_type: m5.2xlarge
node_min: 3
node_max: 3
node_zone: << zones >>
bucket_name: << bucket name>>
bucket_region: <<region >>
ssh_key_file: ~/.ssh/id_rsa.pub
manifest_name: Manifest/.scripts/<<cluster-name>>-manifest.yaml
http_proxy: XXX.XXX.XXX.XXX
http_proxy_exclude: << exclude list>>
private_1a_cidr: XXX.XXX.XXX.XXX/XX
private_1a_id: subnet-XXXXXXXX
private_1a_egress: nat-XXXXXXXX
private_1a_name: < zone >
private_1a_type: Private
private_1a_zone: << zone >>
private_1b_cidr: XXX.XXX.XXX.XXX/XX
private_1b_id: subnet-XXXXXXXX
private_1b_egress: nat-XXXXXXXX
private_1b_name: < zone >
private_1b_type: Private
private_1b_zone: < zone >
private_1c_cidr: XXX.XXX.XXX.XXX/XX
private_1c_id: subnet-XXXXXXXX
private_1c_egress: nat-XXXXXXXX
private_1c_name: < zone >
private_1c_type: Private
private_1c_zone: < zone >
utility_1a-cidr: XXX.XXX.XXX.XXX/XX
utility_1a_id: subnet-XXXXXXXX
utility_1a_name: utility-us-<< az >>
utility_1a_type: Utility
utility_1a_zone: << zone >>
utility_1b_cidr: XXX.XXX.XXX.XXX/XX
utility_1b_id: subnet-XXXXXXXX
utility_1b_name: utility-<< az>>
utility_1b_type: Utility
utility_1b_zone: us-gov-west-1b
utility_1c_cidr: XXX.XXX.XXX.XXX/XX
utility_1c_id: subnet-XXXXXXXX
utility_1c_name: utility-<< az>>
utility_1c_type: Utility
utility_1c_zone:<< zone >>

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
    - instanceGroup: master-<< region az >>
      name: a
    - instanceGroup: master-<< region az >>
      name: b
    - instanceGroup: master-<< region az >>
      name: c
    image: {{artifactory_uri}}/etcd-amd64:3.2.24
    name: main
    version: 3.2.24
  - etcdMembers:
    - instanceGroup: master-<< region az >>
      name: a
    - instanceGroup: master-<< region az >>
      name: b
    - instanceGroup: master-<< region az >>
      name: c
    image: {{artifactory_uri}}/etcd-amd64:3.2.24
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
  name: master-<< region az >>
spec:
  additionalUserData:
  associatePublicIp: false
  image: {{ master_image }}
  machineType: {{ master_type }}
  maxSize: {{ master_max }}
  minSize: {{ master_min }}
  nodeLabels:
    kops.k8s.io/instancegroup: master-<< region az >>
  cloudLabels:
    type: k8s
    subtype: master
  role: Master
  rootVolumeSize: 128
  subnets:
  - << region az >>

---

apiVersion: kops/v1alpha2
kind: InstanceGroup
metadata:
  creationTimestamp: null
  labels:
    kops.k8s.io/cluster: {{ cluster_name }}
  name: master-<< region az >>
spec:
  associatePublicIp: false
  image: {{ master_image }}
  machineType: {{ master_type }}
  maxSize: {{ master_max }}
  minSize: {{ master_min }}
  nodeLabels:
    kops.k8s.io/instancegroup: master-<< region az >>
  cloudLabels:
    type: k8s
    subtype: master
  role: Master
  rootVolumeSize: 128
  subnets:
  - << region az >>

---

apiVersion: kops/v1alpha2
kind: InstanceGroup
metadata:
  creationTimestamp: null
  labels:
    kops.k8s.io/cluster: {{ cluster_name }}
  name: master-<< region az >>
spec:
  associatePublicIp: false
  image: {{ master_image }}
  machineType: {{ master_type }}
  maxSize: {{ master_max }}
  minSize: {{ master_min }}
  nodeLabels:
    kops.k8s.io/instancegroup: master-<< region az >>
  cloudLabels:
    type: k8s
    subtype: master
  role: Master
  rootVolumeSize: 128
  subnets:
  - << region az >>

---

apiVersion: kops/v1alpha2
kind: InstanceGroup
metadata:
  creationTimestamp: null
  labels:
    kops.k8s.io/cluster: {{ cluster_name }}
  name: nodes
spec:
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
  - << region az >>
  - << region az >>
  - << region az >>
```

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
