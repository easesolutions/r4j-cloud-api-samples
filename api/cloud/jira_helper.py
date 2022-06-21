from api.cloud.api import jira_cloud_api
from report.log_and_report import write_logging_dry_run_message, write_logging_server_response


def search_for_issues_using_jql(body):
    return jira_cloud_api.search_for_issues_using_jql(body)


def get_project_by_project_id_or_key(project_id_or_key):
    return jira_cloud_api.get_project_by_project_id_or_key(project_id_or_key)


def create_issue(project, issue_type, issue_summary, dry_run):
    request_body = {"fields": {"summary": issue_summary, "issuetype": {"id": issue_type}, "project": {"id": project}}}
    if dry_run:
        message = f"Created issue folder with the summary: {issue_summary}"
        write_logging_dry_run_message(message, request_body)
        return None
    else:
        response = jira_cloud_api.create_issue(request_body)
        return response


def get_project_issue_types(project_key):
    response = get_project_by_project_id_or_key(project_key).json()
    project_id = response["id"]
    response = jira_cloud_api.get_project_issue_types(project_id)
    return response


def get_issue_type_name(folder_issue_type_id):
    response = jira_cloud_api.get_issue_type(folder_issue_type_id)
    if response.status_code == 200:
        return response.json()["untranslatedName"]
    else:
        message = f"FOLDER ISSUE TYPE ERROR: Cannot possible to retrieve folder issue type name from Jira cloud"
        write_logging_server_response(response, message, True, ConnectionError)
