import argparse
import unicodecsv as csv
import json
import sys
import math

from utils import user_download
from utils import versions
from utils import auth_handler
from utils import logger
from utils import request_receiver

class GLOBALS(object):
    enums = []
    order_tag_defaults = []
    order_tag_default_fields = []
    users = []

common = GLOBALS()

def download_users(auth):
    logger.log('Downloading users list')

    users = []
    endpoint = 'https://apigateway.{domain}/risk/{env}/users'.format(domain=auth.domain, env=auth.environment)
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer {0}'.format(auth.access_token),
        'x-api-key': auth.client
    }

    next_page_key = None
    while True:
        req = request_receiver.RequestReceiver()
        j_resp = req.get(url=endpoint,
                         headers=headers,
                         params={'nextPageKey': next_page_key})

        # {
        #     "status": "Ok",
        #     "users": [
        #         {
        #             "id": 25,
        #             "email": "first.last@tradingtechnologies.com",
        #             "firstname": "First",
        #             "lastname": "Last",
        #             "alias": "FLast"
        #         }
        #     ]
        #     "lastPage": "true",
        #     "nextPageKey": "...",
        # }

        if j_resp['status'] == 'Ok':
            users += j_resp['users']
            logger.log_verbose('Users downloaded:'
                               ' num_downloaded={0}'
                               ' total_downloaded={1}'
                               ' last_page={2}'.format(
                len(j_resp['users']),
                len(users),
                j_resp['lastPage']))

            if j_resp['lastPage'] == 'false':
                next_page_key = j_resp['nextPageKey']
            else:
                break
        else:
            raise Exception('Users download failed.  msg={0}'.format(j_resp['status_message']))

    return users


def download_order_tag_defaults(auth):
    logger.log('Downloading order tag default list (this may take a while)')

    order_tag_defaults = []
    endpoint = 'https://apigateway.{domain}/risk/{env}/ordertagdefaults/'.format(domain=auth.domain,
                                                                                       env=auth.environment)
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer {0}'.format(auth.access_token),
        'x-api-key': auth.client
    }

    next_page_key = None
    while True:
        req = request_receiver.RequestReceiver()
        j_resp = req.get(url=endpoint,
                         headers=headers,
                         params={'nextPageKey': next_page_key})

        # {
        #     "status": "string",
        #     "fields": [
        #         {
        #             "fieldId": 0,
        #             "isRequired": 0,
        #             "marketId": 0,
        #             "name": "string",
        #             "valueTypeId": 0,
        #             "category": 0,
        #             "enums": [
        #                 {
        #                     "valueEnumId": 0,
        #                     "valueEnumName": "string"
        #                 }
        #             ]
        #         }
        #     ]
        # }

        if j_resp['status'] == 'Ok':
            order_tag_defaults += j_resp['orderTagDefaults']
            logger.log_verbose('Fields downloaded:'
                               ' num_downloaded={0}'
                               ' total_downloaded={1}'
                               ' last_page={2}'.format(
                               len(j_resp['orderTagDefaults']),
                               len(order_tag_defaults),
                               j_resp['lastPage']))

            if j_resp['lastPage'] == 'false':
                next_page_key = j_resp['nextPageKey']
            else:
                break
        else:
            raise Exception('Order tag defaults download failed.  msg={0}'.format(j_resp['status_message']))

    return order_tag_defaults


def download_order_tag_default_fields(auth):
    logger.log('Downloading order tag default field list')

    fields = []
    endpoint = 'https://apigateway.{domain}/risk/{env}/ordertagdefaults/fields'.format(domain=auth.domain,
                                                                                       env=auth.environment)
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer {0}'.format(auth.access_token),
        'x-api-key': auth.client
    }

    next_page_key = None
    while True:
        req = request_receiver.RequestReceiver()
        j_resp = req.get(url=endpoint,
                         headers=headers,
                         params={'nextPageKey': next_page_key})

        # {
        #     "status": "string",
        #     "fields": [
        #         {
        #             "fieldId": 0,
        #             "isRequired": 0,
        #             "marketId": 0,
        #             "name": "string",
        #             "valueTypeId": 0,
        #             "category": 0,
        #             "enums": [
        #                 {
        #                     "valueEnumId": 0,
        #                     "valueEnumName": "string"
        #                 }
        #             ]
        #         }
        #     ]
        # }

        if j_resp['status'] == 'Ok':
            fields += j_resp['fields']
            logger.log_verbose('Fields downloaded:'
                               ' num_downloaded={0}'
                               ' total_downloaded={1}'
                               ' last_page={2}'.format(
                               len(j_resp['fields']),
                               len(fields),
                               j_resp['lastPage']))

            if j_resp['lastPage'] == 'false':
                next_page_key = j_resp['nextPageKey']
            else:
                break
        else:
            raise Exception('Order tag defaults download failed.  msg={0}'.format(j_resp['status_message']))

    return fields


def download_enums(auth):
    enums = {}

    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer {0}'.format(auth.access_token),
        'x-api-key': auth.client
    }
    req = request_receiver.RequestReceiver()

    state_endpoint = 'https://apigateway.{domain}/risk/{env}/user/stateIds'
    j_resp = req.get(url=state_endpoint.format(domain=auth.domain, env=auth.environment),
                     headers=headers)
    if j_resp['status'] == 'Ok':
        enums['states'] = j_resp['states']
    else:
        raise Exception('State id download failed.  msg={0}'.format(j_resp['status_message']))

    country_endpoint = 'https://apigateway.{domain}/risk/{env}/user/countryIds'
    j_resp = req.get(url=country_endpoint.format(domain=auth.domain, env=auth.environment),
                     headers=headers)
    if j_resp['status'] == 'Ok':
        enums['countries'] = j_resp['countries']
    else:
        raise Exception('Country id download failed.  msg={0}'.format(j_resp['status_message']))

    markets_endpoint = 'https://apigateway.{domain}/pds/{env}/markets'
    j_resp = req.get(url=markets_endpoint.format(domain=auth.domain, env=auth.environment),
                     headers=headers)
    if j_resp['status'] == 'Ok':
        enums['markets'] = j_resp['markets']
    else:
        raise Exception('Markets download failed.  msg={0}'.format(j_resp['status_message']))

    return enums


def download_data(auth):
    common.order_tag_default_fields = download_order_tag_default_fields(auth)
    common.order_tag_defaults = download_order_tag_defaults(auth)
    common.users = download_users(auth)
    common.enums = download_enums(auth)


class UserData:
    def __init__(self, auth, user_info):
        user_get = user_download.User_GET(auth)
        self.__json_data = user_get.get(user_info['id'])

    @property
    def first_name(self):
        return self.__json_data.get('firstName', '')

    @property
    def last_name(self):
        return self.__json_data.get('lastName', '')

    @property
    def email(self):
        return self.__json_data.get('email', '')

    @property
    def user_name(self):
        return self.__json_data.get('alias', '')

    @property
    def user_id(self):
        return self.__json_data.get('id', '')

    @property
    def company_name(self):
        return self.__json_data['company'].get('name', '')

    @property
    def trading_disabled(self):
        trading_disabled = self.__json_data['settings'].get('disableTrading', 0)
        return 'True' if trading_disabled == 1 else 'False'

    @property
    def invitation_status(self):
        def is_pending(user): user['invitationPending'] == 1
        def is_retired(user): int(self.__json_data['userActive']) == 1 and 'personId' in self.__json_data # TODO update this when personId is added
        def is_provisional(user): 'personId' not in user or math.isnan(user['personId']) # TODO update this when personId is added

        status = 'Active'
        if is_pending(self.__json_data) == 1 and is_retired(self.__json_data):
            status = "Retired Re-invited"
        elif is_pending(self.__json_data):
            status = "Sent" if not self.__json_data['emailState'] else self.__json_data['emailState'] # TODO Update this when emailState is added
        elif is_provisional(self.__json_data):
            status = "Not Sent"
        elif is_retired(self.__json_data):
            status = "Retired";

        return self.__json_data.get('invitationPending', '')

    @property
    def access_level(self):
        if self.__json_data['settings'].get('fullAdmin', 0) == 1:
            access_level = 'Full Admin'
        elif self.__json_data['settings'].get('internalAdmin', 0) == 1:
            return 'Internal Admin'
        elif self.__json_data['settings'].get('viewOnlyAdmin', 0) == 1:
            access_level = 'View Only Admin'
        else:
            return 'User'

    @property
    def user_status(self):
        is_active = int(self.__json_data['userActive']) == 1
        if is_active:
            return 'Active'
        else:
            return 'Inactive'

    @property
    def trade_mode(self):
        # 1: View only, 2: Basic and 3: Professional
        mode = int(self.__json_data['tradeMode'])
        if mode == 1:
            return 'TT Standard (View Only)'
        elif mode == 2:
            return 'TT Standard'
        elif mode == 3:
            return 'TT Pro'
        else:
            return 'Unknown'

    @property
    def address1(self):
        return self.__json_data['address'].get('streetAddress1', '')

    @property
    def address2(self):
        return self.__json_data['address'].get('streetAddress2', '')

    @property
    def city(self):
        return self.__json_data['address'].get('city', '')

    @property
    def state(self):
        state_id = self.__json_data['address']['stateId']
        return get_state(state_id)

    @property
    def country(self):
        country_id = self.__json_data['address']['countryId']
        return get_country(country_id)


def get_state(state_id):
    return next((m['stateName'] for m in common.enums['states'] if m['stateId'] == state_id), None)


def get_country(country_id):
    return next((m['countryName'] for m in common.enums['countries'] if m['countryId'] == country_id), None)


def get_market_id(market_name):
    return int(next((m['id'] for m in common.enums['markets'] if m['name'] == market_name), None))


def get_field_id(field_name, market_name):
    market_id = get_market_id(market_name)
    return next((m['fieldId'] for m in common.order_tag_default_fields
                 if m['name'] == field_name
                 and m['marketId'] == market_id), None)


def get_field_value(user_id, field_name, market_name):
    field_id = get_field_id(field_name, market_name)
    return next((m['value'] for m in common.order_tag_defaults
                 if m['userId'] == user_id
                 and m['fieldId'] == field_id), '')


class OperatorIDReport:
    __format = [
        ("First Name", lambda user_data: user_data.first_name),
        ("Last Name", lambda user_data: user_data.last_name),
        ("Email", lambda user_data: user_data.email),
        ("UserID", lambda user_data: user_data.user_id),
        ("UserName", lambda user_data: user_data.user_name),
        ("Company Name", lambda user_data: user_data.company_name),
        ("Trading Disabled", lambda user_data: user_data.trading_disabled),
        # ("Invitation Status", lambda user_data: user_data.invitation_status),
        ("Access Level", lambda user_data: user_data.access_level),
        ("User Status", lambda user_data: user_data.user_status),
        ("Trade Mode", lambda user_data: user_data.trade_mode),
        ("Address1", lambda user_data: user_data.address1),
        ("Address2", lambda user_data: user_data.address2),
        ("City", lambda user_data: user_data.city),
        ("State", lambda user_data: user_data.state),
        ("Country", lambda user_data: user_data.country),
        ("CME - Operator ID", lambda user_data: get_field_value(user_data.user_id,'Operator ID','CME')),
        ("CFE - Operator ID", lambda user_data: get_field_value(user_data.user_id,'Operator ID','CFE')),
        ("ICE - Authorized Trader", lambda user_data: get_field_value(user_data.user_id,'Authorized Trader','ICE')),
        ("ICE_L - Authorized Trader", lambda user_data: get_field_value(user_data.user_id,'Authorized Trader','ICE_L'))
    ]

    def get_header(self):
        header = []
        for column in self.__format:
            header += [column[0]]
        return header

    def get_user_row(self, user_data):
        row = []
        for column in self.__format:
            row += [column[1](user_data)]
        return row

def print_format():
    logger.log('')
    logger.log('TT US Order Tag Default Report')


def main():
    versions.check_requirements()
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     usage=print_format())

    parser.add_argument('-v', '--verbose', required=False,
                        dest='verbose', action='store_true',
                        help='Enable verbose logging')
    parser.add_argument('-e', '--env', required=False,
                        dest='env', action='store',
                        choices=['ext_uat_cert', 'ext_prod_sim', 'ext_prod_live','int_dev_cert'], default='ext_uat_cert',
                        help='TT environment')
    parser.add_argument('-k', '--key', required=False,
                        dest='app_key', action='store',
                        help='TT RestAPI AppKey.  This argument can be omitted by setting the '
                             '"{0}" environment variable'.format(auth_handler.AppKeyEnvVar))
    parser.add_argument('-o', '--output', required=False,
                        dest='output', action='store',
                        help='Name of a file to write the programs output')

    parser.add_argument('--version', action='version', version='%(prog)s v{0}'.format(versions.ScriptVersion))
    parser.add_argument('--disable-throttle', required=False,
                        dest='disable_throttle', action='store_false',
                        help='Disable throttling of REST requests (may introduce errors)')
    parser.add_argument('--usage-plan', required=False,
                        dest='usage_plan', action='store',
                        choices=['Free', 'Low', 'Medium','High'], default='Low',
                        help='Key usage plan (sets throttle rate)')
    parser.add_argument('file', help='CSV output file')
    args = parser.parse_args()

    logger.set_outfile(args.output)
    logger.set_verbose(args.verbose)
    logger.log('Running TT Batch User Risk Limit Settings Import v{0}'.format(versions.ScriptVersion))
    logger.log('  Requested Environment: {0}'.format(args.env))
    if args.usage_plan and args.usage_plan == 'Free':
        request_receiver.set_throttle_rate(.34)
    elif args.usage_plan == 'Low':
        request_receiver.set_throttle_rate(.2)
    elif args.usage_plan == 'Medium':
        request_receiver.set_throttle_rate(.1)
    elif args.usage_plan == 'High':
        request_receiver.set_throttle_rate(.04)
    request_receiver.throttle_requests(args.disable_throttle)

    try:
        auth = auth_handler.RestAPIAuthenticator(args.env, args.app_key)
    except Exception as err:
        logger.log('Unable to authenticate: %s' % str(err))
        sys.exit(2)

    try:
        download_data(auth)
    except Exception as ex:
        logger.log('Error downloading data. msg={}'.format(ex.message))

    report = OperatorIDReport()
    with open(args.file, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(report.get_header())
        for user in common.users:
            try:
                data = UserData(auth, user)
                logger.log(u'Making report on user {}'.format(data.user_name))
                csvwriter.writerow(report.get_user_row(data))
            except Exception as ex:
                logger.log(u'ERROR: error processing user "{}", msg='.format(user['alias'], str(ex.message)))
                continue


if __name__ == "__main__":
    main()
