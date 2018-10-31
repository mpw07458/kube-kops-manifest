#!/usr/bin/python
# noinspection PyPep8Naming
import yaml
import sys
from jinja2 import Environment, FileSystemLoader
import subprocess


class Manifest:
    def __init__(self, manifest_template_file, manifest_data_file, state_template_file, new_manifest_file,
                 new_state_file, vers_template_file, new_vers_file, ssh_template_file, new_ssh_file, upd_template_file,
                 new_upd_file, val_template_file, new_val_file):
        self._manifest_create_inject(manifest_template_file, manifest_data_file, new_manifest_file)
        self._create_state_object(state_template_file, manifest_data_file, new_state_file)
        self._create_state_cls(self, new_state_file)
        self._create_vers_object(vers_template_file, manifest_data_file, new_vers_file)
        self._create_vers_cls(self, new_vers_file)
        self._create_ssh_key(ssh_template_file, manifest_data_file, new_ssh_file)
        self._create_ssh_cls(self, new_ssh_file)
        self._create_mfst_cls(self, new_manifest_file)
        self._create_upd_manifest(upd_template_file, manifest_data_file, new_upd_file)
        self._create_upd_cls(self, new_upd_file)
        self._create_val_manifest(val_template_file, manifest_data_file, new_val_file)
        self._create_val_cls(self, new_val_file)
        # self._install_Addons()
        # self._extract_kubecfg()
        pass

    @staticmethod
    def _manifest_create_inject(manifest_template_file, manifest_data_file, new_manifest_file):
        """
        Load data template and inject into cluster manifest
        :param manifest_template_file:
        :param manifest_data_file:
        :param new_manifest_file:
        :return:
        """
        data_file_path = "Manifest/.data_files/" + manifest_data_file
        cluster_data = yaml.load(open(data_file_path))
        # Load Jinja2 template
        env = Environment(loader=FileSystemLoader('Manifest/.templates'), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(manifest_template_file)
        # Render the template with data and print the output
        new_manifest = open("Manifest/.scripts/" + new_manifest_file, "w")
        print("Cluster Manifest ****************")
        print(template.render(cluster_data))
        print(template.render(cluster_data), file=new_manifest)
        print("Cluster Manifest Complete ************")
        pass

    @staticmethod
    def _create_state_object(state_template_file, state_data_file, new_state_file):
        """
        Load data template and inject into cluster manifest
        :param state_template_file:
        :param state_data_file:
        :param new_state_file:
        :return:
        """
        data_file_path = "Manifest/.data_files/" + state_data_file
        aws_state_data = yaml.load(open(data_file_path))
        # Load Jinja2 template
        env = Environment(loader=FileSystemLoader('Manifest/.templates'), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(state_template_file)
        # Render the template with data and print the output
        new_state = open("Manifest/.scripts/" + new_state_file, "w")
        print("State Manifest ****************")
        print(template.render(aws_state_data))
        print(template.render(aws_state_data), file=new_state)
        print("State Manifest Complete ****************")
        pass

    @staticmethod
    def _create_state_cls(self, new_state_file):
        """
        use kops to deploy a kubernetes cluster based on a manifest from templated values
        :param self:
        :param new_state_file:
        :return:
        """
        state_file_path = "Manifest/.scripts/" + new_state_file
        exc_cmd = 'chmod +x ./' + state_file_path
        bucket_cmd = './' + state_file_path
        # Render the template with data and print the output
        self._k8s_command_helper_sys(exc_cmd)
        self._k8s_command_helper_sys(bucket_cmd)
        pass

    @staticmethod
    def _create_vers_object(vers_template_file, vers_data_file, new_vers_file):
        """
        Load data template and inject into cluster manifest
        :param vers_template_file:
        :param vers_data_file:
        :param new_vers_file:
        :return:
        """
        data_file_path = "Manifest/.data_files/" + vers_data_file
        aws_vers_data = yaml.load(open(data_file_path))
        # Load Jinja2 template
        env = Environment(loader=FileSystemLoader('Manifest/.templates'), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(vers_template_file)
        # Render the template with data and print the output
        new_vers = open("Manifest/.scripts/" + new_vers_file, "w")
        print("State Manifest ****************")
        print(template.render(aws_vers_data))
        print(template.render(aws_vers_data), file=new_vers)
        pass

    @staticmethod
    def _create_vers_cls(self, new_vers_file):
        """
        use kops to deploy a kubernetes cluster based on a manifest from templated values
        :param self:
        :param new_vers_file:
        :return:
        """
        vers_file_path = "Manifest/.scripts/" + new_vers_file
        exc_cmd = 'chmod +x ./' + vers_file_path
        vers_cmd = './' + vers_file_path
        # Render the template with data and print the output
        self._k8s_command_helper_sys(exc_cmd)
        self._k8s_command_helper_sys(vers_cmd)
        pass

    @staticmethod
    def _create_ssh_key(ssh_template_file, ssh_data_file, new_ssh_file):
        """
        Load data template and inject into cluster manifest
        :param ssh_template_file:
        :param ssh_data_file:
        :param new_ssh_file:
        :return:
        """
        data_file_path = "Manifest/.data_files/" + ssh_data_file
        aws_ssh_data = yaml.load(open(data_file_path))
        # Load Jinja2 template
        env = Environment(loader=FileSystemLoader('Manifest/.templates'), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(ssh_template_file)
        # Render the template with data and print the output
        new_ssh = open("Manifest/.scripts/" + new_ssh_file, "w")
        print("State Manifest ****************")
        print(template.render(aws_ssh_data))
        print(template.render(aws_ssh_data), file=new_ssh)
        pass

    @staticmethod
    def _create_ssh_cls(self, new_ssh_file):
        """
        use kops to deploy a kubernetes cluster based on a manifest from templated values
        :param self:
        :param new_ssh_file:
        :return:
        """
        ssh_file_path = "Manifest/.scripts/" + new_ssh_file
        exc_cmd = 'chmod +x ./' + ssh_file_path
        ssh_cmd = './' + ssh_file_path
        # Render the template with data and print the output
        self._k8s_command_helper_sys(exc_cmd)
        self._k8s_command_helper_sys(ssh_cmd)
        pass

    @staticmethod
    def _create_mfst_cls(self, new_manifest_file):
        """
        use kops to deploy a kubernetes cluster based on a manifest from templated values
        :param self:
        :param new_manifest_file:
        :return:
        """
        manifest_file_path = "Manifest/.scripts/" + new_manifest_file
        kops_cmd = 'kops create -f ' + manifest_file_path
        # Render the template with data and print the output
        self._k8s_command_helper_sys(kops_cmd)
        pass

    @staticmethod
    def _install_Addons(template_file, data_file):
        """
        Load data from YAML into Python dictionary
        :param template_file:
        :param data_file:
        :return:
        """
        data_file_path = "j2Template/.data_files/" + data_file
        config_data = yaml.load(open(data_file_path))
        # Load Jinja2 template
        env = Environment(loader=FileSystemLoader('j2Template/.templates'), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(template_file)
        # Render the template with data and print the output
        print(template.render(config_data))
        pass

    @staticmethod
    def _extract_kubecfg(template_file, data_file):
        """
        Load data from YAML into Python dictionary
        :param template_file:
        :param data_file:
        :return:
        """
        data_file_path = "j2Template/.data_files/" + data_file
        config_data = yaml.load(open(data_file_path))
        # Load Jinja2 template
        env = Environment(loader=FileSystemLoader('j2Template/.templates'), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(template_file)
        # Render the template with data and print the output
        print(template.render(config_data))
        pass

    @staticmethod
    def _create_upd_manifest(upd_template_file, upd_data_file, new_upd_file):
        """
        Load data template and inject into cluster manifest
        :param upd_template_file:
        :param upd_data_file:
        :param new_upd_file:
        :return:
        """
        data_file_path = "Manifest/.data_files/" + upd_data_file
        aws_upd_data = yaml.load(open(data_file_path))
        # Load Jinja2 template
        env = Environment(loader=FileSystemLoader('Manifest/.templates'), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(upd_template_file)
        # Render the template with data and print the output
        new_upd = open("Manifest/.scripts/" + new_upd_file, "w")
        print("State Manifest ****************")
        print(template.render(aws_upd_data))
        print(template.render(aws_upd_data), file=new_upd)
        pass

    @staticmethod
    def _create_upd_cls(self, new_upd_file):
        """
        use kops to deploy a kubernetes cluster based on a manifest from templated values
        :param self:
        :param new_upd_file:
        :return:
        """
        upd_file_path = "Manifest/.scripts/" + new_upd_file
        exc_cmd = 'chmod +x ./' + upd_file_path
        upd_cmd = './' + upd_file_path
        # Render the template with data and print the output
        self._k8s_command_helper_sys(exc_cmd)
        self._k8s_command_helper_sys(upd_cmd)
        pass

    @staticmethod
    def _create_val_manifest(val_template_file, val_data_file, new_val_file):
        """
        Load data template and inject into cluster manifest
        :param val_template_file:
        :param val_data_file:
        :param new_val_file:
        :return:
        """
        data_file_path = "Manifest/.data_files/" + val_data_file
        aws_val_data = yaml.load(open(data_file_path))
        # Load Jinja2 template
        env = Environment(loader=FileSystemLoader('Manifest/.templates'), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(val_template_file)
        # Render the template with data and print the output
        new_val = open("Manifest/.scripts/" + new_val_file, "w")
        print("State Manifest ****************")
        print(template.render(aws_val_data))
        print(template.render(aws_val_data), file=new_val)
        pass

    @staticmethod
    def _create_val_cls(self, new_val_file):
        """
        use kops to deploy a kubernetes cluster based on a manifest from templated values
        :param self:
        :param new_val_file:
        :return:
        """
        val_file_path = "Manifest/.scripts/" + new_val_file
        exc_cmd = 'chmod +x ./' + val_file_path
        val_cmd = './' + val_file_path
        # Render the template with data and print the output
        self._k8s_command_helper_sys(exc_cmd)
        self._k8s_command_helper_sys(val_cmd)
        pass

    @staticmethod
    def _k8s_command_helper_sys(cmd):

        """
        kubernetes Command Helper - sends shell scripts to Shell
        :param cmd:
        :return:
        """
        print(cmd)
        try:
            retcode = subprocess.call([cmd], shell=True)
            if retcode < 0:
                print(sys.stderr, "Child was terminated by signal", -retcode)
            else:
                print(sys.stderr, "Child returned", retcode)
        except OSError as e:
            print(sys.stderr, "Execution failed:", e)

    @staticmethod
    def _k8s_command_helper(cmd):
        """
        kubernetes Command Helper -  sends non-executable
        shell commands to a command Shell
        :param cmd:
        :return:
        """
        print(cmd)
        try:
            retcode = subprocess.call([cmd], shell=True)
            if retcode < 0:
                print(sys.stderr, "Child was terminated by signal", -retcode)
            else:
                print(sys.stderr, "Child returned", retcode)
        except OSError as e:
            print(sys.stderr, "Execution failed:", e)
