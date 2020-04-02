import sys
import logging
import os
from configparser import ConfigParser
from argparse import ArgumentParser

KUBE_CONFIG_DEFAULT_LOCATION = os.environ.get('KUBECONFIG', '~/.kube/config')

config = "config"

common = 'common'
version = 'version'
name = 'name'
port = 'port'
k8config = 'k8config'
gh = 'gh_auth'
COMMON = [version, name, port, k8config]

azure = "azure"
aks = 'aks'
az_resourceGroup = 'az_resourceGroup'
az_subscription = 'az_subscription'
az_token = 'az_token'
AZURE = [aks, az_resourceGroup, az_subscription, az_token]

gcp = "gcp"
gcp_project = 'gcp_project'
gcp_zone = 'gcp_zone'
gcp_token = 'gcp_token'
GCP = [gcp_token, gcp_zone, gcp_project]

aws = "aws"
AWS = []


class Configuration(object):
    __config: ConfigParser

    def __init__(self):
        args = self.__get_argument_parser()
        # read arguments from the command line and show help if requested[main purpose]!
        args = args.parse_args()
        configuration = ConfigParser()
        configuration.read('./config.ini')
        if args.version:
            print("A.R.M.O.R. version is " + configuration[common][version])
            sys.exit()
        dict_args = vars(args)
        configuration.read(dict_args[config])
        for arg in dict_args:
            if dict_args[arg] is not None and arg != config and arg != version:
                configuration[self.__get_group_by_arg(arg)][arg] = str(dict_args[arg])
        self.__config = configuration

    def __get_group_by_arg(self, arg: str) -> str:
        if arg in COMMON:
            return common
        elif arg in AZURE:
            return azure
        elif arg in GCP:
            return gcp
        elif arg in AWS:
            return aws
        else:
            raise ValueError(f'{arg} is not defined in any group')

    def __get_argument_parser(self) -> ArgumentParser:
        parser = ArgumentParser(description="A.R.M.O.R. application protects you to be late in cloud")
        parser.add_argument(config, nargs='?', type=str, default="./application.ini",
                            help="Configuration file with all necessary values , by default application.ini is taken")
        # common
        common_group = parser.add_argument_group(common)
        common_group.add_argument("-V", "--" + version, help="show A.R.M.O.R. version", action="store_true")
        common_group.add_argument("--" + name, default="armor", help="Installation name", type=str)
        common_group.add_argument("--" + port, help="A.R.M.O.R. port to use", type=int)
        common_group.add_argument("--" + k8config, help="K8 config file location", type=str)
        common_group.add_argument("--" + gh, help="GH basic auth token base64(username:token)", type=str)

        # azure
        azure_group = parser.add_argument_group(azure)
        azure_group.add_argument("--" + aks, help="Azure Kubernetes service name", type=str)
        azure_group.add_argument("--" + az_resourceGroup, help="Azure Resource group name", type=str)
        azure_group.add_argument("--" + az_subscription, help="Azure Subscription name", type=str)
        azure_group.add_argument("--" + az_token, help="Azure access token [az account get-access-token]", type=str)
        # gcp
        gcp_group = parser.add_argument_group(gcp)
        gcp_group.add_argument("--" + gcp_project, help="Gcp project", type=str)
        gcp_group.add_argument("--" + gcp_zone, help="Gcp zone", type=str)
        gcp_group.add_argument("--" + gcp_token, help="Gcp token [gcloud auth print-access-token]", type=str)
        # aws
        aws_group = parser.add_argument_group(aws)
        return parser

    def name(self) -> str:
        return self.__config.get(common, name)

    def version(self) -> str:
        return self.__config.get(common, version)

    def port(self) -> int:
        return self.__config.getint(common, port)

    def kubernetes_config(self) -> str:
        return self.__config.get(common, k8config, fallback=KUBE_CONFIG_DEFAULT_LOCATION)

    def aks(self) -> str:
        return self.__config.get(azure, aks)

    def az_resourceGroup(self) -> str:
        return self.__config.get(azure, az_resourceGroup)

    def az_subscription(self) -> str:
        return self.__config.get(azure, az_subscription)

    def az_token(self) -> str:
        return self.__config.get(azure, az_token)

    def gcp_project(self) -> str:
        return self.__config.get(gcp, gcp_project)

    def gcp_zone(self) -> str:
        return self.__config.get(gcp, gcp_zone)

    def gcp_token(self) -> str:
        return self.__config.get(gcp, gcp_token)

    def gh_auth(self) -> str:
        return self.__config.get(common, gh)

    def kubernetes_application(self) -> str:
        if self.__config.has_section(aws):
            logging.warning("AWS is not supported yet , Mock will be used to cover this area")
            return "aws.kubernetes.eks"
        elif self.__config.has_section(gcp):
            return "gcp.kubernetes.gke"
        elif self.__config.has_section(azure):
            return "azure.kubernetes.aks"
        else:
            return "party3rd.cloud_native.kubernetes"
