from rich.console import Console
from models import User, Project
from ui import console
from api import API, api
from utils import get_token, NotLoggedIn, NotAdmin


def create_project(*args, console: Console = console, api: API = api) -> None:

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    # input
    project_name = str(input("Project name: "))
    if project_name == "":
        console.print("\nYou must enter a project name!", style="danger")
        return

    project_description = str(input("\nProject description: "))

    project = Project(name=project_name, description=project_description)

    rc = api.post_project(project, token)

    if rc == 1:
        console.print("\nCould not create project\n", style="danger")
        return
    if rc == 2:
        console.print("\nProject with this name already exists\n", style="danger")
        return

    console.print("\nProject created successfully!\n", style="success")
    console.print(
        f"\nStart adding members with 'project members add {project.name}', or add tasks with 'project tasks add {project.name}'.\n",
        style="warning",
    )


def show_project(
    *project_name: str, console: Console = console, api: API = api
) -> None:
    """Get project data from API

    Args:
        *project_name(str): words that make up the project name

    Raises:
        NotLoggedIn: invalid token
    """

    # join project name into a single string
    project_name = " ".join(project_name)

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    if project_name == "":
        # console.print(
        #     "You have to enter the name of the project to show\n", style="warning"
        # )
        projects = api.get_all_projects(token)
        if type(projects) is int:
            console.print(
                f"Could not retrieve list of projects (HTTP Error {projects})\n",
                style="danger",
            )
        else:
            console.print(projects)
            console.print()  # add space
        return

    project = api.get_project(token, project_name)

    if type(project) is int:
        if project == 404:
            console.print("Could not find project\n", style="danger")
        elif project == 403:
            console.print("You are not a member of this project\n", style="danger")
        else:
            console.print(
                f"Something went wrong and could not show project (HTTP error {project})\n",
                style="danger",
            )
    else:
        print_project(project)


def print_project(project_data: Project) -> None:

    # todo add proper functionality
    console.print(project_data.model_dump())
    console.print()


def edit_project(
    *project_name: str, console: Console = console, api: API = api
) -> None:

    # join project name into a single string
    project_name = " ".join(project_name)

    if project_name == "":
        console.print(
            "You have to enter the name of the project to edit\n", style="warning"
        )
        return

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    # get latest data
    project = api.get_project(token, project_name)

    if project is None:
        console.print("Could not find project\n", style="danger")

    # input
    project_description = str(input(f"Description [{project.description}]: "))
    if project_description == "":
        console.print("\nNothing changed1!\n", style="success")
        return

    project.description = project_description

    try:
        rc = api.put_project(token, project_name, project)
    except NotAdmin:
        console.print(
            "\nYou need to be the owner or an admin to edit this project!\n",
            style="danger",
        )

    if rc == 200:
        console.print("\nProject updated successfully!\n", style="success")
    elif (
        rc == 400
    ):  # only possible with a modified client, thought to include this anyway
        console.print("\nYou cannot change the project's name!\n", style="danger")
    else:
        console.print(
            f"\nSomething went wrong and could not update the project (HTTP Error {rc})\n",
            style="danger",
        )


def delete_project(
    *project_name: str, console: Console = console, api: API = api
) -> None:

    # join project name into a single string
    project_name = " ".join(project_name)

    if project_name == "":
        console.print(
            "You have to enter the name of the project to delete\n", style="warning"
        )
        return

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    # verification
    console.print(
        f"You are about to try and delete '{project_name}'. This action is not reversible, please retype the project's name for confirmation:\n",
        style="danger",
    )
    confirmation = str(input("Confirmation: "))

    if confirmation != project_name:
        console.print("\nConfirmation not successful, aborting\n", style="warning")
        return

    # api call
    try:
        rc = api.delete_project(token, project_name)
    except NotAdmin:
        console.print(
            "\nYou must be the owner or an admin to delete this project!\n",
            style="danger",
        )
        return
    if rc == 200:
        console.print("\nProject deleted successfully!\n", style="success")
    else:
        console.print(
            f"\nSomething went wrong and could not delete project (HTTP Error {rc})\n",
            style="danger",
        )


def project_members_add(
    *project_name: str,
    console: Console = console,
    api: API = api,
) -> None:
    """Add a single member to a project. Must be the owner, a moderator, or a server admin.

    Raises:
        NotLoggedIn: invalid token
    """

    # join project name into a single string
    project_name = " ".join(project_name)

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    # input
    username = str(input("Username of user to add: "))
    if username == "":
        console.print("\nYou must enter a username of someone to add\n", style="danger")
        return

    # api call
    try:
        rc = api.project_add_member(token, project_name, username)
    except NotAdmin:
        console.print(
            "You must be the owner, a moderator, or an admin to add a user to this project!\n",
            style="danger",
        )
        return

    # handle response
    if rc == 200:
        console.print("\nUser added successfully to project\n", style="success")
    else:
        console.print(
            f"\nUser could not be added to the project (HTTP Error {rc})\n",
            style="danger",
        )


def project_members_remove(
    *project_name: str, console: Console = console, api: API = api
) -> None:

    # join project name into a single string
    project_name = " ".join(project_name)

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    # input
    username = str(input("Username of user to remove: "))
    if username == "":
        console.print(
            "\nYou must enter a username of someone to remove\n", style="danger"
        )
        return

    # api call
    try:
        rc = api.project_remove_member(token, project_name, username)
    except NotAdmin:
        console.print(
            "You must be the owner, a moderator, or an admin to remove a user from this project!\n",
            style="danger",
        )
        return

    # handle response
    if rc == 200:
        console.print("\nUser removed successfully from project\n", style="success")
    elif rc == 404:
        console.print("\nUser is not part of the project\n", style="warning")
    else:
        console.print(
            f"\nUser could not be removed from the project (HTTP Error {rc})\n",
            style="danger",
        )


def project_members(function: str, *args, console: Console = console) -> None:

    if function == "add":
        return project_members_add(*args)
    elif function == "remove":
        return project_members_remove(*args)
    else:
        raise AttributeError


def project_moderators_add(
    *project_name: str, console: Console = console, api: API = api
) -> None:

    # join project name into a single string
    project_name = " ".join(project_name)

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    # input
    username = str(input("Username of member to promote: "))
    if username == "":
        console.print(
            "\nYou must enter a username of someone to promote\n", style="danger"
        )
        return

    # api call
    try:
        rc = api.project_add_moderator(token, project_name, username)
    except NotAdmin:
        console.print(
            "You must be the owner or an admin to add a moderator to this project!\n",
            style="danger",
        )
        return

    # handle response
    if rc == 200:
        console.print("\nUser promoted to moderator successfully\n", style="success")
    elif rc == 404:
        console.print(
            "\nUser must be a member of the project before making them a moderator. Please add them to the project then try again\n",
            style="warning",
        )
    else:
        console.print(
            f"\nUser could not be promoted (HTTP Error {rc})\n",
            style="danger",
        )


def project_moderators_remove(
    *project_name: str, console: Console = console, api: API = api
) -> None:

    # join project name into a single string
    project_name = " ".join(project_name)

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    # input
    username = str(input("Username of moderator to demote: "))
    if username == "":
        console.print(
            "\nYou must enter a username of someone to demote\n", style="danger"
        )
        return

    # api call
    try:
        rc = api.project_remove_moderator(token, project_name, username)
    except NotAdmin:
        console.print(
            "You must be the owner or an admin to remove a moderator from this project!\n",
            style="danger",
        )
        return

    # handle response
    if rc == 200:
        console.print("\nUser demoted from moderator successfully\n", style="success")
    elif rc == 404:
        console.print(
            "\nUser is not a moderator within this project\n",
            style="warning",
        )
    else:
        console.print(
            f"\nUser could not be demoted (HTTP Error {rc})\n",
            style="danger",
        )


def project_moderators(function: str, *args, console: Console = console) -> callable:

    if function == "add":
        return project_moderators_add(*args)
    elif function == "remove":
        return project_moderators_remove(*args)
    else:
        raise AttributeError


def project_add_task() -> int:
    raise NotImplementedError


def project_edit_task() -> int:
    raise NotImplementedError


def project_remove_task() -> int:
    raise NotImplementedError


def project_task_add_member() -> int:
    raise NotImplementedError


def project_task_remove_member() -> int:
    raise NotImplementedError


def project_task_edit_progress() -> int:
    raise NotImplementedError


def project(function: str, *args: str) -> callable:
    """Parent function to combine all project functions

    Args:
        function (str): Which function to use

    Raises:
        AttributeError: invalid use of function

    Returns:
        callable: appropriate function to execute depending on user input
    """

    match function:
        case "show":
            return show_project(*args)
        case "create":
            return create_project(*args)
        case "edit":
            return edit_project(*args)
        case "delete":
            return delete_project(*args)
        case "members":
            return project_members(*args)
        case "moderators":
            return project_moderators(*args)
        case _:
            raise AttributeError
