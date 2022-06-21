from utilities import cloud_verifications, read_and_process_tree_items, \
    migrate_data_center_tree_to_cloud, sort_deep_order_tree
from api import r4j_helper
from report.log_and_report import generate_expected_tree_html, initialize_logging, write_logging_simple_message, \
    open_report_html, raise_an_error

LOG_FILE = "migration"


def run_migration(project_key, dry_run):
    initialize_logging(LOG_FILE)

    # Jira Cloud verifications
    write_logging_simple_message("Jira Cloud verifications started")
    flag_cloud_verifications = cloud_verifications.run_project_cloud_verifications(project_key)
    if flag_cloud_verifications:
        write_logging_simple_message("All verifications successfully")

    # Download the tree from R4JDC
    write_logging_simple_message("Download the tree from R4JDC")
    data_center_tree = r4j_helper.get_complete_tree_structure_by_project_key(project_key)
    tree_items_list = []
    read_and_process_tree_items(data_center_tree, tree_items_list)

    # Check if all issues are found on the Jira Cloud instance
    write_logging_simple_message("Check if all issues are found on the Jira Cloud instance")
    verify_issues_in_cloud = cloud_verifications.verify_all_data_center_tree_issues_in_cloud_instance(tree_items_list)
    if not verify_issues_in_cloud:
        message = "CLOUD ISSUES ERROR: Tree data center issues are not found on the Jira Cloud or not are the same"
        raise_an_error(message, AssertionError)
    else:
        write_logging_simple_message("Tree data center issues are found on the Jira Cloud")

    # Create the Folder issues in the Jira Cloud instance and create tree in R4J Cloud
    if dry_run:
        message = "\nDRY RUN ON => " \
                  "The issue folder creation and tree migration only show log steps and console messages (NO MIGRATE)\n"
        write_logging_simple_message(message)
    write_logging_simple_message("All verifications OK: Migrating tree to Jira Cloud instance")
    migrate_data_center_tree_to_cloud(project_key, tree_items_list, dry_run)

    # Generate report HTML with expected tree structure
    if dry_run:
        deep_order_tree = sort_deep_order_tree(tree_items_list)
        write_logging_simple_message("Expected tree HTML generating")
        generate_expected_tree_html(deep_order_tree, project_key)
        open_report_html()
