import logging
import json
import re
from utils.configuration import Configuration
from kubernetes import config, client

armor_template = "armor.io/{}"


def add_annotation_to_resource(resource, annotations: dict):
    annos = {}
    anno_exist = resource.metadata.annotations is None
    for annotation in annotations.keys():
        key = armor_template.format(annotation)
        exist = anno_exist or key in i.metadata.annotations.keys()
        if exist:
            continue
        annos[key] = annotations[annotation]
    if len(annos) == 0:
        return
    patch = {'metadata': {'annotations': annos}}
    logging.warning(f'Patch {patch}')
    client.AppsV1Api().patch_namespaced_deployment(resource.metadata.name, resource.metadata.namespace, patch)


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
        ret = client.AppsV1Api().list_deployment_for_all_namespaces(watch=False)
        for i in ret.items:
            dp_name = i.metadata.name
            for mutation in mutations['by_regexp']:
                if not ("annotations" in mutation and len(mutation["annotations"]) > 0):
                    continue
                if re.search(mutation['regexp'], dp_name):
                    add_annotation_to_resource(i, mutation["annotations"])
