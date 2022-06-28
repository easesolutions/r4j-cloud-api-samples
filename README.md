# Migrating an R4J Tree from Data Center to the Cloud example
This repository exemplifies how to migrate the tree structure from a Jira Server/Data Center to a Jira Cloud instance using Python and the R4J APIs. It assumes that the Jira issues were already migrated to the Cloud using the [Jira Cloud Migration Assistant](https://support.atlassian.com/migration/docs/use-the-jira-cloud-migration-assistant-to-migrate/) or [Jira Site import](https://support.atlassian.com/migration/docs/use-jira-site-import-to-migrate-from-server-to-cloud/). The script will just copy the Tree structure. It won't create any issues in the Jira Cloud besides the R4J folders.

# Table of Contents
  - [Pre-requisites](#pre-requisites)
  - [Setup the development machine](#setup-the-development-machine)
  - [Preparing to run the migration script](#preparing-to-run-the-migration-script)
  - [How to run the migration script](#how-to-run-the-migration-script)
    - [Optional: Clean up the tree](#optional-clean-up-the-tree)
    - [Migrate a Server or Data Center R4J tree to the Cloud](#migrate-a-server-or-data-center-r4j-tree-to-the-cloud)
- [Known Issues and Possible Improvements](#known-issues-and-possible-improvements)
- [Disclaimer](#disclaimer)


## Pre-requisites
* A Jira Server or Data Center instance with R4J 4.9 installed and a project containing an R4J Tree Structure
* A Jira Cloud instance with R4J installed
* A project migrated to the Cloud using [Jira Cloud Migration Assistant](https://support.atlassian.com/migration/docs/use-the-jira-cloud-migration-assistant-to-migrate/) or [Jira Site import](https://support.atlassian.com/migration/docs/use-jira-site-import-to-migrate-from-server-to-cloud/) and activated in R4J for both instances.
* The R4J Folder issue type is correctly configured in the Cloud instance. (See [R4J Folder configurations](https://easesolutions.atlassian.net/wiki/spaces/R4JC/pages/2114388135/Configuration#Folder-Issue-Type) )
* The R4J Folder issue type is [associated with the project(s)](https://support.atlassian.com/jira-cloud-administration/docs/associate-issue-types-with-projects/) to be migrated

## Setup the development machine
1. Install Python 3.8.9 or greater [Python official documentation](https://www.python.org/downloads/release/python-389/)
2. Clone the repository. [How to clone a repository](https://support.atlassian.com/bitbucket-cloud/docs/clone-a-repository/)
3. Install the Python dependencies 
```
    pip install -r requirements.txt
```

## Preparing to run the migration script
The script relies on a set of parameters to run. Before running the script you need to set these up in the *config.yaml* file. This file is not committed to this repository.

Your *config.yaml* file should look something like this:

    settings:
      cloud_env:
        # Cloud
        application_url: https://your-domain.atlassian.net
        username: cloud-your-username
        jira_api_token:  JIRAAPITOKEN
        r4j_api_token: R4JCAPITOKEN
        
      data_center_env:
        # Data Center
        application_url: https://www.mywebsite.com/jira/
        username: data-center-username
        password: data-center-password
        # pat: data-center-personal-access-token

### Cloud instance configurations
  1. **application_url**: URL of your Cloud instance.
  2. **username**: Jira Cloud user with WRITE rights to the project being migrated.
  3. **jira_api_token**: Jira API Token to access the Jira Cloud instance generated for the above user. https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
  4. **r4j_api_token**: R4JC API token to access the R4J Cloud endpoints generated for the above user. https://easesolutions.atlassian.net/wiki/spaces/R4JC/pages/2250473484/API+Tokens
### Server/Data Center configurations
  1. **application_url**: URL to the Jira Server or Data Center instance.
  2. **username**: User with READ access to the projects you want to migrate.
  3. **password**: Password for the user.
  4. **pat**: Alternatively to providing the username and password, you can provide a [Personal Access Token (PAT)](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html)

## How to run the migration script 
### Optional: Clean up the tree
The script assumes that the R4JC project tree is empty in the Cloud instance. If this is not the case, you can run the below command to empty it. It won't delete any Jira issues, but simply empty the tree.
**WARNING**: If you run the below command, the project tree will be empty. This cannot be reversed.
```
python cloud_clean_tree.py {project_key}
```
Where *project_key* is the key to the Jira project you want to clean up. 

### Migrate a Server or Data Center R4J tree to the Cloud
To finally migrate a tree to the Cloud just run the following script:
```
python migrate.py {project_key} {dry_run: optional}
```
Setting *dry_run* to *True* allows you to verify if the migration is possible without actually creating any items in the Jira or R4J Cloud instance. After running it on dry run mode, an HTML file will open in your default browser showing the expected tree. Example:
```
python migrate.py {project_key} True
```
If you don't specify the *dry_run* command-line parameter, it assumes to be false.

# Known Issues and Possible Improvements
* The script doesn't migrate folder attachments
* The script doesn't check for user rights before running. If the users associated with the tokens cannot perform the needed operations, the script will fail leaving a potentially uncomplete R4J Tree in the Cloud instance.
* If the below error is encountered in the logs, check if there is an issue security configuration in the project. If yes, add the user performing the migration to the issue security level.
```  
'error': 'Issue does not exist or you do not have permission to see it.'  
```

# Disclaimer

THIS REPOSITORY IS PROVIDED BY THE CONTRIBUTORS “AS IS”. IT IS NOT AN OFFICIAL MIGRATION PROCEDURE SUPPORTED BY EASE SOLUTIONS OR ITS AFFILIATES. ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.