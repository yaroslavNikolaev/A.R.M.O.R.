import argparse
from Initializer import Initializer

if __name__ == '__main__':
    # initiate the parser (todo think about kind of auto-discovery)
    parser = argparse.ArgumentParser(description="calculate X to the power of Y")
    parser.add_argument("-V", "--version", help="show program version", action="store_true")
    parser.add_argument("-v", "--verbosity", help="increase output verbosity", type=int, choices=[1, 2, 3, 4, 5, 6])
    parser.add_argument("-p", "--port", default=8000, help="A.R.M.O.R. port to use", type=int)
    parser.add_argument("-e", "--environment", help="Name of environment where application is deployed", type=str,
                        choices={"aws", "azure", "gcp", "metal"}, required=True)
    parser.add_argument("-k8", "--kubernetes", help="Http endpoint of kube", type=str)
    parser.add_argument("-k8t", "--kubernetes_token",
                        help="Kubernetes access token with rights to see nodes (*admin role can do it)"
                             "https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/",
                        type=str)


    # azure
    azure = parser.add_argument_group("azure")
    azure.add_argument("-aks", "--aks", help="Azure Kubernetes service name", )
    azure.add_argument("-arg", "--azureResourceGroup", help="Azure Resource group name", type=str)
    azure.add_argument("-as", "--azureSubscription",  help="Azure Subscription name", type=str)
    azure.add_argument("-at", "--azuretoken", help="Azure access token", type=str)
    # gcp
    # aws

    # read arguments from the command line
    args = parser.parse_args()
    Initializer().init(args)
