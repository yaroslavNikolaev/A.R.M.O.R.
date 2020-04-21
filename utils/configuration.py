import sys, logging, yaml
from argparse import ArgumentParser

K8_CONFIG_DEFAULT_LOCATION = "./armor-io/templates/config"

config = "config"
version = 'version'
name = 'name'
port = 'port'
k8config = 'k8config'
gh = 'gh_auth'
mode = 'mode'
COMMON = [version, name, port, k8config, mode]

azure = "azure"
aks = 'aks'
az_resourceGroup = 'az_resourceGroup'
az_subscription = 'az_subscription'
secret = 'secret'
tenant = 'tenant'
client = 'client'
AZURE = [aks, az_resourceGroup, az_subscription, secret, client, tenant]

gcp = "gcp"
gcp_project = 'gcp_project'
gcp_zone = 'gcp_zone'
gcp_token = 'gcp_token'
GCP = [gcp_token, gcp_zone, gcp_project]

aws = "aws"
AWS = []

internal = "internal"
external = "external"


class Configuration(object):
    __config = dict()
    __dict_args: dict

    def __init__(self):
        args = self.__get_argument_parser()
        # read arguments from the command line and show help if requested[main purpose]!
        args = args.parse_args()
        with open('./armor-io/values.yaml', "r") as yml:
            self.__config.update(yaml.load(yml, Loader=yaml.FullLoader))
        with open('./armor-io/Chart.yaml', "r") as yml:
            self.__config.update(yaml.load(yml, Loader=yaml.FullLoader))
        if args.version:
            print("A.R.M.O.R. version is " + self.__config[version])
            sys.exit()
        self.__dict_args = vars(args)

    def load_application_configuration(self):
        with open(self.__dict_args[config], "r") as yml:
            self.__config.update(yaml.load(yml, Loader=yaml.FullLoader))
        for arg in self.__dict_args:
            if self.__dict_args[arg] is not None and arg != config and arg != version:
                group = self.__get_group_by_arg(arg)
                if group is None:
                    self.__config[arg] = str(self.__dict_args[arg])
                else:
                    if group not in self.__config:
                        self.__config[group] = dict()
                    self.__config[group][arg] = str(self.__dict_args[arg])

    def __get_group_by_arg(self, arg: str):
        if arg in AZURE:
            return azure
        elif arg in GCP:
            return gcp
        elif arg in AWS:
            return aws
        else:
            return None

    def __get_argument_parser(self) -> ArgumentParser:
        parser = ArgumentParser(description="A.R.M.O.R. application protects you to be late in cloud")
        parser.add_argument(config, nargs='?', type=str, default="./application.yaml",
                            help="Configuration file with all necessary values , by default application.yaml is taken")
        # common
        parser.add_argument("-V", "--" + version, help="show A.R.M.O.R. version", action="store_true")
        parser.add_argument("--" + name, help="Installation name", type=str)
        parser.add_argument("--" + port, help="A.R.M.O.R. port to use", type=int)
        parser.add_argument("--" + k8config, help="K8 config file location", type=str)
        parser.add_argument("--" + gh, help="GH basic auth token base64(username:token)", type=str)
        parser.add_argument("--" + mode, type=str, choices=[internal, external],
                            help="Armor mode. Internal means use SA to login , External means use config")

        # azure
        azure_group = parser.add_argument_group(azure)
        azure_group.add_argument("--" + aks, help="Azure Kubernetes service name", type=str)
        azure_group.add_argument("--" + az_resourceGroup, help="Azure Resource group name", type=str)
        azure_group.add_argument("--" + az_subscription, help="Azure Subscription name", type=str)
        azure_group.add_argument("--" + tenant, help="Azure AD tenant", type=str)
        azure_group.add_argument("--" + client, help="Azure Application client id", type=str)
        azure_group.add_argument("--" + secret, help="Azure Application secret", type=str)
        # gcp
        gcp_group = parser.add_argument_group(gcp)
        gcp_group.add_argument("--" + gcp_project, help="Gcp project", type=str)
        gcp_group.add_argument("--" + gcp_zone, help="Gcp zone", type=str)
        gcp_group.add_argument("--" + gcp_token, help="Gcp token [gcloud auth print-access-token]", type=str)
        # aws
        aws_group = parser.add_argument_group(aws)
        return parser

    def name(self) -> str:
        return self.__config[name]

    def config(self) -> str:
        return self.__config.get(k8config, K8_CONFIG_DEFAULT_LOCATION)

    def port(self) -> int:
        return int(self.__config[port])

    def internal(self) -> bool:
        return self.__config[mode] == internal

    def aks(self) -> str:
        return self.__config[azure].get(aks)

    def az_resource_group(self) -> str:
        return self.__config[azure].get(az_resourceGroup)

    def az_subscription(self) -> str:
        return self.__config[azure].get(az_subscription)

    def az_tenant(self) -> str:
        return self.__config[azure].get(tenant)

    def az_client(self) -> str:
        return self.__config[azure].get(client)

    def az_secret(self) -> str:
        return self.__config[azure].get(secret)

    def gcp_project(self) -> str:
        return self.__config[gcp].get(gcp_project)

    def gcp_zone(self) -> str:
        return self.__config[gcp].get(gcp_zone)

    def gcp_token(self) -> str:
        return self.__config[gcp].get(gcp_token)

    def gh_auth(self) -> str:
        return self.__config.get(gh)

    def cloud(self) -> str:
        if aws in self.__config:
            logging.warning("AWS is not supported yet , Mock will be used to cover this area")
            return aws
        elif gcp in self.__config:
            return gcp
        elif azure in self.__config:
            return azure
        else:
            return "default"
