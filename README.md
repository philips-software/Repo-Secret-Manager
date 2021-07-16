# Github Secret Manager
This script is used to automate creating, updating, and deleting repository level [GitHub secrets](https://docs.github.com/en/actions/reference/encrypted-secrets) for repos belonging to a user or a team, leveraging GitHub's existing encrypted storage. 

Currently, GitHub does not support storing secrets at the team level, only at the repository or organization level. This is inconvenient in case a team manages many repositories, as the secrets would otherwise need to be manually added to each repo or exposed to the entire organization.

## Dependencies
Python >= 3.5

[PyGithub](https://github.com/PyGithub/PyGithub) >= 1.55

## Parameters
**If no command-line arguments are provided, the tool will prompt for each value**
| Command | Description | Mandatory? |
| ---- | ---- | ---- |
|"create", "update", or "delete" | The action to be performed. If `create` is selected and the secret(s) already exist for a repo, they will not be updated. If `update` is selected, existing secrets will be updated to the new value. If a repository is missing a secret, it will be added. add If `delete` is selected and the secret does not exist it will not cause issues | Yes, as the first argument |
|--token| A [GitHub PAT](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) with permission to manage secrets | Yes |
|--names| A comma-separated list of secret name(s) | Yes |
|--values| A comma-separated list of secret value(s) | If "create" is selected |
|--team|If a team name is given, the secret will be added to all repositories in that team. If no team is specified, the secret will be added to all of the user's repositories|No|
|--interactive | If this parameter is provided, the tool will prompt before applying the action to each repository, allowing you to limit where the secrets go. | No |

Add or Update Secret(s)
```
create --names <comma seperated list of secret names> --values <comma seperated list of secret values> --token <github PAT>
e.g. create --names BLACKDUCK_TOKEN,PACKAGE_FEED_TOKEN --values ABC,XYZ --token 12345 --team iX
e.g. update --names BLACKDUCK_TOKEN --values ABC --token 12345
```

Delete Secret(s)
```
delete --names <comma seperated list of secret names> --token <github PAT>
e.g. delete --names BLACKDUCK_TOKEN,PACKAGE_FEED_TOKEN --token 12345
e.g. delete --names BLACKDUCK_TOKEN --token 12345 --team iX
```

## Github Workflow
In addition to running locally, this script can be run through Github Actions. To do this, store the secret(s) you want to deploy as a repo secret and reference them from a workflow calling the tool. This will propagate the secret to other repositories without exposing it. 

Example
``` YAML
name: Manage Secrets
on: 
    workflow_dispath:
jobs:
  Manage-Secrets:
    runs-on: [ubuntu-latest]
    env:
       SECRET_NAMES: BLACKDUCK_TOKEN
       SECRET_VALUES: ${{ secrets.BLACKDUCK_TOKEN }}
       TEAM_NAME: iX
  
    steps:
    - uses: actions/checkout@v2

    - name: Install dependencies
      run: pip install -r requirements.txt

    - name: Run manage_secrets script
      run: python3 ./main.py create --names ${{ env.SECRET_NAMES }} --values ${{ env.SECRET_VALUES }}  --token ${{ secrets.IX_ACTIONS_PAT }} --team ${{ env.TEAM_NAME }}  

```
