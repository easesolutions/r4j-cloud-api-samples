import math
from api import cloud_jira_helper, cloud_r4j_helper
from report.log_and_report import write_logging_server_response

MAX_RESULTS = 100


def get_cloud_issue_folders(project_key, folder_issue_type_id):
    start_at = 0
    total = 1
    folder_issue_type_name = cloud_jira_helper.get_issue_type_name(folder_issue_type_id)
    request_body = {"jql": f'issuetype = "{folder_issue_type_name}" and project = {project_key}',
                    "maxResults": MAX_RESULTS, "fields": ["summary"], "startAt": start_at}
    cloud_issue_folders = []
    while len(cloud_issue_folders) != total:
        response = cloud_jira_helper.search_for_issues_using_jql(request_body)
        cloud_issues = response.json()
        if response.status_code == 200:
            total = cloud_issues["total"]
            start_at += MAX_RESULTS
            request_body["startAt"] = start_at
            cloud_issue_folders += [{"issue_key": issue["key"], "summary": issue["fields"]["summary"]}
                                    for issue in cloud_issues["issues"]]
            message = f"Folder issues retrieved from {cloud_issues['startAt']} to {len(cloud_issue_folders)}" \
                      f" in Jira Cloud instance"
            write_logging_server_response(response, message)
        else:
            message = "Could not retrieve the folder issues in Jira cloud instance"
            write_logging_server_response(response, message, True)

    return cloud_issue_folders


def delete_tree_items_by_project_key(project_key):
    issues = set()
    start_at = 0
    cloud_r4j_helper.get_all_existing_issues_in_a_tree_by_project_key(project_key, issues, start_at)
    issues = list(issues)
    request_iterator = math.ceil(len(issues) / MAX_RESULTS)
    for i in range(request_iterator):
        stop_at = start_at + MAX_RESULTS
        response = cloud_r4j_helper.delete_existing_items_from_tree(project_key, issues[start_at:stop_at])
        if response.status_code == 200:
            message = F"The tree root children were successfully deleted"
            write_logging_server_response(response, message)
        else:
            message = "Incapable of delete all items of tree, you cannot continue with the migration"
            write_logging_server_response(response, message, True)
        start_at += MAX_RESULTS
