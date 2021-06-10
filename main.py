import sys
from github import Github, BadCredentialsException
from github.GithubException import UnknownObjectException

args = sys.argv[1:]
source = None

createCommand = "create"
deleteCommand = "delete"
tokenCommand = "--token"
namesCommand = "--names"
valuesCommand = "--values"
teamCommand = "--team"
interactiveCommand = "--interactive"

noTokenMessage = "Please provide a valid GitHub PAT using --token <PAT>."
invalidTokenMessage = "The token you provided is invalid."
noActionMessage = "You must specify an action, either create or delete."
noNamesMessage = "You must specify the name(s) of the secrets to be modified."
noTeamMessage = "Invalid team name provided."
invalidNamesAndSecretsMessage = "Secret names and secret values lists are not the same length. This may be due to an " \
                                "invalid input or a secret that contains a comma. Secrets with comma(s) are currently" \
                                " not supported."


class UserInput:
    def __init__(self, token, action, secret_names, secret_values, target_team_name, interactive):
        self.token = token
        self.action = action
        self.secret_names = secret_names
        self.secret_values = secret_values
        self.target_team_name = target_team_name
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


def validate_action(candidate_action, create_command, delete_command, secret_names, secret_values):
    if delete_command.lower() in candidate_action.lower():
        return delete_command
    if create_command.lower() in candidate_action.lower():
        if len(secret_names) != len(secret_values):
            raise ValueError(invalidNamesAndSecretsMessage)
        return create_command
    raise ValueError(f"{candidate_action} is not a valid action! Please enter \"{create_command}\" or" \
                     f"\"{delete_command}\" as the first argument")


def get_input_from_user():
    token = input("Github PAT: ")
    action = input("Desired action to be performed (create/delete): ")
    secret_names = input("Comma separated list of secret names: ")
    if action.lower() != deleteCommand:
        secret_values = input("Comma separated list of secret values: ")
        validate_action(action, createCommand, deleteCommand, secret_names, secret_values)
    if "y" in input("Limit tool to a github team? (y/n)").lower():
        target_team_name = input("Team name: ")
    else:
        target_team_name = ""
    interactive = "y" in input("Prompt for approval before applying action to each repo? (y/n)").lower()
    return UserInput(token, action, secret_names, secret_values, target_team_name, interactive)


def get_input_from_cli():
    token = get_mandatory_value_from_input(args, tokenCommand, noTokenMessage)
    secret_names = get_mandatory_value_from_input(args, namesCommand, noNamesMessage).split(',')
    secret_values = get_optional_value_from_input(args, valuesCommand).split(',')
    target_team_name = get_optional_value_from_input(args, teamCommand)
    interactive = interactiveCommand in args
    action = validate_action(args[0], createCommand, deleteCommand, secret_names, secret_values)
    return UserInput(token, action, secret_names, secret_values, target_team_name, interactive)


if __name__ == "__main__":
    if len(args) == 0:
        inp = get_input_from_user()
    else:
        inp = get_input_from_cli()

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
        for i in range(len(inp.secret_names)):
            if not inp.interactive or apply_action(repo.name):
                try:
                    if inp.action == createCommand:
                        repo.create_secret(inp.secret_names[i], inp.secret_values[i])
                        print(f"Secret \"{inp.secret_names[i]}\" added to {repo.name}")
                    if inp.action == deleteCommand:
                        repo.delete_secret(inp.secret_names[i])
                        print(f"Secret \"{inp.secret_names[i]}\" removed from {repo.name}")
                except UnknownObjectException:
                    print(f"The provided token does not have permission to manage {repo.name}, it is being skipped")
