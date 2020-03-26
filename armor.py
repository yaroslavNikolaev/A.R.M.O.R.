from argparse import ArgumentParser
import os
from configparser import ConfigParser
from Initializer import Initializer

if __name__ == '__main__':

    parser = ArgumentParser(description="A.R.M.O.R. application protect you to be late in cloud",
                                     fromfile_prefix_chars='@')
    parser.add_argument('config', nargs='?', default=os.getcwd(), help="Configuration file with all necessary value")
    parser.add_argument("-V", "--version", help="show program version", action="store_true")
    # common
    common = parser.add_argument_group("common")
    common.add_argument("--name", default="default", help="Installation name", type=str)
    common.add_argument("--port", default=8000, help="A.R.M.O.R. port to use", type=int)
    common.add_argument("--kubernetes", help="Http endpoint of kube", type=str)
    # https://kubernetes.io/docs/reference/access-authn-authz/rbac/#service-account-permissions
    common.add_argument("--kubernetes_token", type=str,
                        help="Kubernetes access token with rights to see nodes (*admin role can do it)"
                             "https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/")

    # azure
    azure = parser.add_argument_group("azure")
    azure.add_argument("--aks", help="Azure Kubernetes service name", )
    azure.add_argument("--az_resourceGroup", help="Azure Resource group name", type=str)
    azure.add_argument("--az_subscription", help="Azure Subscription name", type=str)
    azure.add_argument("--az_token", help="Azure access token [az account get-access-token]", type=str)
    # gcp
    gcp = parser.add_argument_group("gcp")
    gcp.add_argument("--gcp_project", help="Gcp project", type=str)
    gcp.add_argument("--gcp_zone", help="Gcp zone", type=str)
    gcp.add_argument("--gcp_token", help="Gcp token [gcloud auth print-access-token]", type=str)
    # aws
    aws = parser.add_argument_group("aws")

    # read arguments from the command line
    args = parser.parse_args()
    # check for --version or -V
    if args.version:
        print("A.R.M.O.R. version is 0.0.2")
    config = ConfigParser()
    config.read('./config.ini')
    Initializer().init(config)
