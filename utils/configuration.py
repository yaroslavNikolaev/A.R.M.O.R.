import sys
import logging
from configparser import ConfigParser
from argparse import ArgumentParser

common = 'common'
version = 'version'
name = 'name'
port = 'port'
kubernetes = 'kubernetes'
kubernetes_token = 'kubernetes_token'

azure = "azure"
aks = 'aks'
az_resourceGroup = 'az_resourceGroup'
az_subscription = 'az_subscription'
az_token = 'az_token'

gcp = "gcp"
gcp_project = 'gcp_project'
gcp_zone = 'gcp_zone'
gcp_token = 'gcp_token'

aws = "aws"


class Configuration(object):
    __config: ConfigParser

    def __init__(self):
        args = self.__get_argument_parser()
        # read arguments from the command line and show help if requested[main purpose]!
        args = args.parse_args()
        config = ConfigParser()
        config.read('./config.ini')
        if args.version:
            print("A.R.M.O.R. version is " + config[common][version])
            sys.exit()
        config.read(args.config)
        self.__config = config

    def __get_argument_parser(self) -> ArgumentParser:
        parser = ArgumentParser(description="A.R.M.O.R. application protects you to be late in cloud")
        parser.add_argument('config', nargs='?', type=str, default="./application.ini",
                            help="Configuration file with all necessary value , by default config.ini is taken")
        # common
        common_group = parser.add_argument_group(common)
        common_group.add_argument("-V", "--" + version, help="show A.R.M.O.R. version", action="store_true")
        common_group.add_argument("--" + name, default="armor", help="Installation name", type=str)
        common_group.add_argument("--" + port, default=8000, help="A.R.M.O.R. port to use", type=int)
        common_group.add_argument("--" + kubernetes, help="Http endpoint of kube", type=str)
        # https://kubernetes.io/docs/reference/access-authn-authz/rbac/#service-account-permissions
        common_group.add_argument("--" + kubernetes_token, type=str,
                                  help="Kubernetes access token with rights to see nodes (*admin role can do it)"
                                       "https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/")

        # azure
        azure_group = parser.add_argument_group(azure)
        azure_group.add_argument("--" + aks, help="Azure Kubernetes service name", )
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

    def kubernetes(self) -> str:
        return self.__config.get(common, kubernetes)

    def kubernetes_token(self) -> str:
        return self.__config.get(common, kubernetes_token)

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
