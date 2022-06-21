import math
from api import cloud_jira_helper, cloud_r4j_helper
from report.log_and_report import write_logging_server_response

MAX_RESULTS = 100
ROOT_FOLDER = -1
PROJECT_EMPTY_START_AT = 0


def verify_authorized_in_r4j_api():
    response = cloud_r4j_helper.get_activate_project(None)
    if response.status_code == 401:
        message = "INVALID AUTHENTICATION: You are not authorized to use r4j REST API"
        write_logging_server_response(response, message, True, ValueError)  # CHECK ERROR
    elif response.status_code == 200:
        message = "You are authorized to use r4j REST API, you can continue with the migration"
        write_logging_server_response(response, message)
        return True


def verify_data_center_project_exists_in_cloud(project_key):
    response = cloud_jira_helper.get_project_by_project_id_or_key(project_key)
    if response.status_code == 200 and response.json()["key"] == project_key:
        message = "Project exists on jira cloud"
        write_logging_server_response(response, message)
        project = response.json()
        return verify_project_is_active_r4j_in_cloud(project)
    else:
        message = "ERROR: Project not found on jira cloud"
        write_logging_server_response(response, message, True, AssertionError)


def verify_project_is_active_r4j_in_cloud(project):
    response = cloud_r4j_helper.get_activate_project(project["key"])
    if response.status_code == 200 and len(response.json()["values"]) > 0:
        if response.json()["values"][0]["key"] == project["key"]:
            message = "Project activated in rj4 cloud"
            write_logging_server_response(response, message)
            return True
    else:
        active_project = input(f"Do you want active project {project['name']} Y/N?\t")
        if active_project.lower() == "y":
            activate_project_response = cloud_r4j_helper.\
                activate_projects(project["id"], project["key"], project["name"], project["avatarUrls"]["24x24"])
            if activate_project_response.status_code == 201:
                message = f"The project {project['name']} was successfully activated in the rj4 cloud."
                write_logging_server_response(activate_project_response, message)
                return True
            else:
                message = \
                    f"ACTIVATION PROJECT ERROR: The project {project['name']} cannot be activated in the rj4 cloud"
                write_logging_server_response(activate_project_response, message, True, AssertionError)
        else:
            message = "ACTIVATION PROJECT ERROR: Project in not activated in rj4 cloud"
            write_logging_server_response(response, message, True, AssertionError)


def verify_all_data_center_tree_issues_in_cloud_instance(tree_items_list):
    start_at = 0
    issue_keys_and_summary_response = []
    tree_issues_list = [tree_issue for tree_issue in tree_items_list if "folder_name" not in tree_issue.keys()]
    request_iterator = math.ceil(len(tree_issues_list) / MAX_RESULTS)
    tree_items_key_list = tuple([tree_item['issue_key'] for tree_item in tree_issues_list])
    issue_keys_and_summary_expected = [{"issue_key": tree_item['issue_key'], "summary": tree_item["summary"]}
                                       for tree_item in tree_issues_list]

    request_body = {"jql": f"issueKey in {tree_items_key_list}", "maxResults": MAX_RESULTS, "fields": ["summary",
                    "issuetype"], "startAt": start_at}

    for i in range(request_iterator):
        response = cloud_jira_helper.search_for_issues_using_jql(request_body)
        cloud_issues = response.json()
        if response.status_code == 200:
            start_at += MAX_RESULTS
            request_body["startAt"] = start_at
            issue_keys_and_summary_response += [{"issue_key": issue["key"], "summary": issue["fields"]["summary"]}
                                                for issue in cloud_issues["issues"]]
            message = f"Issues retrieved from {cloud_issues['startAt']} to {len(issue_keys_and_summary_response)}" \
                      f" in Jira Cloud instance"
            write_logging_server_response(response, message)
        else:
            message = "CLOUD ISSUES ERROR: Could not retrieve the issues in Jira cloud instance"
            write_logging_server_response(response, message, True, ConnectionError)

    return False not in [issue in issue_keys_and_summary_response for issue in issue_keys_and_summary_expected]


def verify_folder_issue_type_configured_in_cloud(project_key):
    response = cloud_r4j_helper.get_folder_issue_type()
    folder_issue_type = response.json()["folderIssueType"]
    if folder_issue_type is not None:
        message = "Folder issue type is configured in cloud instance"
        write_logging_server_response(response, message)
        return verify_folder_issue_type_on_project_issue_types(project_key, folder_issue_type)
    else:
        message = "FOLDER ISSUE TYPE ERROR: Folder issue type is not configured in cloud instance"
        write_logging_server_response(response, message, True, AssertionError)


def verify_folder_issue_type_on_project_issue_types(project_key, folder_issue_type):
    response = cloud_jira_helper.get_project_issue_types(project_key)
    if response.status_code == 200:
        project_issue_types = response.json()
        folder_issue_type_in_project_issue_types = \
            str(folder_issue_type) in [project_issue_type["id"] for project_issue_type in project_issue_types]
        if folder_issue_type_in_project_issue_types:
            message = f"Folder issue type is include on project {project_key} issue types"
            write_logging_server_response(response, message)
            return folder_issue_type_in_project_issue_types
        else:
            message = f"PROJECT ISSUE TYPES ERROR: Folder issue type not found on project {project_key} issue types" \
                      f"\n\n If you want to continue with the migration you need to configure issue types on project " \
                      f"{project_key} and include folder issue type"
            write_logging_server_response(response, message, True, AssertionError)
    else:
        message = f"PROJECT ISSUE TYPES ERROR: Cannot possible to retrieve the issue types on project {project_key}"
        write_logging_server_response(response, message, True, ConnectionError)


def verify_that_the_project_tree_is_empty(project_key):
    response = cloud_r4j_helper.get_tree_structure(project_key, ROOT_FOLDER, MAX_RESULTS, PROJECT_EMPTY_START_AT)
    existing_issues = response.json()
    if response.status_code == 200 and len(existing_issues["values"][0]["children"]) == 0:
        message = "The project tree is empty, you can continue with the migration"
        write_logging_server_response(response, message)
        return True
    else:
        message = "CLOUD TREE ERROR: The project tree is not empty, you cannot continue with the migration"
        print(f"\nIf you want to continue with the migration, you need to run:\n \tpython cloud_clean_tree.py "
              f"{project_key}")
        write_logging_server_response(response, message, True, AssertionError)


def run_project_cloud_verifications(project_key):
    if verify_authorized_in_r4j_api():
        if verify_data_center_project_exists_in_cloud(project_key) and \
            verify_folder_issue_type_configured_in_cloud(project_key) and \
                verify_that_the_project_tree_is_empty(project_key):
            return True
        else:
            return False

