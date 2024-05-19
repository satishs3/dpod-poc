import os
from app.logger import logger
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class KubernetesClient:
    def __init__(self):
        try:
          config.load_kube_config()
        except:
          # load_kube_config throws 
          config.load_incluster_config()

        self.kube_api = client.CoreV1Api()

    def get_namespaced_secret(self, secret_name):
        try:
            namespace=os.getenv("POD_NAMESPACE")
            if namespace is None:
                namespace = "default"
            logger.debug("Fetching secret '%s' from namespace '%s'" % (secret_name, os.getenv("POD_NAMESPACE")))
            secret = self.kube_api.read_namespaced_secret(name=secret_name, namespace=namespace)
            return secret.data
        except ApiException as e:
            logger.exception("Exception when calling CoreV1Api->read_namespaced_secret: %s\n" % e)
            return None
    
if __name__ == "__main__":
    kube_client = KubernetesClient()
    secret = kube_client.get_namespaced_secret("my-secret")
    print(secret)



    