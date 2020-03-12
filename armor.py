import argparse
from Initializer import Initializer

if __name__ == '__main__':
    # initiate the parser (todo think about kind of auto-discovery)
    parser = argparse.ArgumentParser(description="calculate X to the power of Y")
    parser.add_argument("-V", "--version", help="show program version", action="store_true")
    parser.add_argument("-v", "--verbosity", help="increase output verbosity", type=int, choices=[1, 2, 3, 4, 5, 6])
    parser.add_argument("-k8", "--kubernetes", help="Http endpoint of kube", type=str)
    parser.add_argument("-k8t", "--kubernetes_token",
                        help="Kubernetes access token. "
                             "https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/",
                        type=str)

    # read arguments from the command line
    args = parser.parse_args()
    Initializer().init(args)
