import os
import base64
from conjur import Client
from app.logger import logger
from kubernetesClient import KubernetesClient

# Conjur variables
CONJUR_ACCOUNT = 'prod'

CONJUR_SAFE_PARAMS = {
    'production':  {'safe': 'S-CJR-DPO-O-DPO',
                    'login_id': 'host/prodvault/devops/S-CJR-DPO-O-DPO/DPO-host1',
                    'api_key_secret': 'conjur-api-key'},
}

CONJUR_CONNECT_PARAMS = {
    'CORP': {'url': 'https://svc-pam.cls.eng.netapp.com',
             'pem_secret_name': 'conjur-corp-pem',
             'pem_file': '/dpod/conjur.pem'},
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
        logger.debug("Get secret from conjur safe")
        safe = CONJUR_SAFE_PARAMS[self.environment]['safe']
        login_id = CONJUR_SAFE_PARAMS[self.environment]['login_id']
        conjur_api_key = base64.b64decode(self.get_conjur_api_key())
        secret_value = None
        for environment in ["CORP"]:
            conjur_url = CONJUR_CONNECT_PARAMS[environment]['url']
            conjur_pem_file = self.get_conjur_pem_file(environment)
            try:
                client = Client(account=CONJUR_ACCOUNT,
                                api_key=conjur_api_key,
                                ca_bundle=conjur_pem_file,
                                debug=True,
                                http_debug=False,
                                login_id=login_id,
                                password=None,
                                ssl_verify=False,
                                url=conjur_url)

                # Get the <variable_id> used to fetch the secret value
                #   prodvault/devops/<safe>/Operating System-SSHKeyVaulting-kubeconfig-<cluster>/password
                variable_id = "prodvault/devops/S-CJR-DPO-O-DPO/Misc-GenericPasswordVault-TestConjur-TestConjur/password"

                # Fetch secret value for <variable_id>
                secret_value = client.get(variable_id)

                # Decode the secret from binary format to string format
                secret_value = secret_value.decode('utf-8')

                logger.debug("Fetching conjur secret from network '%s' succeeded" % environment)
                break

            except Exception as e:
                # Continue and try the next network
                logger.exception("Fetching conjur secret from network failed ->" + str(e))
                continue

        return secret_value

if __name__ == "__main__":
    conjur_client = ConjurClient()
    secret = conjur_client.get_secret()
    logger.debug(secret)