from api.data_center.api import jira_api


def get_issue_by_key(issue_key):
    response = jira_api.get_issue_by_key(issue_key).json()
    return response


if __name__ == '__main__':
    issue = get_issue_by_key("BPS-153")
    DEBUG_POINT = ""
