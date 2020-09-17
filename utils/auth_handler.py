import copy
import os
import requests
import uuid
import jwt
import json

from utils import logger

AppKeyEnvVar = 'TT_REST_API_APPKEY'

def get_domain(environment):
    if environment.startswith('int'):
        return 'debesys.net'
    return 'trade.tt'

class RestAPIAuthenticator:
    __endpoint = 'https://apigateway.{domain}/ttid/{env}/token'
    __headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-api-key': ''
    }
    __body = {
        'grant_type': 'user_app',
        'app_key': ''
    }

    def __init__(self, environment, app_key):
        self.environment = environment
        self.domain = get_domain(environment)
        self.user_id = 0
        self.company_id = 0

        if app_key is None:
            logger.log_verbose('Querying environment variable "{0}" for the AppKey'.format(AppKeyEnvVar))
            app_key = os.environ.get(AppKeyEnvVar)

        try:
            self.client, secret = app_key.split(':', 2)
            uuid.UUID(str(self.client))
            uuid.UUID(str(secret))
        except Exception:
            raise Exception('Invalid app_key')

        self.__endpoint = self.__endpoint.format(domain=self.domain, env=self.environment)
        self.__headers['x-api-key'] = self.client
        self.__body['app_key'] = app_key

        resp = requests.post(url = self.__endpoint, headers = self.__headers, data = self.__body)
        j_resp = resp.json()

        if 'status' in j_resp and j_resp['status'] == 'Ok':
            logger.log('Authentication succeeded...')
            self.access_token = j_resp['access_token']
            self.token_type = j_resp['token_type']
            self.expiry = j_resp['seconds_until_expiry']

            decoded = jwt.decode(self.access_token, verify=False)
            self.user_id = decoded['id']
            self.company_id = decoded['company_id']
            logger.log_verbose('Received token for'
                               ' user_id={0}'
                               ' company_id={1}'.format(
                               self.user_id,
                               self.company_id))
        else:
            error_message = None
            if 'message' in j_resp:
                error_message = j_resp['message']
            elif 'status_message' in j_resp:
                error_message = j_resp['status_message']
            else:
                error_message = json.dumps(j_resp)

            raise Exception('Token request failed.  msg={0}'.format(error_message))
