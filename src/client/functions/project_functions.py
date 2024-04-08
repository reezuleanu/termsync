from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.text import Text
from random import choice

from models import Project, Discrete_Task, Milestone_Task
from ui import console
from api import API, api
from utils import get_token, NotLoggedIn, NotAdmin, read_update_cache, pop_update_cache


def create_project(*args, console: Console = console, api: API = api) -> None:
    """Create new project"""

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

    # api call
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


def show_updated(*args, console: Console = console) -> None:
    """Show which projects were changed since last viewing them"""

    # random color for printing
    color = choice(["red", "blue", "green", "cyan", "purple", "magenta", "yellow"])

    # get cache data
    try:
        fp = open("data/update_cache.txt", "r")
        cache = fp.read()
    except FileNotFoundError:
        fp = open("data/update_cache.txt", "w")
        fp.write("")
        fp.close()
        cache = ""

    if cache == "":
        cache = "No projects updated"

    # print updated projects
    results = Panel.fit(
        f"[{color}]\n{cache}\n[/]", title="updated projects", border_style=color
    )
    console.print(results)


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
            print_all_projects(projects)
        return

    # api call
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
        if project.name in read_update_cache():
            pop_update_cache(project.name)
        print_project(project)


def print_project(project_data: Project, console: Console = console) -> None:
    """Function to properly display project data"""

    # random color for printing
    color = choice(["red", "blue", "green", "cyan", "purple", "magenta", "yellow"])

    # join lists into strings
    moderators = ", ".join(project_data.moderators)
    members = ", ".join(project_data.members)

    # convert task objects to strings
    tasks = ""
    for task in project_data.tasks:
        if type(task) is Discrete_Task:
            if task.completed == True:
                progress = "[green]Completed[/]"
            else:
                progress = f"[{int(task.completed)}/1]"
        else:
            if task.completed == task.milestones:
                progress = "[green]Completed[/]"
            else:
                progress = f"[{task.completed}/{task.milestones}]"

        converted = f"""
    [bold]{task.name}[/]
    [{color}]Description: [/]{task.description}
    [{color}]Progress: [/]{progress}
    [{color}]Members: [/]{", ".join(task.members)}
"""
        tasks = tasks + converted

    # print project data
    data = Panel.fit(
        f"""
[{color}]Owner: [/]{project_data.owner}\n
[{color}]Description: [/]{project_data.description}\n
[{color}]Moderators: [/]{moderators}\n
[{color}]Project members: [/]{members}\n
[{color}]Tasks: [/]
{tasks}""",
        border_style=color,
        title=project_data.name,
    )
    console.print(data)


def print_all_projects(projects: dict, console: Console = console) -> None:
    """Print all projects the user is a member of

    Args:
        projects (dict): list of projects, format: {project: project.progress}
        console (Console, optional): _description_. Defaults to console.
    """

    # random color for printing
    color = choice(["red", "blue", "green", "cyan", "purple", "magenta", "yellow"])

    # if user is not part of any projects
    if len(projects.keys()) == 0:
        console.print("You are not part of any projects\n", style=color)
        return

    # proint projects
    for project in projects:
        console.print(f"[{color}]{project}[/]\n")
        console.print(
            f"Progress: [{projects[project][0]}/{projects[project][1]}]\n",
        )

    console.print()  # add space


def edit_project(
    *project_name: str, console: Console = console, api: API = api
) -> None:
    """Edit project data (only description is eligible)


    Raises:
        NotLoggedIn: expired session
    """

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

    # the way i coded the api interface is already starting to punish me
    if type(project) is int:
        console.print("Could not find project\n", style="danger")

    # input
    project_description = str(input(f"Description [{project.description}]: "))
    if project_description == "":
        console.print("\nNothing changed1!\n", style="success")
        return

    project.description = project_description

    # update project on server
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


def project_moderators(function: str, *args) -> callable:

    if function == "add":
        return project_moderators_add(*args)
    elif function == "remove":
        return project_moderators_remove(*args)
    else:
        raise AttributeError


def project_tasks_add(
    *project_name: str, console: Console = console, api: API = api
) -> None:

    # join project name into a single string
    project_name = " ".join(project_name)

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    # input
    name = str(input("Task name: "))
    if name == "":
        console.print("\nYou must enter a project name\n", style="danger")
        return
    description = str(input("\nTask description: "))

    type = str(input("\nTask type [discrete | milestone]: "))
    if type not in ["discrete", "milestone"]:
        console.print("\nInvalid task type\n", style="danger")
        return

    if type == "milestone":
        try:
            milestones = int(input("\nTotal milestones: "))
        except:
            console.print("\nYou must enter a valid number\n", style="danger")
            return

        try:
            completed = int(input("\nHow many are completed so far: "))
        except:
            console.print("\nYou must enter a valid number\n", style="danger")
            return

        task = Milestone_Task(
            name=name,
            description=description,
            milestones=milestones,
            completed=completed,
        )
    if type == "discrete":
        task = Discrete_Task(name=name, description=description, completed=False)

    try:
        rc = api.project_post_task(token, project_name, task)

    except NotAdmin:
        console.print(
            "\nYou must be the owner, a moderator, or an admin to add tasks to this project\n",
            style="danger",
        )

    if rc == 200:
        console.print("\nTask added successfully\n", style="success")
    elif rc == 401:
        console.print(
            "\nTask with this name already exists within project\n", style="danger"
        )
    else:
        console.print(
            f"\nCould not add task to project (HTTP Error {rc})\n", style="danger"
        )


def project_tasks_edit(
    *project_name: str, console: Console = console, api: API = api
) -> None:

    # join project name into a single string
    project_name = " ".join(project_name)

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    # input
    task_name = str(input("Which task do you want to edit? : "))
    if task_name == "":
        console.print("\nYou must enter a task name to edit\n", style="danger")
        return

    # get latest task data
    project = api.get_project(token, project_name)

    if type(project) is int:
        console.print(
            f"\nCould not get latest data from the project (HTTP Error {project})\n",
            style="danger",
        )
        return

    task_index = [task.name for task in project.tasks].index(task_name)
    task = project.tasks[task_index]

    # more input
    task_description = str(input(f"\nTask Description [{task.description}]: "))
    if task_description == "":
        task_description = task.description

    task.description = task_description

    if type(task) is Milestone_Task:
        milestones = str(input(f"\nTotal milestones [{task.milestones}]: "))
        if milestones == "":
            milestones = 0
        else:
            try:
                milestones = int(milestones)
            except ValueError:
                console.print("\nYou must enter a valid number\n", style="danger")
                return

        if milestones != 0:
            task.milestones = milestones

    try:
        rc = api.project_put_task(token, project_name, task_name, task)
    except NotAdmin:
        console.print(
            "\nYou must be the owner, a moderator, or an admin to edit tasks within this project\n",
            style="danger",
        )
        return

    if rc == 200:
        console.print("\nTask updated successfully\n", style="success")
    elif rc == 404:
        console.print("\nTask not found\n", style="danger")
    else:
        console.print(f"\nCould not update task (HTTP Error {rc})\n", style="danger")


def project_tasks_delete(
    *project_name: str, console: Console = console, api: API = api
) -> None:

    # join project name into a single string
    project_name = " ".join(project_name)

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    # input
    task_name = str(input("Which task do you want to remove? : "))
    if task_name == "":
        console.print("\nYou must enter a task to delete\n", style="danger")
        return

    # api call
    try:
        rc = api.project_delete_task(token, project_name, task_name)
    except NotAdmin:
        console.print(
            "\nYou must be the owner or an admin to delete this project\n",
            style="danger",
        )

    if rc == 200:
        console.print("\nTask deleted successfully\n", style="success")
    elif rc == 404:
        console.print("\nCould not find task\n", style="danger")
    else:
        console.print(f"\nCould not delete task (HTTP Error {rc})\n", style="danger")


def project_tasks_members_add(
    *project_name: str, console: Console = console, api: API = api
) -> None:

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    # join project name into a single string
    project_name = " ".join(project_name)

    # input
    task_name = str(input("Enter a task name: "))
    if task_name == "":
        console.print(
            "\nYou must enter a task name to add members to\n", style="danger"
        )
        return

    username = str(input("\nEnter username of user to add: "))
    if username == "":
        console.print("\nYou must enter a user to add to the task\n", style="danger")
        return

    # api call
    try:
        rc = api.project_task_post_member(token, project_name, task_name, username)
    except NotAdmin:
        console.print(
            "\nYou must be the owner, a moderator, or an admin to add users to tasks"
        )
        return

    if rc == 200:
        console.print("\nUser added to the task successfully\n", style="success")
    elif rc == 400:
        console.print(
            "\nUser is not part of the project. Add them as a member of the project first!\n",
            style="danger",
        )
    elif rc == 404:
        console.print("\nTask not found\n", style="danger")
    else:
        console.print(
            f"\nUser could not be added to task (HTTP Error {rc})\n", style="danger"
        )


def project_tasks_members_remove(
    *project_name: str, console: Console = console, api: API = api
) -> None:

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    # join project name into a single string
    project_name = " ".join(project_name)

    # input
    task_name = str(input("Enter a task name: "))
    if task_name == "":
        console.print(
            "\nYou must enter a task name to remove members from\n", style="danger"
        )
        return

    username = str(input("\nEnter username of user to remove: "))
    if username == "":
        console.print(
            "\nYou must enter a user to remove from the task\n", style="danger"
        )
        return

    # api call
    try:
        response = api.project_task_delete_member(
            token, project_name, task_name, username
        )
    except NotAdmin:
        console.print(
            "\nYou must be the owner, a moderator, or an admin to remove users from tasks"
        )
        return

    # new method to handle api responses
    match response.status_code:
        case 200:
            console.print(
                "\nUser removed from the task successfully\n", style="success"
            )
        case _:
            console.print(
                f"\nHTTP Error {response.status_code}: {response.json()['detail']}\n",
                style="danger",
            )

    # if rc == 200:
    #     console.print("\nUser removed from the task successfully\n", style="success")
    # elif rc == 400:
    #     console.print(
    #         "\nUser is not part of the task\n",
    #         style="danger",
    #     )
    # elif rc == 404:
    #     console.print("\nTask not found\n", style="danger")
    # else:
    #     console.print(
    #         f"\nUser could not be removed from task (HTTP Error {rc})\n", style="danger"
    #     )


def project_tasks_progress(
    *project_name: str, console: Console = console, api: API = api
) -> None:

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    # join project name into a single string
    project_name = " ".join(project_name)

    # input
    task_name = str(input("Enter a task name: "))
    if task_name == "":
        console.print(
            "\nYou must enter a task name to update progress for\n", style="danger"
        )
        return

    # get latest data
    project = api.get_project(token, project_name)
    if type(project) is int:
        console.print(
            f"\nCould not get latest project data (HTTP Error {project})\n",
            style="danger",
        )
        return

    # get task from project
    try:
        task_index = [task.name for task in project.tasks].index(task_name)
    except ValueError:
        console.print(
            f"\nThere is no task with that name within '{project_name}'\n",
            style="danger",
        )
        return
    task = project.tasks[task_index]

    # more input
    if type(task) is Milestone_Task:
        progress = str(
            input(f"\nPlease enter new progress [{task.completed}/{task.milestones}]: ")
        )
        if progress == "":
            console.print("\nProgress was not updated\n", style="success")
            return
        else:
            try:
                progress = int(progress)
            except ValueError:
                console.print("\nPlease enter a valid number\n", style="danger")
                return
    else:
        if task.completed is False:
            progress = True
        else:
            progress = False

    # api call
    try:
        response = api.project_task_update_progress(
            token, project_name, task_name, progress
        )
    except NotAdmin:
        console.print(
            "\nYou must be a member of the task, a moderator, the owner, or an admin to edit task completion\n",
            style="danger",
        )

    match response.status_code:
        case 200:
            console.print("\nProgress updated successfully\n", style="success")
        case _:
            console.print(
                f"\nCould not update task progress (HTTP Error {response.status_code}: {response.json()['detail']})",
                style="danger",
            )


def project_tasks_members(function: str, *args) -> callable:

    match function:
        case "add":
            return project_tasks_members_add(*args)
        case "remove":
            return project_tasks_members_remove(*args)
        case _:
            raise AttributeError


def project_tasks(function: str, *args) -> callable:

    match function:
        case "add":
            return project_tasks_add(*args)
        case "delete":
            return project_tasks_delete(*args)
        case "edit":
            return project_tasks_edit(*args)
        case "members":
            return project_tasks_members(*args)
        case "progress":
            return project_tasks_progress(*args)
        case _:
            raise AttributeError


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
        case "update":
            return show_updated(*args)
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
        case "tasks":
            return project_tasks(*args)
        case _:
            raise AttributeError
