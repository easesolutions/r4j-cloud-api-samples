from report.log_and_report import initialize_logging, write_logging_simple_message
from utilities import cloud_functions

LOG_FILE = "clean_tree"


def run_clean(project_key):
    initialize_logging(LOG_FILE)

    # Delete tree items on project
    write_logging_simple_message(f"Deleting tree items on project: {project_key}")
    cloud_functions.delete_tree_items_by_project_key(project_key)
