#!/usr/bin/python
# noinspection PyPep8Naming
from Manifest import *

manifest_template_file = "original-k8s-manifest.yaml"
manifest_data_file = "k8s-cluster-feed.yaml"
state_template_file = "aws-bucket.yaml"
new_manifest_file = "new-k8s-manifest.yaml"
new_state_file = "create-aws-state.sh"
vers_template_file = "aws-bucket-vers.yaml"
new_vers_file = "create-aws-vers.sh"
ssh_template_file = "aws-ssh-secret.yaml"
new_ssh_file = "create-aws-ssh-key.sh"
upd_template_file = "aws-update-cls.yaml"
new_upd_file = "update_cls.sh"
val_template_file = "aws-validate-cls.yaml"
new_val_file = "validate_cls.sh"


def test_manifest():
    """
    Test creation of a KOPS kubeconfig file via Jinga2 template
    :return:
    """
    print("***************************************************************************************************")
    print("Configure Manifest for Cluster...")
    print("***************************************************************************************************")
    Manifest(manifest_template_file, manifest_data_file, state_template_file, new_manifest_file, new_state_file,
             vers_template_file, new_vers_file, ssh_template_file, new_ssh_file, upd_template_file, new_upd_file,
             val_template_file, new_val_file)
    print("***************************************************************************************************")
    print("Manifest Configuration Complete")
    print("***************************************************************************************************")
    return


if __name__ == "__main__":
    test_manifest()
