import json
import logger
import request_receiver

class User_GET:
    __endpoint = 'https://apigateway.{domain}/risk/{env}/user'
    __headers = {
        'accept': 'application/json',
        'Authorization': '',
        'x-api-key': ''
    }

    def __init__(self, auth):
        self.__endpoint = self.__endpoint.format(domain=auth.domain, env=auth.environment) + '/{user_id}'
        self.__headers['Authorization'] = 'Bearer {0}'.format(auth.access_token)
        self.__headers['x-api-key'] = auth.client

    def get(self, user_id):
        logger.log_verbose('Downloading user data for id [{0}]'.format(user_id))

        req = request_receiver.RequestReceiver()
        j_resp = req.get(url=self.__endpoint.format(user_id=user_id),
                         headers=self.__headers)

        # {
            # "status": "Ok",
            # "user": [
                # {
                    # "id": 1936,
                    # ...
                # }
            # ]
        # }

        if j_resp['status'] == 'Ok':
            return j_resp['user'][0]
        else:
            raise Exception('User download request failed.'
                            'user_id={0} msg={1}'.format(user_id, j_resp['status_message']))
