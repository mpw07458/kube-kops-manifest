source vault.env
kubectl create -f k8s-cls-admin.yaml
kubectl create -f helm-tiller-rbac.yaml
helm init --service-account tiller
