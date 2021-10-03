import json
import pytest
import requests
from requests import Response
import uuid
from base64 import b64encode
from time import sleep
from retry import retry

header = {'Content-type': 'application/json'}
header_webhooks = {"argyle_access_token": "9DXPR3JajywaKpwNNNV4kvVn8QEhZF"}


class API(object):

    def __init__(self, production=False, user_agent="Argyle QA Test"):
        if production:
            self.base_url = pytest.apiUrl
        else:
            self.base_url = pytest.apiSandbox
        self.internal_base_url = pytest.internal_base_url
        self.webhook_service = pytest.webhook_service
        self.client_name = None
        self.client_id = None
        self.api_key_name = None
        self.user_agent_header = {'User-Agent': user_agent}
        encoded_credentials = b64encode(bytes(f'{pytest.adminUser}:{pytest.adminPassword}',
                                              encoding='ascii')).decode('ascii')
        self.admin_header = {'Authorization': 'Basic %s' % encoded_credentials,
                             'Content-type': 'application/json'
                             }
        self.admin_header.update(self.user_agent_header)
        self.link_item_grouping = "QA_GROUPING"

    @retry(requests.exceptions.HTTPError, tries=10, delay=2)
    def create_user(self, base_url, api_id=None, api_secret=None, bearer=None, verify=True):

        print("Create user using client id: {} and client secret: {}".format(api_id, api_secret))
        url = "{}/users".format(base_url)
        if bearer:
            headers = {'Authorization': 'Bearer ' + bearer}
            headers.update(self.user_agent_header)
            response: Response = requests.post(url=url, headers=headers)
        else:
            response: Response = requests.post(url=url, auth=(api_id, api_secret), headers=self.user_agent_header)

        if verify:
            response.raise_for_status()
        return response

    def create_user_invite_template(self, client_id, client_secret, name, subject, page_heading, company):
        body = {
            "name": name,
            "email_body": "Hi, [Name]\n\n[Company] is working with a 3rd party to verify your work history.\nIt’s a quick process that should not take longer.\nGet started by clicking the link below.\n\nSinceerely,\n[Sender]",
            "sms_body": "\"[Company] has asked you to link your income sources. [Link]\"",
            "button": "Connect your employment account",
            "header": "[Company] is requesting you to connect your employment account",
            "subject": subject,
            "sender": "[Company]",
            "logo_url": "logo",
            "page_heading": page_heading,
            "page_description": "\"[Company] has asked you to link the companies you make money from\nas part of their service.\"",
            "page_button": "Link Companies",
            "company": company,
            "purpose": "Verify your income"
        }
        url = "{}/user-invite-templates/".format(self.base_url)
        response: Response = requests.post(url=url, auth=(client_id, client_secret), json=body,
                                           headers=self.user_agent_header)
        print("user invite template")
        print(response.content)
        print(response.status_code)
        assert response.status_code == 201
        return response.json()

    def send_user_invite_pd(self,
                            client_id,
                            client_secret,
                            template_id,
                            full_name,
                            email,
                            purpose,
                            link_items,
                            pds_only=False,
                            verification_selected=False,
                            enable_suggstions=False,
                            allow_add_allocation=True,
                            allow_editing=True):
        body = {
            "invite_template_id": template_id,
            "full_name": full_name,
            "email": email,
            "verification_selected": verification_selected,
            "purpose": purpose,
            "link_config": {
                "link_items": [link_items],
                "pay_distribution_items_only": pds_only
            },
            "pds_config": {
                "bank_account": {
                    "bank_name": "New Test Bank",
                    "routing_number": "084101234",
                    "account_number": "9483746361234",
                    "account_type": "checking"
                },
                "percent_allocation": {
                    "value": "20"
                },
                "allow_add_allocation": allow_add_allocation,
                "enable_suggestions": enable_suggstions,
                "allow_editing": allow_editing
            }
        }
        url = "{}/user-invites".format(self.base_url)
        response: Response = requests.post(url=url, auth=(client_id, client_secret), json=body,
                                           headers=self.user_agent_header)
        print("user invite")
        print(response.content)
        tries = 0
        while (response.status_code != 201 and tries < 20):
            response: Response = requests.post(url=url, auth=(client_id, client_secret), json=body,
                                               headers=self.user_agent_header)
            print("Status code: " + str(response.status_code))
            sleep(30)
            tries += 1
        print(response.status_code)
        assert response.status_code == 201
        return response.json()

    def send_user_invite_simple(self,
                                client_id,
                                client_secret,
                                template_id,
                                full_name,
                                email,
                                purpose,
                                verification_selected=False):
        body = {
            "invite_template_id": template_id,
            "full_name": full_name,
            "email": email,
            "verification_selected": verification_selected,
            "purpose": purpose
        }
        url = "{}/user-invites".format(self.base_url)
        response: Response = requests.post(url=url, auth=(client_id, client_secret), json=body,
                                           headers=self.user_agent_header)
        print(response.status_code)
        assert response.status_code == 201
        return response.json()

    def resend_user_invite(self, client_id, client_secret, user_invite_id):
        url = "{}/user-invites/{}".format(self.base_url, user_invite_id)
        response: Response = requests.post(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Revoke user invite {}".format(user_invite_id))
        assert response.status_code == 201
        return response.json()

    def revoke_user_invite(self, client_id, client_secret, user_invite_id):
        url = "{}/user-invites/{}/revoke".format(self.base_url, user_invite_id)
        response: Response = requests.post(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Revoke user invite {}".format(user_invite_id))
        assert response.status_code == 201
        return response.json()

    def delete_user_invite(self, client_id, client_secret, user_invite_id):
        url = self.base_url + "/user-invites/{}".format(user_invite_id)
        response: Response = requests.delete(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Deleted user invite by id: {}".format(user_invite_id))
        assert response.status_code == 200

    def delete_user_invite_template(self, client_id, client_secret, template_id):
        url = self.base_url + "/user-invite-templates/{}".format(template_id)
        response: Response = requests.delete(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Deleted user invite template by id: {}".format(template_id))
        assert response.status_code == 200

    def get_user_invite_template(self, client_id, client_secret, template_id):
        url = self.base_url + "/user-invite-templates/{}".format(template_id)
        response: Response = requests.get(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Get user invite template by id: {}".format(template_id))
        return response

    def delete_account_by_id(self, client_id, client_secret, account_id):
        url = self.base_url + "/accounts/{}".format(account_id)
        response: Response = requests.delete(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        # TODO remove sleep after account removal is done
        sleep(5)
        print("Deleted account {}".format(account_id))
        assert response.status_code == 204

    def get_account_ids_by_data_partner(self, client_id, client_secret, data_partner):
        url = self.base_url + "/accounts?data_partner={}".format(data_partner)
        response: Response = requests.get(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Get account ids by data partner {}".format(data_partner))
        assert response.status_code == 200
        return [result["id"] for result in response.json()["results"] if len(response.json()["results"]) > 0]

    def get_account_by_id(self, client_id, client_secret, account_id, status_code=200):
        url = self.base_url + "/accounts/{}".format(account_id)
        response: Response = requests.get(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Get account by id {}".format(account_id))
        print(response)
        assert response.status_code == status_code
        return response.json()

    def get_all_results_resource(self, client_id, client_secret, resource, expected_count=None, user_id=None,
                                 next=None):
        all_results = []
        results = self.get_resource(client_id, client_secret, resource, expected_count, user_id, next)
        all_results = all_results + results['results']
        while results['next']:
            results = self.get_resource(client_id, client_secret, resource, expected_count, user_id, results['next'])
            print(results['results'][0])
            print(len(results['results']))
            all_results = all_results + results['results']
        return all_results

    @retry(AssertionError, tries=10, delay=2)
    def get_resource(self, client_id, client_secret, resource, expected_count=None, user_id=None, next=None):
        url = self.base_url + "/{}".format(resource)
        if user_id:
            url = "{}?user={}".format(url, user_id)
        if next:
            url = next
        response: Response = requests.get(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Get resource {}".format(resource))
        print(response)
        response.raise_for_status()
        if expected_count:
            assert response.json()['count'] == expected_count
        return response.json()

    def generate_reports(self, client_id, client_secret, user_id):
        url = self.base_url + "/reports"
        body = {
            "user": user_id,
            "type": "voie",
            "metadata": {
                "purpose": "Risk Assessment",
                "email": "Lorna@company.com"
            }
        }
        response: Response = requests.post(url=url, json=body, auth=(client_id, client_secret),
                                           headers=self.user_agent_header)
        print("Generate reports")
        assert response.status_code == 201
        return response.json()

    @retry(requests.exceptions.HTTPError, tries=10, delay=2)
    def create_user_token(self, client_id, client_secret, user_id):
        url = self.base_url + "/user-tokens"
        body = {"user": user_id}
        response: Response = requests.post(url=url, json=body, auth=(client_id, client_secret),
                                           headers=self.user_agent_header)
        print("Create user token")
        print(client_id)
        print(client_secret)
        print(response)
        response.raise_for_status()
        return response.json().get("access")

    def get_user_by_id(self, client_id, client_secret, user_id, status_code=200):
        url = self.base_url + "/users/{}".format(user_id)
        response: Response = requests.get(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Get user by id {}".format(user_id))
        assert response.status_code == status_code
        return response.json()

    def patch_user_by_id(self, client_id, client_secret, user_id, body):
        url = self.base_url + "/users/{}".format(user_id)
        print("Patch user by id {} with \n body: ".format(user_id, body))
        response: Response = requests.patch(url=url, json=body, auth=(client_id, client_secret),
                                            headers=self.user_agent_header)
        assert response.status_code == 200
        return response.json()

    def delete_user_by_id(self, client_id, client_secret, user_id):
        url = self.base_url + "/users/{}".format(user_id)
        response: Response = requests.delete(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Delete user by id {}".format(user_id))
        assert response.status_code == 204

    def get_link_item(self, client_id, client_secret, link_item_name, status_code=200):
        url = self.base_url + "/link-items/{}".format(link_item_name)
        response: Response = requests.get(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Get link item by name {}".format(link_item_name))
        assert response.status_code == status_code
        return response.json()

    def search_link_item(self, client_id, client_secret, link_item_name):
        url = self.base_url + "/search/link-items?q={}".format(link_item_name)
        response: Response = requests.get(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Get link item by name {}".format(link_item_name))
        assert response.status_code == 200
        return response.json()

    def get_link_items(self, client_id, client_secret, limit=None, offset=None):
        if limit:
            url = self.base_url + "/link-items?limit={}&offset={}".format(limit, offset)
        else:
            url = self.base_url + "/link-items"
        response: Response = requests.get(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Get link all items")
        assert response.status_code == 200
        return response.json()

    def get_pay_allocations(self, client_id, client_secret, user_id=None):
        if user_id:
            user = "?user={}".format(user_id)
        else:
            user = ""
        url = self.base_url + "/pay-allocations{}".format(user)
        response: Response = requests.get(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Get pay-allocations by user id {}".format(user_id))
        print(response.json())
        assert response.status_code == 200
        return response.json()

    def get_pay_allocation_by_id(self, client_id, client_secret, allocation_id, status_code=200):
        url = self.base_url + "/pay-allocations/{}".format(allocation_id)
        response: Response = requests.get(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Get pay-allocations by allocation id {}".format(allocation_id))
        print(response.json())
        assert response.status_code == status_code
        return response.json()

    def get_employment_data(self, client_id, client_secret, endpoint, user_id):
        url = self.base_url + "/{}?user={}".format(endpoint, user_id)
        response: Response = requests.get(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Get {} by user id {}".format(endpoint, user_id))
        print(response.content)
        assert response.status_code == 200
        return json.loads(response.content.decode("utf-8", "ignore"))

    def get_reports_data(self, client_id, client_secret, user_id, retry_max=30, status_desired="generated"):
        url = self.base_url + "/reports?user={}".format(user_id)
        condition_reports = True
        while retry_max > 0 and condition_reports:
            print("Retry get reports by user id {} retry no {}".format(user_id, retry_max))
            response = requests.get(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
            print(response.content)
            if response.status_code == 200:
                if len(response.json()['results']) == 0:
                    pass
                elif response.json()['results'][0]['status'] == status_desired:
                    condition_reports = False
            sleep(5)
            retry_max -= 1
        print("Reports response")
        print(response.status_code)
        print(response.content)
        assert response.status_code == 200
        return json.loads(response.content.decode("utf-8", "ignore"))

    def check_webhook_service(self, unique_id, multiple_elems=False,
                              retry_times=20,
                              number_of_events_expected=1, greater_than=False,
                              wait_for_event=None
                              ):
        """
        event -> must match with at least one JSONSchema from utilities/json_schemas
        """
        url = "{}/{}".format(self.webhook_service, unique_id)
        print("Requesting get to fetch webhook to URL: {}".format(url))
        response: Response
        no_webhooks = 0
        conditions_met = False
        wait_for_event_condition = False
        wait_for_no_webhooks = False
        while retry_times > 0 and not conditions_met:
            retry_times -= 1
            response: Response = requests.get(url=url, headers=header_webhooks)
            print("try again")
            print("Response body: {}".format(response.content))
            if response.content == b"''":
                no_webhooks = 0
            elif isinstance(response.json()[0], dict):
                no_webhooks = 1
            else:
                no_webhooks = len(response.json())
            # Check for desired no_webhooks
            if greater_than and no_webhooks > number_of_events_expected:
                wait_for_no_webhooks = True
            elif not greater_than and no_webhooks == number_of_events_expected:
                wait_for_no_webhooks = True
            print("Number of events is : {}".format(no_webhooks))

            # Having desired no_webhooks is mandatory
            if not wait_for_no_webhooks:
                # When multiple webhooks are expected and want to make sure you wait to get a desired webhook event
                if wait_for_event and no_webhooks >= 1:
                    print("Wait for desired event {} retry_times {}".format(wait_for_event, retry_times))
                    for webhook_event in response.json():
                        if webhook_event[1]['event'] == wait_for_event:
                            wait_for_event_condition = True
                            break
                        else:
                            wait_for_event_condition = False
            else:
                wait_for_event_condition = True
            # both conditions should be False in order to exit while
            conditions_met = wait_for_no_webhooks and wait_for_event_condition
            if not conditions_met:
                sleep(5)
            else:
                break

        if not greater_than:
            assert no_webhooks == number_of_events_expected, "Number of events {} is not the one expected {}" \
                .format(no_webhooks, number_of_events_expected)
        else:
            assert no_webhooks > number_of_events_expected, "Number of events {} is not greater than the one expected {}" \
                .format(no_webhooks, number_of_events_expected)
        try:
            response.json()
        except json.decoder.JSONDecodeError as e:
            assert False, 'Webhook get return empty to many times'
        webhook_response = response.json()
        if multiple_elems:
            pass
        else:
            webhook_response = webhook_response[-1]
        print("Webhook response: {}".format(webhook_response))
        return webhook_response

    def check_resource(self, client_id, client_secret, endpoint, resource):
        print("Checking resource {} {}".format(endpoint, resource))
        url = self.base_url + "/{}/{}".format(endpoint, resource)
        response: Response = requests.get(url=url, auth=(client_id, client_secret), headers=self.user_agent_header)
        print("Check resource response \n Status: {} \n Response:\n {}".format(response.status_code,
                                                                               response.content))
        return response.status_code == 200

    def update_data(self, email, endpoint, password, user_id=None):
        print("Update data from endpoint {}".format(endpoint))
        url = self.base_url + "/{}".format(endpoint)
        if user_id:
            url = "{}?user={}".format(url, user_id)
        response: Response = requests.get(url=url, auth=(email, password), headers=self.user_agent_header)
        body = response.json()
        print("body")
        print(body)
        url = self.base_url + "/{}/{}".format(endpoint, body["results"][0]["id"])
        print("url")
        print(url)
        response: Response = requests.patch(url=url, json=body, auth=(pytest.adminUser, pytest.adminPassword),
                                            headers=self.user_agent_header)
        print(response)
        assert response.status_code == 200

    def remove_pay_allocation(self, email, password, pay_allocation_id):
        print("Delete pay-allocation by id: {}".format(pay_allocation_id))
        url = self.base_url + "/pay-allocations/{}/remove".format(pay_allocation_id)
        response: Response = requests.post(url=url, auth=(email, password), headers=self.user_agent_header)
        print(response)
        assert response.status_code == 202

    def delete_data(self, email, endpoint, password):
        print("Delete data from endpoint {}".format(endpoint))
        url = self.base_url + "/{}".format(endpoint)
        response: Response = requests.get(url=url, auth=(email, password), headers=self.user_agent_header)
        body = response.json()
        url = self.base_url + "/{}/{}".format(endpoint, body["results"][0]["id"])
        response: Response = requests.delete(url=url, auth=(pytest.adminUser, pytest.adminPassword),
                                             headers=self.user_agent_header)
        assert response.status_code == 204

    def trigger_webhooks_sandbox_periodic_scan(self, account_id, email, password):
        print("Trigger sandbox periodic scan for account: {}".format(account_id))
        url = self.base_url + "/accounts/{}/periodic-scan".format(account_id)
        headers = {"Content-Type": "application/json"}
        headers.update(self.user_agent_header)
        response: Response = requests.post(url=url, headers=headers, auth=(email, password))
        assert response.status_code == 201

    def configure_webhook(self, client_id, client_secret, events, name, config=None, secret="lorem ipsum"):
        unique_id = str(uuid.uuid4())
        print("unique_id : " + unique_id)
        url = "{}/{}".format(self.webhook_service, unique_id)
        print("Configuring webhook with: \n events: {} \n name: {} url: {} \n config: {} \n secret {} \n"
              .format(events, name, url, config, secret))
        base_url = self.base_url + "/webhooks"
        if config:
            body = {
                "events": events,
                "name": name,
                "url": url,
                "secret": secret,
                "config": config
            }
        else:
            body = {
                "events": events,
                "name": name,
                "url": url,
                "secret": secret
            }
        print("Body")
        print(body)
        print(base_url)
        response: Response = requests.post(url=base_url, auth=(client_id, client_secret), json=body,
                                           headers=self.user_agent_header)
        print("Configure webhook response")
        print(response.content)
        print(response.status_code)
        assert response.status_code == 201
        return unique_id, response.json()

    def set_client_permissions(self, admin_id, admin_secret, client_id, permissions):
        print("Set client permissions for client id: " + client_id)
        body_clients = {
            "permissions": permissions,
            "is_test": True
        }

        headers = {'Content-type': 'application/json'}
        headers.update(self.user_agent_header)
        response: Response = requests.put(url=pytest.internal_base_url + "/clients/" + client_id,
                                          auth=(admin_id, admin_secret), json=body_clients, headers=headers)
        assert response.status_code == 200

    def delete_webhook(self, client_id, client_secret, unique_id):

        print("Delete webhook id {}".format(unique_id))
        base_url = "{}/webhooks/{}".format(self.base_url, unique_id)

        response: Response = requests.delete(url=base_url, auth=(client_id, client_secret))
        print("Delete webhook response")
        print(response.content)
        print(response.status_code)
        assert response.status_code == 204

    @staticmethod
    @retry(IndexError, tries=10, delay=2)
    def approve_client(mail, password="passgoodA1@"):
        _url = f"{pytest.argyle_develop_data_service}/client-requests"
        name = mail.split("@")[0]
        session = requests.Session()
        session.auth = (pytest.adminUser, pytest.adminPassword)
        session.headers = {'Content-Type': 'application/json',
                           'X-Argyle-Api-Token': pytest.x_argyle}
        response = json.loads(session.get(_url).text)["data"]
        id = [data for data in response if data["email"] == mail][0]["id"]
        body = {
            "firstName": name,
            "lastname": f"{name}LastName",
            "email": f"{mail}",
            "company": f"{name}CompanyName",
            "password": password,
            "termsAccepted": True,
            "id": id}
        print(body)
        r = session.post(pytest.argyle_develop_data_service + "/client-requests/approve",
                         json=body)
        print("status code")
        print(r.status_code)
        print(r.text)

    @retry(requests.exceptions.HTTPError, tries=10, delay=2)
    def set_client_permissions(self, mail, password, permissions=["data-viewer-access",
                                                                  "scan-pay-distribution",
                                                                  "scan-historical-info",
                                                                  "update-pay-distribution",
                                                                  "scan-future-info"]):
        # permissions -> default value is full access
        response: Response = requests.get(url=pytest.apiSandbox + "/clients", auth=(mail, password))
        response.raise_for_status()
        response: Response = requests.put(
            url=pytest.internal_base_url + "/clients/" + response.json()['results'][0]['id'],
            json={"permissions": permissions}, headers=header, auth=(pytest.adminUser, pytest.adminPassword))
        response.raise_for_status()

    @retry(requests.exceptions.HTTPError, tries=10, delay=2)
    def post_client_accounts(self, specified_email=False):
        pytest.client_id = str(uuid.uuid4())
        pytest.new_email = "dont-send_{}@mailinator.com".format(pytest.client_id) if not specified_email \
            else specified_email
        client_name = "QA ARGYLE {}".format(pytest.client_id)
        self.api_key_name = "APIKEYNAME {}".format(pytest.client_id)
        print("Creating username {} with client_member_name {} and pass {}".format(pytest.new_email,
                                                                                   client_name,
                                                                                   pytest.console_password))
        body = {"client": {
            "id": pytest.client_id,
            "is_test": True
        },
            "username": pytest.new_email,
            "first_name": "TestUser",
            "password": pytest.console_password,
            "password2": pytest.console_password,
            "membership": 'admin'
        }
        response: Response = requests.post(url=self.base_url + "/client-accounts", json=body, headers=self.admin_header)
        print("/client-accounts")
        print(response.status_code)
        print(response.content)
        response.raise_for_status()
        self.client_id = pytest.client_id
        self.client_name = client_name

    @retry(requests.exceptions.HTTPError, tries=10, delay=2)
    def post_clients(self):
        body_clients = {"id": pytest.client_id,
                        "terms_accepted": True,
                        "name": self.client_name,
                        "is_test": True
                        }
        encoded_credentials = b64encode(bytes(f'{pytest.new_email}:{pytest.console_password}',
                                              encoding='ascii')).decode('ascii')
        pytest.new_headers_auth = {'Authorization': 'Basic %s' % encoded_credentials,
                                   'Content-type': 'application/json'}
        pytest.new_headers_auth.update(self.user_agent_header)
        response: Response = requests.put(url=self.base_url + "/clients/" + pytest.client_id,
                                          json=body_clients, headers=pytest.new_headers_auth)

        print(response.content)
        print(response.status_code)
        response.raise_for_status()

    @retry(requests.exceptions.HTTPError, tries=10, delay=2)
    def post_api_keysets(self):
        create_api_body = {"name": self.api_key_name,
                           "live": True,
                           "sandbox": True}
        response: Response = requests.post(url=pytest.internal_base_url + "/api-keysets",
                                           json=create_api_body, headers=pytest.new_headers_auth)
        print("/api-keysets")
        print(response.content)
        print(response.status_code)
        response.raise_for_status()

    def create_client_account(self, non_sandbox=False, specified_email=False):
        self.post_client_accounts(specified_email)
        self.post_clients()
        self.post_api_keysets()
        self.get_api_keys(pytest.new_headers_auth)
        if non_sandbox:
            self.set_client_permissions(pytest.new_email, pytest.console_password)

    @retry(requests.exceptions.HTTPError, tries=10, delay=10)
    def delete_client(self, client_id=None):
        # headers = {'X-Argyle-Api-Token': pytest.x_argyle}
        headers = self.user_agent_header
        # headers.update(self.user_agent_header)
        # This logic is just to make sure that
        client_id = pytest.client_id if not client_id else client_id
        # response: Response = requests.delete(url=pytest.argyle_develop_data_service + "/clients/" + client_id,
        #                                      headers=headers)

        response: Response = requests.delete(url=pytest.apiUrl + "/clients/" + client_id,
                                             headers=headers, auth=(pytest.adminUser, pytest.adminPassword))

        response.raise_for_status()

    def generate_pds_config(self, client_id, client_secret, config):
        response: Response = requests.post(url=self.base_url + '/pay-distribution-config/encrypt',
                                           auth=(client_id, client_secret), json=config, headers=self.user_agent_header)
        response.raise_for_status()
        encrypted_config = response.json()['encrypted_config']
        print(response.content)
        return encrypted_config

    def get_clients(self):
        response: Response = requests.get(url=self.base_url + "/client-accounts", headers=self.admin_header)
        print("GET /client-accounts")
        print(response.status_code)
        print(response.content)
        return response.json()

    def get_token_member(self, member_id):
        response: Response = requests.get(url=pytest.internal_base_url + "/client-accounts/{0}/auth-token"
                                          .format(member_id), headers=self.admin_header)
        print("Get Token member_id {}".format(member_id))
        response.raise_for_status()
        token = response.json()['token']
        authorization_member_header = {
            "authorization": "Bearer {}".format(token)}
        return authorization_member_header

    @retry(requests.exceptions.HTTPError, tries=10, delay=10)
    def get_api_keys(self, authorization_member_header):
        response: Response = requests.get(url=pytest.internal_base_url + "/api-keysets",
                                          headers=authorization_member_header)
        response.raise_for_status()
        print("GET /api-keysets")
        print(response.status_code)
        print(response.content)
        api_keys = response.json()["results"][0]['api_keys']
        for api_key in api_keys:
            if api_key['environment'] == 'production':
                pytest.new_production_id = api_key['client_id']
                pytest.new_production_secret = api_key['client_secret']
            else:
                pytest.new_sandbox_id = api_key['client_id']
                pytest.new_sandbox_secret = api_key['client_secret']
        print("### Production ###")
        print(pytest.new_production_id)
        print(pytest.new_production_secret)
        print("### Sandbox ###")
        print(pytest.new_sandbox_id)
        print(pytest.new_sandbox_secret)

    def wait_account_status_done(self, api_id, api_secret, account_id):
        sleep_time_between_checks = 5
        timeout_max = 60 * 60 * 1  # max 1 hour
        status = self.get_account_by_id(api_id, api_secret, account_id)['status']
        while status != 'done' and timeout_max:
            print("Waiting for status of account {} in 'done' currently {} time left {} seconds"
                  .format(account_id, status, timeout_max))
            timeout_max = timeout_max - sleep_time_between_checks
            sleep(sleep_time_between_checks)
            status = self.get_account_by_id(api_id, api_secret, account_id)['status']
            if status == 'done':
                print("Status expected 'Done'")
                return timeout_max
