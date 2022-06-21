import requests
from uplink import Consumer, get, delete, headers, json, Body, post, Query
from uplink.auth import ApiTokenHeader, BasicAuth
import urllib3
from config.config import CLOUD_ENV


class R4JCRestApi(Consumer):
    ease_endpoint = 'rest/api/1/'

    @get("{}{}".format(ease_endpoint, 'tree/projects/{project_key}/items/{id_or_jira_issue_key}'))
    def get_tree_structure(self, project_key, id_or_jira_issue_key, maxResults: Query, startAt: Query):
        """Get tree structure"""

    @get("{}{}".format(ease_endpoint, "projects"))
    def get_activate_project(self, query: Query):
        """Get active projects"""

    @headers({"Accept": "application/json", "Content-Type": "application/json"})
    @json
    @post("{}{}".format(ease_endpoint, "projects"))
    def activate_projects(self, body: Body):
        """Activate project by project id"""

    @get("{}{}".format(ease_endpoint, 'configurations'))
    def get_folder_issue_type(self):
        """get the current folder issue type"""

    @delete("{}{}".format(ease_endpoint, 'tree/projects/{project_key}/items'))
    def delete_existing_items_from_tree(self, project_key, idOrJiraIssueKey: Query):
        """Delete tree item by item id or jira issue key"""

    @headers({"Accept": "application/json", "Content-Type": "application/json"})
    @json
    @post("{}{}".format(ease_endpoint, 'tree/projects/{project_key}/items'))
    def add_existing_items_to_a_tree(self, project_key, items: Body):
        """Add existing item(s) to a tree"""


class JiraCloudApi(Consumer):
    jira_endpoint = '/rest/api/3/'

    @headers({"Accept": "application/json", "Content-Type": "application/json"})
    @json
    @post("{}{}".format(jira_endpoint, "search"))
    def search_for_issues_using_jql(self, body: Body):
        """Search issues through jql"""

    @get("{}{}".format(jira_endpoint, "project/{project_id_or_key}"))
    def get_project_by_project_id_or_key(self, project_id_or_key):
        """Get project by project id or key"""

    @json
    @post("{}{}".format(jira_endpoint, 'issue'))
    def create_issue(self, body: Body):
        """Create new issue"""

    @get("{}{}".format(jira_endpoint, "issuetype/project"))
    def get_project_issue_types(self, projectId: Query):
        """Get issue types per project"""

    @get("{}{}".format(jira_endpoint, "issuetype/{issue_type_id}"))
    def get_issue_type(self, issue_type_id):
        """Get issue type by issue type id"""


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
session = requests.session()
session.verify = False

# Needs to passing token as auth header value
r4j_api_token = ApiTokenHeader("Authorization", f"JWT {CLOUD_ENV.r4j_api_token}")

r4j_cloud_api = R4JCRestApi(CLOUD_ENV.r4j_api_url, auth=r4j_api_token, client=session)
jira_cloud_api = JiraCloudApi(CLOUD_ENV.application_url,
                              auth=BasicAuth(CLOUD_ENV.username, CLOUD_ENV.jira_api_token), client=session)
