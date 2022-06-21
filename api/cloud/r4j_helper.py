from api.cloud.api import r4j_cloud_api
from report.log_and_report import write_logging_dry_run_message

MAX_RESULTS = 100
ROOT_FOLDER = -1


def get_activate_project(project_key):
    return r4j_cloud_api.get_activate_project(project_key)


def activate_projects(project_id, project_key, project_name, project_icon_url):
    request_body = [
      {
        "id": project_id,
        "key": project_key,
        "name": project_name,
        "icon": project_icon_url
      },
    ]
    return r4j_cloud_api.activate_projects(request_body)


def get_folder_issue_type():
    return r4j_cloud_api.get_folder_issue_type()


def get_all_existing_issues_in_a_tree_by_project_key(project_key, issues, start_at):
    existing_issues = get_tree_structure(project_key, ROOT_FOLDER, MAX_RESULTS, start_at).json()
    if not existing_issues['isLast']:
        [issues.add(item["id"]) for item in existing_issues["values"][0]["children"]]
        get_all_existing_issues_in_a_tree_by_project_key(project_key, issues, start_at + MAX_RESULTS)
    else:
        [issues.add(item["id"]) for item in existing_issues["values"][0]["children"]]


def get_tree_structure(project_key, id_or_jira_issue_key, max_results, start_at):
    tree_structure = r4j_cloud_api.get_tree_structure(project_key, id_or_jira_issue_key, max_results, start_at)
    return tree_structure


def delete_existing_items_from_tree(project_key, id_or_jira_issue_key):
    id_or_jira_issue_key = ",".join(list(map(str, id_or_jira_issue_key)))
    deleted_items = r4j_cloud_api.delete_existing_items_from_tree(project_key, id_or_jira_issue_key)
    return deleted_items


def add_existing_items_to_a_tree_by_parent_id_and_items(project_key, parent_id=None, jira_issue_key=None, items=None,
                                                        dry_run=False):
    """Items require two parameters [{jiraIssueId: int, position: int}, ...]"""
    request_body = {
        "id": parent_id,
        "jiraIssueKey": jira_issue_key,
        "items": items
    }
    if dry_run:
        parent = "root folder" if parent_id is not None else jira_issue_key
        message = f"Created {parent} folder children items in tree cloud"
        write_logging_dry_run_message(message, request_body)
        return None
    else:
        response = r4j_cloud_api.add_existing_items_to_a_tree(project_key, request_body)
        return response
