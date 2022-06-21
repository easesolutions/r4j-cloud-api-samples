import logging
import webbrowser
import os

UL_OPEM = "<ul>"
UL_CLOSE = "</ul>"
LI_OPEN = "<li>"
LI_CLOSE = "</li>"
OPEN_ROOT = '<a id="root" class="label">'
OPEN_A = '<a class="label"><icon></icon><span class="issue fa-check-square"></span>'
OPEN_A_FOLDER = '<a class="label"><icon></icon><span class="folder fa-folder"></span>'
CLOSE_A = '</a>'
FONT_AWESOME = '<link rel="stylesheet" href="' \
               'https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css">'
STYLESHEET = '<link rel="stylesheet" href="style.css">'
SCRIPT = '<script src="main.js"></script>'
HEAD = '<head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" ' \
       'content="width=device-width, initial-scale=1.0"><title>Expeted Tree</title></head>'
HEADER = '<header><h1>R4J Data Center Migration to R4J Cloud</h1><h2>Expected tree</h2></header>'
NOTE = '<p><strong>NOTE: Folders that have not been created previously to the execution of the script with ' \
       'dry_run enabled will have a numeric value instead of an issue_key.</strong></p>'


def initialize_logging(file_name):
    logging.basicConfig(format='%(asctime)s: %(levelname)s => %(message)s', filename=f'./report/{file_name}.log',
                        level=logging.DEBUG)


def write_logging_server_response(response, message, error=False, type_error=None):
    path_url = response.request.path_url
    jwt_string = '?jwt' if '?jwt' in path_url else '&jwt'
    if jwt_string in path_url:
        method_status_endpoint = f"\t\t{response.request.method} {path_url[:path_url.index(jwt_string)]} " \
                             f"=> Status code: {response.status_code}"
    else:
        method_status_endpoint = f"\t\t{response.request.method} {path_url} => Status code: {response.status_code}"
    response_content = f"\t\tResponse content: {response.json()}" \
        if response.status_code != 400 else f"\t\t{response.content}"
    if not error:
        print(f"\t{message}")
        logging.info(f"\t{message}")
        logging.info(method_status_endpoint)
        if response.request.method == "POST":
            logging.info(f"\t\tRequest body: {response.request.body}")
        logging.info(response_content)
    else:
        logging.error(f"\t{message}")
        logging.error(method_status_endpoint)
        logging.error(response_content)
        raise_an_error(message, type_error)


def write_logging_dry_run_message(message, request_body):
    print(f"\t{message}")
    logging.info(f"\t{message}")
    logging.info(f"\t\tRequest body: {request_body}")


def write_logging_simple_message(message):
    print(message)
    logging.info(message)


def create_item_on_current_level(data, a_label):
    if "summary" in data.keys():
        report_html = f"{LI_CLOSE}{LI_OPEN}{a_label} {data['issue_key']} - {data['summary']}{CLOSE_A}"
    else:
        report_html = f"{LI_CLOSE}{LI_OPEN}{a_label} {data['issue_key']}{CLOSE_A}"
    return report_html


def create_item_on_next_level(data, a_label):
    if "summary" in data.keys():
        report_html = f"{UL_OPEM}{LI_OPEN}{a_label} {data['issue_key']} - {data['summary']}{CLOSE_A}"
    else:
        report_html = f"{UL_OPEM}{LI_OPEN}{a_label} {data['issue_key']}{CLOSE_A}"
    return report_html


def create_item_on_previous_level(data, a_label, level_difference):
    close_level = f"{LI_CLOSE}{UL_CLOSE}" * level_difference
    if "summary" in data.keys():
        report_html = f"{close_level}{LI_OPEN}{a_label} {data['issue_key']} - {data['summary']}{CLOSE_A}"
    else:
        report_html = f"{close_level}{LI_OPEN}{a_label} {data['issue_key']}{CLOSE_A}"
    return report_html


def generate_expected_tree_html(issue_process_list, project_key):
    report_html = f"<html><body>{HEAD}{HEADER}{NOTE}{UL_OPEM}{LI_OPEN}{OPEN_ROOT}{project_key}{CLOSE_A}"
    current_level = 0
    final_level = 0
    for data in issue_process_list:
        a_label = OPEN_A_FOLDER if "folder" in data.keys() else OPEN_A
        if data["level"] == current_level:
            report_html += create_item_on_current_level(data, a_label)
        if data['level'] > current_level:
            report_html += create_item_on_next_level(data, a_label)
        if data['level'] < current_level:
            level_difference = (current_level - data['level'])
            report_html += create_item_on_previous_level(data, a_label, level_difference)
        current_level = data["level"]
        final_level = current_level

    repeat = final_level + 1
    report_html += f"{LI_CLOSE}{UL_CLOSE}" * repeat

    html = report_html + f"{SCRIPT}{STYLESHEET}{FONT_AWESOME}</body></html>"

    hs = open("./report/expected_tree.html", 'w')
    hs.write(html)


def open_report_html():
    simp_path = './report/expected_tree.html'
    abs_path = os.path.abspath(simp_path)
    webbrowser.open(abs_path)


def raise_an_error(message, type_error):
    try:
        raise type_error(message)
    except type_error as err:
        print(f"\n{err}")
        print(type(err))
        raise SystemExit()
