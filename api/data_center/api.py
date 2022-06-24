import requests
from uplink import Consumer, get
from uplink.auth import BasicAuth, BearerToken
import urllib3
from config.config import DC_ENV


class R4jApi(Consumer):
    ease_endpoint = 'rest/com.easesolutions.jira.plugins.requirements/2.0/'
    ease_endpoint_01 = 'rest/com.easesolutions.jira.plugins.requirements/1.0/'

    @get("{}{}".format(ease_endpoint_01, 'tree/{project_key}'))
    def get_complete_tree_structure_by_project_key(self, project_key):
        """Get the folder structure of the project key provided"""


class JiraAPI(Consumer):

    jira_endpoint = 'rest/api/2/'

    @get("{}{}".format(jira_endpoint, 'issue/{issue_key}'))
    def get_issue_by_key(self, issue_key):
        """Get issue details by key"""


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
session = requests.Session()
session.verify = False
api_auth = BasicAuth(DC_ENV.username, DC_ENV.password) if DC_ENV.pat == '' else BearerToken(DC_ENV.pat)
r4j_api = R4jApi(DC_ENV.application_url, auth=api_auth, client=session)
jira_api = JiraAPI(DC_ENV.application_url, auth=api_auth, client=session)
