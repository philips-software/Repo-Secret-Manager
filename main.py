import sys
import json
import requests
from github import Github, BadCredentialsException
from github.GithubException import UnknownObjectException

from base64 import b64encode
from nacl import encoding, public

args = sys.argv[1:]
source = None

createCommand = "create"
deleteCommand = "delete"
updateCommand = "update"
tokenCommand = "--token"
namesCommand = "--names"
valuesCommand = "--values"
teamCommand = "--team"
repoCommand = "--repo"
dependabotSecretsSyncOption = "--dependabotsecretssync"
repositoryOwner = "--repoowner"
interactiveCommand = "--interactive"
defaultRepoOwnerName = "org-name"

noTokenMessage = "Please provide a valid GitHub PAT using --token <PAT>."
invalidTokenMessage = "The token you provided is invalid."
noActionMessage = "You must specify an action, either create or delete."
noNamesMessage = "You must specify the name(s) of the secrets to be modified."
noTeamMessage = "Invalid team name provided."
invalidNamesAndSecretsMessage = "Secret names and secret values lists are not the same length. This may be due to an " \
                                "invalid input or a secret that contains a comma. Secrets with comma(s) are currently" \
                                " not supported."
invalidRepoOwnerMessage = "Invalid Repository Owner name, please pass the value to sync dependabot secrets!"


class UserInput:
    def __init__(self, token, action, secret_names, secret_values, target_team_name, target_repo_name, dependabotSecretsSync, repoOwner,  interactive):
        self.token = token
        self.action = action
        self.secret_names = secret_names
        self.secret_values = secret_values
        self.target_team_name = target_team_name
        self.target_repo_name = target_repo_name
        self.dependabotSecretsSync = dependabotSecretsSync
        self.repoOwner = repoOwner
        self.interactive = interactive


def get_mandatory_value_from_input(arg_list, label, error_message):
    if label in arg_list:
        return get_element_after_value(arg_list, label, error_message)
    else:
        raise ValueError(error_message)


def get_optional_value_from_input(arg_list, label):
    if label in arg_list:
        return get_element_after_value(arg_list, label,
                                       f"{label} was included in the input but no value was provided")
    else:
        return ""


def get_element_after_value(arg_list, value, error_message):
    try:
        result = arg_list[arg_list.index(value) + 1]
        if not does_string_start_with_two_dashes(result):
            return result
    except IndexError:
        pass
    raise ValueError(error_message)


def does_string_start_with_two_dashes(str1):
    if len(str1) < 2:
        return False
    else:
        return str1[0:2] == "--"


def get_github_user(token, message):
    try:
        g = Github(token)
        print(f"Logged in as {g.get_user().name}")
        return g
    except BadCredentialsException:
        raise ValueError(message)


def apply_action(repo_name):
    return "y" in input(f"Apply action to {repo_name}? (y/n) ").lower()


def validate_action(candidate_action, create_command, update_command, delete_command, secret_names, secret_values):
    if delete_command.lower() in candidate_action.lower():
        return delete_command
    if update_command.lower() in candidate_action.lower():
        return update_command
    if create_command.lower() in candidate_action.lower():
        if len(secret_names) != len(secret_values):
            raise ValueError(invalidNamesAndSecretsMessage)
        return create_command
    raise ValueError(f"{candidate_action} is not a valid action! Please enter \"{create_command}\",\"{update_command}\""
                     + f"\"or {delete_command}\" as the first argument")


def get_input_from_user():
    token = input("Github PAT: ")
    action = input("Desired action to be performed (create/delete): ")
    secret_names = input("Comma separated list of secret names: ").split(',')
    if action.lower() != deleteCommand:
        secret_values = input("Comma separated list of secret values: ").split(',')
        validate_action(action, createCommand, updateCommand, deleteCommand, secret_names, secret_values)
    if "y" in input("Limit tool to a github team? (y/n)").lower():
        target_team_name = input("Team name: ")
    else:
        target_team_name = ""
    if "y" in input("Limit tool to a specific repo? (y/n)").lower():
        target_repo_name = input("Repo name: ")
    else:
        target_repo_name = ""
    interactive = "y" in input("Prompt for approval before applying action to each repo? (y/n)").lower()
    return UserInput(token, action, secret_names, secret_values, target_team_name, target_repo_name, interactive)


def get_input_from_cli():
    token = get_mandatory_value_from_input(args, tokenCommand, noTokenMessage)
    secret_names = get_mandatory_value_from_input(args, namesCommand, noNamesMessage).split(',')
    secret_values = get_optional_value_from_input(args, valuesCommand).split(',')
    target_team_name = get_optional_value_from_input(args, teamCommand)
    target_repo_name = get_optional_value_from_input(args, repoCommand)
    dependabotSecretsSync = get_optional_value_from_input(args, dependabotSecretsSyncOption)
    repoOwner = get_optional_value_from_input(args, repositoryOwner)
    interactive = interactiveCommand in args
    action = validate_action(args[0], createCommand, updateCommand, deleteCommand, secret_names, secret_values)
    return UserInput(token, action, secret_names, secret_values, target_team_name, target_repo_name, dependabotSecretsSync, repoOwner, interactive)


def flatten_secrets_dict(dict_of_secrets):
    list_of_secrets = []
    for secret in dict_of_secrets:
        list_of_secrets.append(secret["name"])
    return list_of_secrets

def get_repo_public_key(token, repo_owner, repo_name):
   
   query_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dependabot/secrets/public-key"
   headers = {'Authorization': f'token {token}'}
   r = requests.get(query_url, headers=headers)
   response = r.json()
   return response["key_id"], response["key"]

def encrypt(public_key: str, secret_value: str) -> str:
  """Encrypt a Unicode string using the public key."""
  public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
  sealed_box = public.SealedBox(public_key)
  encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
  return b64encode(encrypted).decode("utf-8")


def add_secret(token, target_repository, secret_name, secret_value):
    repo_full_name = target_repository.full_name
    repo_name = target_repository.name
    query_url = f"https://api.github.com/repos/{repo_full_name}/actions/secrets"
    headers = {'Authorization': f'token {token}'}
    r = requests.get(query_url, headers=headers)
    response = r.json()
    try:
      secret_names = flatten_secrets_dict(response["secrets"])
    except: 
      secret_names = []
    if secret_name not in secret_names:
        print(f"Secret \"{secret_name}\" added to {repo_name}")
        target_repository.create_secret(secret_name, secret_value)
    else:
        print(f"Secret \"{secret_name}\" already exists in {repo_name}")

def add_dependabot_secret(token, target_repository, secret_name, secret_value, repoOwner):
    repo_name = target_repository.name
    repo_owner = repoOwner
    key_id, key = get_repo_public_key(token, repo_owner, repo_name)
    query_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dependabot/secrets"
    headers = {'Authorization': f'token {token}'}
    r = requests.get(query_url, headers=headers)
    response = r.json()
    try:
      secret_names = flatten_secrets_dict(response["secrets"])
    except: 
      secret_names = []
    if secret_name not in secret_names:
        # put call add repo secrets to dependabot secrets
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dependabot/secrets/{secret_name}"

        data = {
            "encrypted_value": encrypt(key, secret_value),
            "key_id": key_id
        }
        response = requests.put(url, headers=headers, data=json.dumps(data))
        print(f"Response Code: {response.status_code}")
        if response.status_code == 201:
            print(f"dependabot Secret \"{secret_name}\" added to {repo_name}")
        else:
            print(f"dependabot Secret \"{secret_name}\" could NOT be added to {repo_name}")
    else:
        print(f"dependabot Secret \"{secret_name}\" already exists in {repo_name}")

def update_dependabot_secret(token, target_repository, secret_name, secret_value, repoOwner):
    repo_name = target_repository.name
    repo_owner = repoOwner
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json'
    }

    key_id, key = get_repo_public_key(token, repo_owner, repo_name)
    put_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dependabot/secrets/{secret_name}"
    encrypted_value = encrypt(key, secret_value)
    body = {"encrypted_value": encrypted_value, "key_id": key_id}
    put_resp = requests.put(put_url, headers=headers, json=body)
    print(f"Create (update) Response Code: {put_resp.status_code}")
    if put_resp.status_code in (201, 204):
        print(f"dependabot Secret \"{secret_name}\" updated in {repo_name}")
    else:
        print(f"dependabot Secret \"{secret_name}\" could NOT be updated in {repo_name}. Response: {put_resp.text}")

def delete_dependabot_secret(token, target_repository, secret_name, repoOwner):
    repo_name = target_repository.name
    repo_owner = repoOwner
    headers = {'Authorization': f'token {token}'}
    # put call add repo secrets to dependabot secrets
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dependabot/secrets/{secret_name}"
    response = requests.delete(url, headers=headers)
    print(f"Response Code: {response.status_code}")
    if response.status_code == 204:
        print(f"dependabot Secret \"{secret_name}\" deleted from {repo_name}")
    else:
        print(f"dependabot Secret \"{secret_name}\" could NOT be deleted from {repo_name}")

if __name__ == "__main__":
    if len(args) == 0:
        inp = get_input_from_user()
    else:
        inp = get_input_from_cli()
        print(inp.repoOwner)

    g = get_github_user(inp.token, invalidTokenMessage)

    if inp.target_team_name != "":
        for team in g.get_user().get_teams():  # There is no method to get a team by name
            if team.name == inp.target_team_name:
                source = team
        if source is None:
            raise ValueError(noTeamMessage)
    else:
        source = g.get_user()

    for repo in source.get_repos():
        if(inp.target_repo_name != "" and repo.name != inp.target_repo_name):
            continue

        for i in range(len(inp.secret_names)):
            if len(inp.dependabotSecretsSync) == 0 or inp.dependabotSecretsSync.lower() == "yes" or inp.dependabotSecretsSync.lower() == '':
                if not inp.interactive or apply_action(repo.name):
                    try:
                        if inp.action == createCommand:
                            add_secret(inp.token, repo, inp.secret_names[i], inp.secret_values[i])
                            if not inp.repoOwner == defaultRepoOwnerName:
                                add_dependabot_secret(inp.token, repo, inp.secret_names[i], inp.secret_values[i], inp.repoOwner)
                            else:
                                raise ValueError(invalidRepoOwnerMessage)
                        if inp.action == updateCommand:
                            c = repo.get_contributors()
                            repo.create_secret(inp.secret_names[i], inp.secret_values[i])
                            print(f"Secret \"{inp.secret_names[i]}\" updated for {repo.name}")
                            if not inp.repoOwner == defaultRepoOwnerName:
                                update_dependabot_secret(inp.token, repo, inp.secret_names[i], inp.secret_values[i], inp.repoOwner)
                            else:
                                raise ValueError(invalidRepoOwnerMessage)
                        if inp.action == deleteCommand:
                            repo.delete_secret(inp.secret_names[i])
                            print(f"Secret \"{inp.secret_names[i]}\" removed from {repo.name}")
                            if not inp.repoOwner == defaultRepoOwnerName:
                                delete_dependabot_secret(inp.token, repo, inp.secret_names[i], inp.repoOwner)
                            else:
                                raise ValueError(invalidRepoOwnerMessage)
                    except UnknownObjectException:
                        print(f"The provided token does not have permission to manage {repo.name}, it is being skipped")
            else:
                if not inp.interactive or apply_action(repo.name):
                    try:
                        if inp.action == createCommand:
                            add_secret(inp.token, repo, inp.secret_names[i], inp.secret_values[i])
                        if inp.action == updateCommand:
                            c = repo.get_contributors()
                            repo.create_secret(inp.secret_names[i], inp.secret_values[i])
                            print(f"Secret \"{inp.secret_names[i]}\" updated for {repo.name}")
                        if inp.action == deleteCommand:
                            repo.delete_secret(inp.secret_names[i])
                            print(f"Secret \"{inp.secret_names[i]}\" removed from {repo.name}")
                    except UnknownObjectException:
                        print(f"The provided token does not have permission to manage {repo.name}, it is being skipped")
