import time
import requests
import uuid
import inspect
import os
import re
try:
    import simplejson as json
except ImportError:
    import json

from utils import logger

ThrottleRate = 2.2      # What each request/response will take, in seconds
g_throttle = False      # Whether throttling is enabled

def throttle_requests(val):
    global g_throttle
    g_throttle = val
    logger.log_verbose('Request throttling {0}'.format('enabled' if g_throttle == True else 'disabled'))

def set_throttle_rate(val):
    global ThrottleRate
    ThrottleRate = val
    logger.log_verbose('Setting request throttle rate to () seconds'.format(ThrottleRate))

class RequestReceiver:
    __throttle_log_format = 'REST call duration below throttle, sleeping {0} seconds'
    __request_id_key = 'requestId'
    __request_id_format = '{app_name}-{company}--{guid}'

    def __init__(self):
        self.__time0 = None
        self.__time1 = None

    def __throttle(self):
        global g_throttle
        if g_throttle == True:
            time_to_sleep = ThrottleRate - (self.__time1 - self.__time0)
            if time_to_sleep > 0.0:
                time.sleep(time_to_sleep)
                logger.log_verbose(self.__throttle_log_format.format(time_to_sleep))

    def __preprocess(self, **kwargs):
        self.__time0 = time.time()

        frm = inspect.stack()[2]
        mod = inspect.getmodule(frm[0])
        app_name = os.path.splitext(os.path.basename(mod.__file__))[0]

        kwargs['params'][self.__request_id_key] = self.__request_id_format.format(app_name=app_name, company='tt', guid=uuid.uuid1())
        logger.log_verbose('Request ID: {0}'.format(kwargs['params'][self.__request_id_key]))

    def __postprocess(self, response):
        logger.log_verbose('Response Code: {0}'.format(response.status_code))
        logger.log_verbose('Response Encoding: {0}'.format(response.encoding))
        logger.log_verbose('Response Apparent: {0}'.format(response.apparent_encoding))

        content = {}
        try:
            #text = re.sub(r'("[\s\w]*)"([\s\w]*")',r"\1\2", unicode(response.text).strip())
            text = re.sub(r'("TM C)"([\s\w]*")',r"\1\2", unicode(response.text))
            if 'algoName' in text:
                text = text.replace('},    ]', '}    ]')
            content = json.loads(text, strict=False)
            if response.status_code == 429 and 'message' in content:
                content['status'] = 'StatusFailed'
                content['status_message'] = content['message']
                del content['message']
        except Exception as err:
            logger.log('Exception raised parsing response: msg={0} raw={1}'.format(str(err), text))
            content['status'] = 'StatusFailed'
            content['status_message'] = str(err)
        else:
            logger.log_verbose('Response: {0}'.format(content))
        finally:
            self.__time1 = time.time()
            self.__throttle()

        return content

    def get(self, *args, **kwargs):
        if not 'params' in kwargs.keys():
            kwargs['params'] = {}

        self.__preprocess(**kwargs)
        return self.__postprocess(requests.get(*args, **kwargs))

    def post(self, *args, **kwargs):
        if not 'params' in kwargs.keys():
            kwargs['params'] = {}

        self.__preprocess(**kwargs)
        return self.__postprocess(requests.post(*args, **kwargs))

    def delete(self, *args, **kwargs):
        if not 'params' in kwargs.keys():
            kwargs['params'] = {}

        self.__preprocess(**kwargs)
        return self.__postprocess(requests.delete(*args, **kwargs))
