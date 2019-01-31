#!/usr/bin/python
# noinspection PyPep8Naming
#import pdb
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pprint import pprint, pformat
import yaml
import hvac
import socket
import urllib3
from jinja2 import Environment, FileSystemLoader

_vault_uri = os.environ['VAULT_ADDR'] #'http://vault.devs.ns2.priv'
_data_path = "Manifest/.data_files/"
_template_path = "Manifest/.templates/"
_script_path = "Manifest/.scripts/"
_token_file_path = os.environ['HOME']+"/.vault-token"


class Manifest:
    def __init__(self, manifest_template_file, manifest_data_file, new_manifest_file, state_template_file,
                 state_shell_file, vers_template_file, vers_shell_file, ssh_template_file, ssh_shell_file,
                 upd_template_file, upd_shell_file, val_template_file, val_shell_file, kops_template_file,
                 kops_shell_file, kops_del_template_file, kops_del_shell_file, chef_template_file,
                 chef_manifest_file, chef_nofips_template_file, chef_nofips_manifest_file,
                 prebuild_template_file, prebuild_shell_file, ca_cert_file, client_key_file):
        self._start_logger(self)        
        self._remove_tmp_manifest()
        self._create_tmp_manifest()
        print("token file path is: ",_token_file_path)
        if os.path.isfile(_token_file_path):
            self._vault_client = self._get_vault_client(_vault_uri)
            try:
                assert self._vault_client.is_authenticated(), 'Connected to Vault'
                logging.info('Connected to Vault')
                self._ca_cert_file = self._vault_client.read('secret/chef_ca_cert')['data']['value']
                self._client_key_file = self._vault_client.read('secret/chef_client_key')['data']['value']
            except (AssertionError, Exception) as e:
                logging.debug("Error: %s. Occurred ", e)
                self._ca_cert_file = ''
                self._client_key_file = ''
                pass
        else:
            logging.debug('Vault token not configured')
            self._ca_cert_file = ''
            self._client_key_file = ''
        print("This is the name of the script: ", sys.argv[0])
        print('Number of arguments:', len(sys.argv), 'arguments.')
        print('Argument List:', str(sys.argv))
        print("ca cert file:", repr(self._ca_cert_file))
        print("client key file:", repr(self._client_key_file))
        if len(sys.argv) == 1:
            self._manifest_key_dict = self._k8s_yaml_to_dict_helper(_data_path + manifest_data_file)
            pprint("******* Manifest and Key Dictionary creation *******: ")
            if not self._ca_cert_file and not self._client_key_file:
                # client key and ca cert are not in vault get from filesystem
                self._chef_client_cert_dict = {}
                self._chef_client_cert_dict = self._k8s_yaml_to_dict_helper(_template_path + client_key_file)
                pprint('Client Key Dictionary: ' + pformat(self._chef_client_cert_dict))
                logging.debug('Client Key Dictionary: ' + pformat(self._chef_client_cert_dict))
                self._chef_ca_cert_dict = {}
                self._chef_ca_cert_dict = self._k8s_yaml_to_dict_helper(_template_path + ca_cert_file)
                pprint('CA Cert Dictionary: ' + pformat(self._chef_ca_cert_dict))
                logging.debug('CA Cert Dictionary: ' + pformat(self._chef_ca_cert_dict))
                self._chef_merged_dict = {**self._chef_ca_cert_dict, **self._chef_client_cert_dict}
                pprint('Merged Cert Dictionary: ' + pformat(self._chef_merged_dict))
                logging.debug('Merged Cert Dictionary: ' + pformat(self._chef_merged_dict))
                self._manifest_merged_dict = {**self._manifest_key_dict, **self._chef_merged_dict}
                pprint('Merged Manifest Dictionary: ' + pformat(self._manifest_merged_dict))
                logging.debug('Merged Manifest Dictionary: ' + pformat(self._manifest_merged_dict))
            else:
                # client key and ca cert were retrieved from vault
                _str_ca_cert = repr(self._ca_cert_file)
                _strip_ca_cert = _str_ca_cert.strip("'")
                _str_client_key = repr(self._client_key_file)
                _strip_client_key = _str_client_key.strip("'")
                self._key_list = [_strip_ca_cert, _strip_client_key]
                self._key_name = ["chef_ca_cert", "chef_client_key"]
                self._client_key_cert_dict = dict(zip(self._key_name, self._key_list))
                self._chef_merged_dict = {**self._client_key_cert_dict, **self._manifest_key_dict}
                logging.debug(pformat(self._chef_merged_dict))
                self._manifest_merged_dict = {**self._manifest_key_dict, **self._chef_merged_dict}
                logging.debug('Merged Manifest Dictionary: ' + pformat(self._manifest_merged_dict))
            self._newDataFeed = self._k8s_dict_to_yaml_helper(self._manifest_merged_dict)        
            pprint("******* Key Dictionary creation complete *******: ")
            pprint("******* Manifest creation *******: ")
            self._create_manifest(prebuild_template_file, self._newDataFeed, prebuild_shell_file)
            self._create_manifest(chef_template_file, self._newDataFeed, chef_manifest_file)        
            self._cascade_manifest(chef_manifest_file)
            self._create_manifest(chef_nofips_template_file, self._newDataFeed, chef_nofips_manifest_file)
            self._cascade_manifest(chef_nofips_manifest_file)
            self._create_manifest(manifest_template_file, self._newDataFeed, new_manifest_file)
            self._create_manifest(kops_template_file, self._newDataFeed, kops_shell_file)
            self._create_manifest(state_template_file, self._newDataFeed, state_shell_file)
            self._create_manifest(vers_template_file, self._newDataFeed, vers_shell_file)
            self._create_manifest(ssh_template_file, self._newDataFeed, ssh_shell_file)
            self._create_manifest(upd_template_file, self._newDataFeed, upd_shell_file)
            self._create_manifest(val_template_file, self._newDataFeed, val_shell_file)
            pprint("******* Manifest creation complete *******: ")
            pprint("******* Manifest run*******: ")
            # run the manifests
            self._run_manifest(self, prebuild_shell_file)
            self._run_manifest(self, state_shell_file)
            self._run_manifest(self, vers_shell_file)
            self._run_manifest(self, kops_shell_file)
            self._run_manifest(self, ssh_shell_file)
            self._run_manifest(self, upd_shell_file)
            self._run_manifest(self, val_shell_file)
            pprint("******* Manifest run complete *******: ")
        elif sys.argv[1] == "--delete":
            self._manifest_key_dict = self._k8s_yaml_to_dict_helper(_data_path + manifest_data_file)
            self._newDataFeed = self._k8s_dict_to_yaml_helper(self._manifest_key_dict)
            pprint("******* Delete Manifest creation *******: ")
            self._create_manifest(kops_del_template_file, self._newDataFeed, kops_del_shell_file)
            pprint("******* Manifest creation complete *******: ")
            pprint("******* Manifest run*******: ")
            self._run_manifest(self, kops_del_shell_file)
            print("******* Manifest run complete *******: ")
        pass
    
    @property
    def _newDataFeed(self):
        """
        constructor for new DataFeed object
        :return:
        """
        return self.__newDataFeed
        pass
    
    @_newDataFeed.setter
    def _newDataFeed(self, y):
        """
        setter for new DataFeed object
        :param y:
        :return:
        """
        self.__newDataFeed = y
        pass
    
    @staticmethod
    def _get_vault_client(vault_uri):
        """
        returns a valid vault client
        :param vault_uri:
        :return:
        """
        home = os.getenv("HOME")
       # pdb.set_trace()
        vault_addr = os.getenv('VAULT_ADDR', vault_uri)
        logging.debug('Connecting to Vault at %s with token from %s', vault_uri, f"{home}/.vault-token")
        with open(f"{home}/.vault-token", 'r') as vtoken:
            vault_token = vtoken.read().replace('\n', '')
        try:
            client = hvac.Client(url=vault_addr, token=vault_token)
            return client
        except (urllib3.exceptions.NewConnectionError, urllib3.exceptions.ConnectionError,
                urllib3.exceptions.MaxRetryError, socket.error, socket.gaierror, socket.herror,
                socket.timeout) as e:
            logging.debug("Error: %s. Occurred ", e)
            pass
        pass

    @staticmethod
    def _k8s_dict_to_yaml_helper(key_dict):
        """
        Helper file to create YAML file from dictionary
        :param key_dict:
        :return:
        """
        return yaml.dump(key_dict, default_flow_style=False, allow_unicode=True)
        pass
        
    @staticmethod
    def _k8s_yaml_to_dict_helper(yaml_file_name):
        """
        Create a dictionary from a yaml file
        :param yaml_file_name:
        :return:
        """
        data_dict = {}
        temp_dir_name = '__main__'
        for key, value in yaml.load(open(os.path.join(os.path.dirname(temp_dir_name), yaml_file_name))).items():
            data_dict[key] = str(value).strip("'")
        logging.debug(data_dict)
        return data_dict
        pass

    @staticmethod
    def _create_manifest(template_file, data, shell_file):
        """
        Uses Jinja 2: Load data template and inject into cluster manifest file creating shell file
        :param template_file: 
        :param data: 
        :param shell_file: 
        :return:
        """
        manifest_data = ''
        try:
            manifest_data = yaml.load(data)
        except Exception as e:
            logging.DEBUG("yaml load exception: " + pformat(e))
            pass
        # Load Jinja2 template
        env = Environment(loader=FileSystemLoader(_template_path), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(template_file)
        # Render the template with data and print the output
        new_shell = open(_script_path + shell_file, "w")
        logging.debug(template.render(manifest_data))
        print(template.render(manifest_data), file=new_shell)
        pass

    @staticmethod
    def _run_manifest(self, shell_file):
        """
        Run created shell file at command line
        :param shell_file:
        :return:
        """
        shell_file_path = _script_path + shell_file
        exc_cmd = 'chmod +x ./' + shell_file_path
        ssh_cmd = './' + shell_file_path
        # Run commands in shell
        self._k8s_command_helper_sys(exc_cmd)
        self._k8s_command_helper_sys(ssh_cmd)
        pass

    @staticmethod
    def _cascade_manifest(shell_file):
        """
        Cascade a manifest and use as top level template
        :param shell_file:
        :return:
        """
        shell_file_path = _script_path + shell_file
        str_file_path = _template_path + shell_file
        with open(shell_file_path, "r") as c_file, open(str_file_path, "wt+", encoding='utf8') as str_file:
            chef_data = c_file.read()
            str_file.write(chef_data)
            logging.debug(chef_data)
            c_file.close()
            str_file.close()
        pass

    @staticmethod
    def _create_tmp_manifest():
        """
        create new directory to deploy manifest scripts
        :return:
        """
        if not os.path.isdir(_script_path):
            os.mkdir(_script_path)
            logging.debug("Path: " + _script_path + " is created")
        pass

    @staticmethod
    def _remove_tmp_manifest():
        """
        destroy new directory for manifest scripts
        :return:
        """
        if os.path.isdir(_script_path):
            shutil.rmtree(_script_path)
            logging.debug("Path: " + _script_path + " is deleted")
        pass

    @staticmethod
    def _k8s_command_helper_sys(cmd):

        """
        kubernetes Command Helper - sends shell scripts to Shell
        :param cmd:
        :return:
        """
        try:
            retcode = subprocess.call([cmd], shell=True)
            if retcode < 0:
                print(sys.stderr, "Child was terminated by signal", -retcode)
            else:
                print(sys.stderr, "Child returned", retcode)
        except OSError as e:
            print(sys.stderr, "Execution failed:", e)
        pass

    @staticmethod
    def _start_logger(self):

        """
        start the logger function
        :return:
        """
        self._log_dir = "Manifest/.logs"
        if os.path.isdir(self._log_dir):
            shutil.rmtree(self._log_dir)
        if not os.path.isdir(self._log_dir):
            os.mkdir(self._log_dir)
        logger_file_name = self._log_dir + '/' + datetime.now().strftime('k8s_create_cluster_%H_%M_%d_%m_%Y.log')
        logging.basicConfig(filename=logger_file_name, format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.info("Started Logging for DEBUG in file location: k8s_create_cluster.log")
        self._working_dir = os.path.dirname(self._log_dir)
        logging.info("Logging directory location: " + self._working_dir)
        self._master_package_dir = os.path.abspath(self._working_dir)
        logging.info("Package master directory location: " + self._master_package_dir)
        self._master_log_dir = logging.getLoggerClass().root.handlers[0].baseFilename
        logging.info("Logging for DEBUG in file path: " + self._master_log_dir)
        pass
