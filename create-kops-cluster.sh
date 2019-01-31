./k8s-kops-manifest-setup.sh
source vault.env
./venv/bin/python3.6 create_k8s_cluster.py
