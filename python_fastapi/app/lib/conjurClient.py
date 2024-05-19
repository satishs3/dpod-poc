import os
from app.logger import logger
from conjur import Client
from kubernetesClient import KubernetesClient

# Conjur variables
CONJUR_ACCOUNT = 'prod'

CONJUR_SAFE_PARAMS = {
    'production':  {'safe': 'D-CJR-SUM-ENG-S-DAAS',
                    'login_id': 'host/prodvault/devops/D-CJR-SUM-ENG-S-DAAS/apps/host1',
                    'api_key_secret': 'conjur-api-key'},
}

CONJUR_CONNECT_PARAMS = {
    'CORP': {'url': 'https://follower-west.corp.netapp.com',
             'pem_secret_name': 'conjur-corp-pem',
             'pem_file': '/dpod/conjur-corp.pem'},
    'ENG': {'url': 'https://svc-pam.cls.eng.netapp.com',
            'pem_secret_name': 'conjur-eng-pem',
            'pem_file': '/dpod/conjur-eng.pem'},
}

class ConjurClient:
    ''' Conjur API methods to fetch secrets from Conjur safe '''
    def __init__(self):
        self.environment = "production"
        self.kube_api = KubernetesClient()

    def get_conjur_api_key(self):
        '''
        Fetch Conjur api-key from Kubernetes secret
        '''
        kube_secret_name = CONJUR_SAFE_PARAMS[self.environment]['api_key_secret']
        conjur_cred = self.kube_api.get_namespaced_secret(secret_name=kube_secret_name)
        return conjur_cred['password']

    def get_conjur_pem_file(self, environment):
        '''
        Fetch Conjur pem file from Kubernetes secret
        '''
        pem_file = CONJUR_CONNECT_PARAMS[environment]['pem_file']
        if os.path.exists(pem_file):
            # Pem file already exists, so nothing to do
            logger.debug("Pem file %s already exists" % pem_file)
        else:
            # Pem file doesn't exist, so create it
            kube_secret_name = CONJUR_CONNECT_PARAMS[environment]['pem_secret_name']
            logger.debug("Pem file %s not found => Fetching kube secret '%s'" % (pem_file, kube_secret_name))
            kube_secret = self.kube_api.get_namespaced_secret(secret_name=kube_secret_name)

            # Write the secret's password to the pem file
            with open(pem_file, 'w') as pem_fp:
                logger.debug("Writing secret's password to pem file %s" % pem_file)
                pem_fp.write(kube_secret['password'])
        return pem_file
    
    def get_secret(self):
        '''
        Get secret from conjur safe
        '''
        logger.info("Get secret from conjur safe'%s'")
        safe = CONJUR_SAFE_PARAMS[self.environment]['safe']
        login_id = CONJUR_SAFE_PARAMS[self.environment]['login_id']
        conjur_api_key = self.get_conjur_api_key()

        secret_value = None
        # We don't know whether we're in 'CORP' or 'ENG' network, so we'll loop through each and
        # try connecting and fetching the secret until successful
        for environment in ["ENG", "CORP"]:
            conjur_url = CONJUR_CONNECT_PARAMS[environment]['url']
            conjur_pem_file = self.get_conjur_pem_file(environment)

            try:
                logger.debug("Try fetching secret from network '%s' for cluster '%s'"
                                 % (environment, cluster))
                client = Client(account=CONJUR_ACCOUNT,
                                api_key=conjur_api_key,
                                ca_bundle=conjur_pem_file,
                                debug=False,
                                http_debug=False,
                                login_id=login_id,

                                password=None,
                                ssl_verify=False,
                                url=conjur_url)

                # Get the <variable_id> used to fetch the secret value
                #   prodvault/devops/<safe>/Operating System-SSHKeyVaulting-kubeconfig-<cluster>/password
                variable_id = "prodvault/devops/%s/Operating System-SSHKeyVaulting-kubeconfig-%s/password" % (safe, cluster)

                # Fetch secret value for <variable_id>
                secret_value = client.get(variable_id)

                # Decode the secret from binary format to string format
                secret_value = secret_value.decode('utf-8')

                logger.debug("Fetching conjur secret from network '%s' succeeded" % environment)
                break

            except Exception as e:
                # Continue and try the next network
                logger.debug("Fetching conjur secret from network '%s' for cluster '%s' failed"
                                 % (environment, cluster))
                continue

        return secret_value
    
if __name__ == "__main__":
    conjur_client = ConjurClient()
    secret = conjur_client.get_secret()
    print(secret)