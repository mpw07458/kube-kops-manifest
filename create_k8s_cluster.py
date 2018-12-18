#!/usr/bin/python
# noinspection PyPep8Naming
from Manifest import *

_cluster_name = os.environ["KUBERNETES_CLUSTER"]
manifest_template_file = _cluster_name + "-template.yaml"
manifest_data_file = _cluster_name + "-feed.yaml"
new_manifest_file = _cluster_name + "-manifest.yaml"
state_template_file = "aws-bucket.yaml"
state_shell_file = "create-aws-state.sh"
vers_template_file = "aws-bucket-vers.yaml"
vers_shell_file = "create-aws-vers.sh"
ssh_template_file = "aws-ssh-secret.yaml"
ssh_shell_file = "create-aws-ssh-key.sh"
upd_template_file = "aws-update-cls.yaml"
upd_shell_file = "update_cls.sh"
val_template_file = "aws-validate-cls.yaml"
val_shell_file = "validate_cls.sh"
kops_template_file = "aws-create-kops-cls.yaml"
kops_shell_file = "create-k8s-cluster.sh"
kops_del_template_file = "aws-delete-kops-cls.yaml"
kops_del_shell_file = "delete-k8s-cluster.sh"
chef_manifest_file = "chef-template.yaml"
chef_shell_file = "chef-manifest.yaml"
pre_build_manifest_file = "aws-prebuild-cls.yaml"
pre_build_shell_file = "aws-pre-build-cls.sh"
ca_cert_file = "chef-ca-cert.yaml"
client_key_file = "chef-client-key.yaml"


def run_all_manifests():
    """
    Test creation of a KOPS kubeconfig file via Jinja2 template
    :return:
    """
    print("***************************************************************************************************")
    print("Configure Manifest for Cluster...")
    print("***************************************************************************************************")
    Manifest(manifest_template_file, manifest_data_file, new_manifest_file, state_template_file,
             state_shell_file, vers_template_file, vers_shell_file, ssh_template_file, ssh_shell_file,
             upd_template_file, upd_shell_file, val_template_file, val_shell_file, kops_template_file,
             kops_shell_file, kops_del_template_file, kops_del_shell_file, chef_manifest_file, chef_shell_file,
             pre_build_manifest_file, pre_build_shell_file, ca_cert_file, client_key_file)
    print("***************************************************************************************************")
    print("Manifest Configuration Complete")
    print("***************************************************************************************************")
    return


if __name__ == "__main__":
    run_all_manifests()
