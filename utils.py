import os
from datetime import datetime
import psycopg2
from argparse import Namespace
from dotenv import load_dotenv


class DataBase:
    def __init__(self):
        load_dotenv(".env")
        self.username = os.getenv("pmcli_db_user")
        self.password = os.getenv("pmcli_db_pw")
        self.db_name = os.getenv("pmcli_db_name")

    def execute_query(self, query):
        connection = psycopg2.connect(dbname=self.db_name, user=self.username, password=self.password, host="localhost",
                                      port=5432)
        cursor = connection.cursor()
        cursor.execute(query)
        output = cursor.fetchall()
        connection.commit()
        connection.close()
        return output

    @staticmethod
    def construct_create_query(params: Namespace, is_task=False) -> str:
        table = 'tasks' if is_task else 'projects'
        params = validate_input(params)

        row = [
            "'" + params.name + "'" if params.name else "''",
            "'" + params.description + "'" if params.description else "''",
            "'" + params.start_date + "'" if params.start_date else "''",
            "'" + params.end_date + "'" if params.end_date else "''",
            "'" + params.status + "'" if params.status else "''"
        ]
        if is_task:
            row.append(params.project_id)
        row.append("NOW()")
        query = f"INSERT INTO {table} (name, description, start_date, end_date, status,{" project_id," if is_task else""} created_at) VALUES "\
                f"({",".join(row)}) RETURNING id;"
        return query

    @staticmethod
    def construct_update_query(params:Namespace, is_task=False) -> str:
        table = 'tasks' if is_task else 'projects'
        params = validate_input(params)
        row = []
        if params.name:
            row.append(f"name='{params.name}'")
        if params.description:
            row.append(f"description='{params.description}'")
        if params.start_date:
            row.append(f"start_date='{params.start_date}'")
        if params.end_date:
            row.append(f"end_date='{params.end_date}'")
        if params.status:
            row.append(f"status='{params.status}'")
        if is_task:
            row.append(f"project_id='{params.project_id}'")
        query = f"UPDATE {table} SET {', '.join(row)} WHERE id='{params.task_id if is_task else params.project_id}' RETURNING id, name;"
        return query

    @staticmethod
    def construct_delete_query(params:Namespace, is_task=False) -> str:
        table = 'tasks' if is_task else 'projects'
        filter_str = ''
        if is_task and params.task_id:
            filter_str += f" id='{params.task_id}' "
        if is_task and params.project_id:
            if filter_str:
                filter_str += 'AND'
            filter_str += f" project_id='{params.project_id}' "
        elif not is_task and params.project_id:
            filter_str += f" id='{params.project_id}'"
        return f"DELETE FROM {table} WHERE{filter_str}RETURNING id, name;"


    @staticmethod
    def construct_list_query(args, is_task=False) -> str:
        table = 'tasks' if is_task else 'projects'
        return (f"SELECT id, name, description, start_date, end_date, status, created_at{', project_id' if is_task else ''}"
                f" FROM {table} {"" if not is_task else ('WHERE project_id=' + args.project_id)} "
                f"ORDER BY created_at DESC;")


def normalize_datetime(user_input):
    """
    Converts a user-provided date/time into the standard format: YYYY-MM-DD HH:MM:SS.
    If only a date is provided, the time defaults to 00:00:00.

    Args:
        user_input (str): The date/time string entered by the user.

    Returns:
        str: The formatted datetime string (YYYY-MM-DD HH:MM:SS).

    Raises:
        ValueError: If the input format is invalid.
    """

    possible_formats = [
        "%Y-%m-%d %H:%M:%S",  # 2025-02-10 14:30:00
        "%Y-%m-%d %H:%M",  # 2025-02-10 14:30
        "%Y-%m-%d %I:%M %p",  # 2025-02-10 02:30 PM
        "%Y-%m-%d",  # 2025-02-10 (defaults time to 00:00:00)
        "%d-%m-%Y %H:%M:%S",  # 10-02-2025 14:30:00
        "%d-%m-%Y %H:%M",  # 10-02-2025 14:30
        "%d-%m-%Y",  # 10-02-2025 (defaults time to 00:00:00)
        "%m/%d/%Y %H:%M:%S",  # 02/10/2025 14:30:00
        "%m/%d/%Y %H:%M",  # 02/10/2025 14:30
        "%m/%d/%Y",  # 02/10/2025 (defaults time to 00:00:00)
        "%B %d, %Y %H:%M:%S",  # February 10, 2025 14:30:00
        "%B %d, %Y %H:%M",  # February 10, 2025 14:30
        "%B %d, %Y",  # February 10, 2025 (defaults time to 00:00:00)
        "%b %d, %Y %H:%M:%S",  # Feb 10, 2025 14:30:00
        "%b %d, %Y %H:%M",  # Feb 10, 2025 14:30
        "%b %d, %Y"  # Feb 10, 2025 (defaults time to 00:00:00)
    ]

    for fmt in possible_formats:
        try:
            dt_obj = datetime.strptime(user_input, fmt)
            return dt_obj.strftime("%Y-%m-%d %H:%M:%S")  # Standard DB format
        except ValueError:
            continue

    raise ValueError(f"Invalid date/time format: {user_input}. Please provide a valid format.")

def validate_input(params: Namespace) -> Namespace:
    if "name" in params:
        if not isinstance(params.name, str):
            params.name = str(params.name)
    if"description" in  params:
        if not isinstance(params.description, str):
            params.description = str(params.description)
    if "start_date" in params:
        if params.start_date:
            params.start_date = normalize_datetime(params.start_date)
    if "end_date" in params:
        if params.end_date:
            params.end_date = normalize_datetime(params.end_date)
    if "status" in params:
        if not isinstance(params.description, str):
            params.status = str(params.status)
    if "created_at" in params:
        if params.created_date:
            params.created_date = normalize_datetime(params.created_date)
    return params

db = DataBase()
def create_row(args, is_task=False):
    query = db.construct_create_query(args, is_task)
    response = db.execute_query(query)
    if response:
        print("Successfully created " + ("Task" if is_task else "Project") + " with Id " + str(response[0][0]))
    return response

def update_row(args, is_task=False):
    query = db.construct_update_query(args, is_task)
    response = db.execute_query(query)
    if response:
        print("Successfully updated " + ("Task" if is_task else "Project") + str(response[0][0]) + '. ' + response[0][1])
    return  response

def list_row(args, is_task=False):
    query = db.construct_list_query(args, is_task)
    response = db.execute_query(query)
    if len(response) == 0:
        print('No ' + ('tasks' if is_task else 'projects') + ' found.')
        return None
    print('Found ' + str(len(response))+ ' ' + ('tasks' if is_task else 'projects'))
    headers = ["Id"]
    if is_task:
        headers.append("Project ID")
    headers.extend(["Name", "Start Date", "End Date", "Status", "Created Date", "Description"])
    result = [headers]
    if response:
        for res in response:
            start_date = datetime.strftime(res[3], "%Y-%m-%d %H:%M:%S")
            end_date = datetime.strftime(res[4], "%Y-%m-%d %H:%M:%S")
            created_date = datetime.strftime(res[6], "%Y-%m-%d %H:%M:%S")
            if args.name and args.name != res[1]:
                continue
            if args.start_date and args.start_date != start_date:
                continue
            if args.end_date and args.end_date != end_date:
                continue
            if args.created_date and args.created_date != created_date:
                continue
            result.append([str(res[0])])
            if is_task:
                result[-1].append(
                    str(res[-1])
                )
            result[-1].extend([
                res[1],
                start_date,
                end_date,
                res[5],
                created_date,
                res[2]
            ])
    return result

def delete_row(args, is_task=False):
    query = db.construct_delete_query(args, is_task)
    response = db.execute_query(query)
    if response:
        print("Successfully deleted " + ("Task" if is_task else "Project") + " with Id " + str(response[0][0]))
    return response

def column_max_length(arr):
    max_count = [0]*len(arr[0])
    for col in range(len(arr[0])):
        max_len = 0
        for row in range(len(arr)):
            max_len = max(max_len, len(arr[row][col]))
        max_count[col] = max_len
    return max_count

def print_result(arr):
    col_len = column_max_length(arr)
    print_str = ""
    for row in range(len(arr)):
        for col in range(len(arr[0])):
            print_str += arr[row][col] + ' ' * ((col_len[col] - len(arr[row][col])) + 5)
        print_str += "\n"
    print(print_str)