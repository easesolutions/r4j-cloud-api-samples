from api import cloud_jira_helper, cloud_r4j_helper
from report.log_and_report import write_logging_server_response, write_logging_simple_message
from utilities import cloud_functions


def compare_with_existing_folders_in_jira_cloud(cloud_issue_folders, data_center_tree_folders):
    cloud_tree_issue_folders = []
    cloud_existing_folders = []
    for tree_folder in data_center_tree_folders:
        cloud_issue_folder = [issue_folder for issue_folder in cloud_issue_folders
                              if issue_folder["summary"] == tree_folder["folder_name"]]
        if len(cloud_issue_folder) > 0:
            cloud_tree_issue_folders.append({"issue_key": cloud_issue_folder[0]["issue_key"],
                                             "summary": tree_folder["folder_name"], "level": tree_folder["level"]})
            cloud_issue_folders.remove(cloud_issue_folder[0])
            cloud_existing_folders.append(tree_folder)
    for existing_folder in cloud_existing_folders:
        data_center_tree_folders.remove(existing_folder)
    return cloud_tree_issue_folders


def create_issue_folders_in_cloud(project_key, data_center_tree_folders, dry_run):
    project_id = cloud_jira_helper.get_project_by_project_id_or_key(project_key).json()["id"]
    response = cloud_r4j_helper.get_folder_issue_type()
    folder_issue_type = response.json()["folderIssueType"]
    write_logging_simple_message("Search for existing issue folders in Jira cloud")
    cloud_issue_folders = cloud_functions.get_cloud_issue_folders(project_key, folder_issue_type)
    cloud_tree_issue_folders = \
        compare_with_existing_folders_in_jira_cloud(cloud_issue_folders, data_center_tree_folders)
    if len(data_center_tree_folders) != 0:
        write_logging_simple_message("Cloud issue folders creation has been started")
    else:
        write_logging_simple_message("\tCloud issue folders already created")

    if len(data_center_tree_folders) != 0 and dry_run:
        for index, folder in enumerate(data_center_tree_folders):
            cloud_tree_issue_folders.append(
                {"issue_key": index, "summary": folder["folder_name"], "level": folder["level"]})
            message = f"\tCreated {index} issue folder with the summary: {folder['folder_name']}"
            write_logging_simple_message(message)
        return cloud_tree_issue_folders

    for folder in data_center_tree_folders:
        response = cloud_jira_helper.create_issue(project_id, int(folder_issue_type), folder["folder_name"],
                                                  dry_run=dry_run)
        if response is not None:
            if response.status_code == 201:
                created_issue = response.json()
                cloud_tree_issue_folders.append(
                    {"issue_key": created_issue["key"], "summary": folder["folder_name"], "level": folder["level"]})
                message = f"Created {created_issue['key']} issue folder with the summary: {folder['folder_name']}"
                write_logging_server_response(response, message)
            else:
                message = f"ISSUE CREATION ERROR: Cannot possible to create issue folder with the summary: " \
                          f"{folder['folder_name']} and level: {folder['level']}"
                write_logging_server_response(response, message, True, ConnectionError)
    return cloud_tree_issue_folders


def replace_data_center_folders_like_an_issue_in_jira_cloud(project_key, tree_items_list, dry_run):
    data_center_tree_folders = [folder for folder in tree_items_list if "folder_name" in folder.keys()]
    if len(data_center_tree_folders) != 0:
        cloud_tree_issue_folders = create_issue_folders_in_cloud(project_key, data_center_tree_folders, dry_run)

        # Set folder like an issue
        for folder in cloud_tree_issue_folders:
            for index, item in enumerate(tree_items_list):
                if item["parent"] == folder["summary"] and item["level"] == folder["level"] + 1:
                    tree_items_list[index]["parent"] = folder["issue_key"]
                elif "folder_name" in item.keys() and \
                        item["folder_name"] == folder["summary"] and item["level"] == folder["level"]:
                    tree_items_list[index]["issue_key"] = folder["issue_key"]
                    tree_items_list[index]["summary"] = tree_items_list[index].pop("folder_name")


def create_parents(tree_items_list):
    parents = []
    for data in tree_items_list:
        if {"issue_key": data['parent'], "level": data['level']} not in parents:
            parents.append({"issue_key": data['parent'], "level": data['level']})
    return parents


def create_root_children_on_cloud(project_key, parent, child_list, dry_run):
    response = cloud_r4j_helper.\
                    add_existing_items_to_a_tree_by_parent_id_and_items(project_key, parent_id=parent["issue_key"],
                                                                        items=child_list, dry_run=dry_run)
    if response is not None:
        if response.status_code == 200:
            message = "Created root folder children items in tree cloud"
            write_logging_server_response(response, message)
        else:
            message = "CREATE ROOT TREE ITEMS ERROR: " \
                        "Cannot possible to create root folder children items in tree cloud"
            write_logging_server_response(response, message, True, ConnectionError)


def create_children_items_on_cloud(project_key, parent, child_list, dry_run):
    response = cloud_r4j_helper.\
                    add_existing_items_to_a_tree_by_parent_id_and_items(project_key, jira_issue_key=parent["issue_key"],
                                                                        items=child_list, dry_run=dry_run)
    if response is not None:
        if response.status_code == 200:
            message = f"Created {parent['issue_key']} children items in tree cloud"
            write_logging_server_response(response, message)
        else:
            message = f"CREATE TREE ITEMS ERROR: " \
                        f"Cannot possible to create {parent['issue_key']} children items in tree cloud"
            write_logging_server_response(response, message, True, ConnectionError)


def migrate_data_center_tree_to_cloud(project_key, tree_items_list, dry_run):
    replace_data_center_folders_like_an_issue_in_jira_cloud(project_key, tree_items_list, dry_run)
    parents = create_parents(tree_items_list)  
    height = max([parent["level"] for parent in parents])

    write_logging_simple_message("Tree migrations have been started in jira cloud from the jira data center")
    for level in range(1, height + 1):
        level_parents = [parent for parent in parents if parent["level"] == level]
        for parent in level_parents:
            child_list = [{"jiraIssueKey": child["issue_key"], "position": child["position"]}
                          for child in tree_items_list if child["parent"] == parent['issue_key']]
            if parent["issue_key"] == -1:
                create_root_children_on_cloud(project_key, parent, child_list, dry_run)
            else:
                create_children_items_on_cloud(project_key, parent, child_list, dry_run)
