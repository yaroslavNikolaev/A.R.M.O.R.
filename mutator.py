import logging
import json
import re
from utils.configuration import Configuration
from kubernetes import config, client

armor_template = "armor.io/{}"


def add_annotation(pod, annotations: dict):
    annos = {}
    anno_exist = pod.metadata.annotations is None
    for annotation in annotations.keys():
        exist = anno_exist or annotation in i.metadata.annotations.keys()
        if exist:
            continue
        annos[armor_template.format(annotation)] = annotations[annotation]
    if len(annos) == 0:
        return
    patch = {'metadata': {'annotations': annos}}
    logging.warning(f'Patch {patch}')
    client.CoreV1Api().patch_namespaced_pod(pod.metadata.name, pod.metadata.namespace, patch)


if __name__ == '__main__':
    '''
    Mutator application. This application will add armor annotations according to mapping.json file.
    Such approach allow easily test armor on test env before actual usage for live. 
    '''
    logging.info("A.R.M.O.R mutator is going to setup configuration")
    configuration = Configuration()
    config.load_kube_config(configuration.kubernetes_config())
    with open('mapping.json') as json_file:
        mutations = json.load(json_file)
        ret = client.CoreV1Api().list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            pod_name = i.metadata.name
            for mutation in mutations['by_regexp']:
                if not ("annotations" in mutation and len(mutation["annotations"]) > 0):
                    continue
                if re.search(mutation['regexp'], pod_name):
                    add_annotation(i, mutation["annotations"])
