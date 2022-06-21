ROOT_ITEM = {'issue_key': -1, 'level': 1}


def read_and_process_tree_items(data_input, _data_output, level=1):
    root = data_input["id"]

    for folder in data_input["folders"]:
        data_folders = {"id": folder["name"], "folders": folder["folders"], "issues": folder["issues"]}
        _data_output.append({"parent": root, "folder_name": folder["name"], "position": folder["absolutePosition"],
                             "level": level, "folder": True})
        read_and_process_tree_items(data_folders, _data_output, level + 1)

    for issue in data_input["issues"]:
        if "childReqs" in issue.keys() and len(issue["childReqs"]["childReq"]) != 0:
            data_issue = {"id": issue["key"], "folders": [], "issues": issue["childReqs"]["childReq"]}
            _data_output.append({"parent": root, "issue_key": issue["key"], "summary": issue["summary"],
                                 "position": issue["absolutePosition"], "level": level})
            read_and_process_tree_items(data_issue, _data_output, level + 1)
        else:
            _data_output.append({"parent": root, "issue_key": issue["key"], "summary": issue["summary"],
                                 "position": issue["absolutePosition"], "level": level})


def sort_children_items(parent, tree_items_list):
    sorted_list = []
    children_list = [item for item in tree_items_list
                     if item["parent"] == parent["issue_key"] and item["level"] == parent["level"]]
    children_list_positions = [child["position"] for child in children_list]
    for child_position in sorted(children_list_positions):
        for child in children_list:
            if child["position"] == child_position:
                sorted_list.append(child)
                break
    return sorted_list


def deep_order_tree(child_list, tree_items_list, deep_tree_items_list):
    for child in child_list:
        deep_tree_items_list.append(child)
        children_list = sort_children_items(
            {"issue_key": child['issue_key'], "level": child['level']+1}, tree_items_list)
        deep_order_tree(children_list, tree_items_list, deep_tree_items_list)


def sort_deep_order_tree(tree_items_list):
    deep_tree_items_list = []
    root = {'issue_key': -1, 'level': 1}
    root_children = sort_children_items(root, tree_items_list)
    deep_order_tree(root_children, tree_items_list, deep_tree_items_list)
    return deep_tree_items_list
