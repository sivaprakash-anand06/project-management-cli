import argparse
import sys
from dotenv import load_dotenv
from utils import *
load_dotenv(".env")


def get_arguments():
    parser = argparse.ArgumentParser(
        prog="project-cli",
        description="A simple project management CLI tool. Supports commands like create-task, update-task, and list-tasks."
    )

    subparsers = parser.add_subparsers(title="Commands", description="Available commands", dest="command")

    # Project commands
    # create project
    create_project_args = subparsers.add_parser("create-project", help="Create a new project.")
    create_project_args.add_argument("name", type=str, default="", help="Name of the project")
    create_project_args.add_argument("--start-date", type=str, default="", help="Start date of the project (YYYY-MM-DD)")
    create_project_args.add_argument("--end-date", type=str, default="", help="End date of the project (YYYY-MM-DD)")
    create_project_args.add_argument("--description", type=str, default="", help="Short description of the project")
    create_project_args.add_argument("--status", type=str, choices=["future", "on-going", "done"],
                                default="future", help="Current status of the project")
    # update project
    update_project_args = subparsers.add_parser("update-project", help="Create a project.")
    update_project_args.add_argument("--name", type=str, help="Name of the project")
    update_project_args.add_argument("--start-date", type=str,  help="Start date of the project (YYYY-MM-DD)")
    update_project_args.add_argument("--end-date", type=str, help="End date of the project (YYYY-MM-DD)")
    update_project_args.add_argument("--description", type=str, help="Short description of the project")
    update_project_args.add_argument("--status", type=str, choices=["future", "on-going", "done"],
                                default="future", help="Current status of the project")
    update_project_args.add_argument("project_id", type=int, help="ID of the project to delete")

    delete_project_args = subparsers.add_parser("delete-project", help="delete the projects.")
    delete_project_args.add_argument("project_id", type=int, help="ID of the project to delete")

    list_project_args = subparsers.add_parser("list-projects", help="list the projects.")
    list_project_args.add_argument("--name", type=str, help="Name of the task")
    list_project_args.add_argument("--start-date", type=str, help="Start date of the task (YYYY-MM-DD)")
    list_project_args.add_argument("--end-date", type=str, help="End date of the task (YYYY-MM-DD)")
    list_project_args.add_argument("--status", type=str, choices=["to-do", "on-going", "done"],
                                default="to-do", help="Current status of the task")
    list_project_args.add_argument("--created-date", type=str, help="Created date of the task (YYYY-MM-DD)")

    # # Task commands
    create_task_args = subparsers.add_parser("create-task", help="Create a new task.")
    create_task_args.add_argument("name", type=str, help="Name of the task")
    create_task_args.add_argument("--start-date", type=str, required=True, help="Start date of the task (YYYY-MM-DD)")
    create_task_args.add_argument("--end-date", type=str, required=True, help="End date of the task (YYYY-MM-DD)")
    create_task_args.add_argument("--description", type=str, help="Short description of the task")
    create_task_args.add_argument("--status", type=str, choices=["to-do", "on-going", "done"],
                                default="to-do", help="Current status of the task")
    create_task_args.add_argument('--project-id', type=str, required=True,
                                  help="Enter project id under which the task needs to be created.")

    # update project
    update_task_args = subparsers.add_parser("update-task", help="Create a task.")
    update_task_args.add_argument("name", type=str, help="Name of the task")
    update_task_args.add_argument("--start-date", type=str, required=True, help="Start date of the task (YYYY-MM-DD)")
    update_task_args.add_argument("--end-date", type=str, required=True, help="End date of the task (YYYY-MM-DD)")
    update_task_args.add_argument("--description", type=str, help="Short description of the task")
    update_task_args.add_argument("--status", type=str, choices=["to-do", "on-going", "done"],
                                default="to-do", help="Current status of the task")
    update_task_args.add_argument('--project-id', type=str,
                                  help="Enter project id under which the task needs to be created.")

    delete_task_args = subparsers.add_parser("delete-tasks", help="delete the tasks.")
    delete_task_args.add_argument("--task-id", type=int, help="ID of the project to delete")
    delete_task_args.add_argument("--project-id", type=int, help="ID of the project to delete")


    list_task_args = subparsers.add_parser("list-tasks", help="list the tasks.")
    list_task_args.add_argument('--project-id', type=str, default='1',
                                  help="Enter project id under which the task needs to be created.")

    # Parse the arguments
    args = parser.parse_args()
    return args


def main():
    args = get_arguments()
    if args.command == "create-project":
            response = create_row(args)
    elif args.command == "update-project":
            response = update_row(args)
    elif args.command == "list-projects":
            response = list_row(args)
            print_result(response)
    elif args.command == "delete-project":
            response = delete_row(args)
    elif args.command == "create-task":
            response = create_row(args, is_task=True)
    elif args.command == "update-task":
            response = update_row(args, is_task=True)
    elif args.command == "list-tasks":
            response = list_row(args, is_task=True)
    elif args.command == "delete-tasks":
            response = delete_row(args, is_task=True)


if __name__ == "__main__":
    main()
