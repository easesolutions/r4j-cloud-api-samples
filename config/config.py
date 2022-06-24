import yaml
from pathlib import Path

YML_ENV = Path(__file__).parents[1]/'config.yaml'


def read_yaml_file(file):
    with file.open(mode='r') as file:
        return yaml.load(file, Loader=yaml.FullLoader)


class CloudSettings:

    def __init__(self, env_yml_file):
        env_obj = read_yaml_file(env_yml_file)
        env_settings = env_obj['settings']['cloud_env']
        self.application_url = env_settings['application_url']
        if 'r4j_api_url' in env_settings:
            self.r4j_api_url = env_settings['r4j_api_url'] 
        else:
            self.r4j_api_url = 'https://eu.r4j-cloud.easesolutions.com'
        self.username = env_settings['username']
        self.jira_api_token = env_settings['jira_api_token']
        self.r4j_api_token = env_settings['r4j_api_token']


class DataCenterSettings:

    def __init__(self, env_yml_file):
        env_obj = read_yaml_file(env_yml_file)
        env_settings = env_obj['settings']['data_center_env']
        self.application_url = env_settings['application_url']
        if 'pat' in env_settings and env_settings['pat'] != '' and env_settings['pat'] is not None:
            self.pat = env_settings['pat']
        else:
            self.username = env_settings['username']
            self.password = env_settings['password']        
            self.pat = ''


CLOUD_ENV = CloudSettings(env_yml_file=YML_ENV)
DC_ENV = DataCenterSettings(env_yml_file=YML_ENV)
