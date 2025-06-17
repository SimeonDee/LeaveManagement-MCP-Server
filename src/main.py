# import asyncio
from textwrap import dedent
from typing import List
from enum import StrEnum
from pydantic import BaseModel
from datetime import datetime
from dateutil.parser import parse

from mcp.server.fastmcp import FastMCP


class LeaveType(StrEnum):
    SICK = "sick"
    VACATION = "vacation"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    OTHERS = "others"


class Employee(BaseModel):
    id: str
    name: str
    balance: int


class LeaveHistory(BaseModel):
    employee_id: str
    purpose: LeaveType
    leave_date: str


mcp = FastMCP("LeaveManager")

employees = [
    {"id": "0001", "name": "Wale", "balance": 20},
    {"id": "0002", "name": "Seun", "balance": 20},
    {"id": "0003", "name": "Kayode", "balance": 20},
    {"id": "0004", "name": "Adeola", "balance": 20},
]

leave_histories = [
    {"employee_id": "0001", "purpose": "sick", "leave_date": "2025-06-01"},
    {"employee_id": "0001", "purpose": "vacation", "leave_date": "2025-06-05"},
    {"employee_id": "0001", "purpose": "sick", "leave_date": "2025-06-10"},
    {"employee_id": "0001", "purpose": "sick", "leave_date": "2025-06-16"},
    {"employee_id": "0002", "purpose": "others", "leave_date": "2025-06-12"},
]


def format_date(leave_date: str):
    try:
        date_obj = parse(leave_date, fuzzy=False)
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        raise


def is_valid_leave_date(leave_date_str: str) -> bool:
    try:
        # Confirm leave date is a valid date
        leave_date_obj = parse(leave_date_str, fuzzy=False)
        # validating leave_date is a future date
        date_diff = (leave_date_obj - datetime.today()).days
        return True if date_diff > 0 else False
    except ValueError:
        return False


def add_leave_to_history(employee_id: str, purpose: str, leave_date: str):
    leave_histories.append(
        {
            "employee_id": employee_id,
            "purpose": purpose,
            "leave_date": format_date(leave_date),
        }
    )  # no-qa


def format_leave_history(history: LeaveHistory) -> str:
    return dedent(
        f"""
        Date: {history.leave_date}
        Purpose: {history.purpose.capitalize()}
    """
    )


@mcp.tool()
def register_employee(name: str) -> str:
    """Registers a new employee.

    Args:
        name (str): The name of the new employee to register.

    Returns:
        str: A success message with the generated ID of the
            registered employee and the maximum leave available
            or a failure message if registration fails.
    """
    last_employee = employees[-1]
    new_id = str(int(last_employee["id"]) + 1).rjust(4, "0")
    new_employee = {"id": new_id, "name": name, "balance": 20}
    employees.append(new_employee)
    return (
        f"Registration successful. Your employee ID is {new_id} and you "
        f"are entitled to a maximum of {new_employee['balance']} days leave."
    )


@mcp.tool()
def apply_for_leave(
    employee_id: str,
    leave_dates: List[str],
    purpose: str,
) -> str:
    """Processes leave request from employee.

    Args:
        employee_id (str): The ID of the employee applying for leave e.g.
            "0001", "0002".
        leave_dates (List[str]): A list of leave dates applied for. e.g.
            ["2025-04-20"] or ["2025-04-20", "2025-02-30"].
        purpose (str): The purpose of the leave. Value can be one of
            {"sick", "vacation", "maternity", "paternity", "others"}.

    Returns:
        str: A message indicating that the leave application has
            been successful or not.
    """
    # validate date
    invalid_dates = [dt for dt in leave_dates if not is_valid_leave_date(dt)]
    if len(invalid_dates) > 0:
        return (
            f"Error: Invalid leave dates {invalid_dates}. "
            "Leave date should be a valid date and should not be a past date."
        )

    if purpose.lower() not in {"sick", "vacation", "maternity", "paternity"}:
        purpose = LeaveType.OTHERS.value

    # matches = list(
    #     filter(lambda emp: emp["id"] == employee_id.lower(), employees),
    # )
    # find details of employee applying for leave
    matches = [
        (i, employees[i])
        for i in range(len(employees))
        if employees[i]["id"] == employee_id
    ]  # no-qa

    if len(matches) == 0:
        return f"Not Found: Employee with ID '{employee_id}' not found."
    else:
        idx, employee = matches[0]
        leave_count = len(leave_dates)
        if leave_count > employee["balance"]:
            return (
                "Sorry, Insufficient leave balance. "
                f"You have only {employee["balance"]} leave days left."
            )
        else:
            try:
                for leave_dt in leave_dates:
                    add_leave_to_history(employee["id"], purpose, leave_dt)
            except ValueError as e:
                return f"Error: {e}"
            new_balance = employee["balance"] - leave_count
            employees[idx]["balance"] = new_balance

            return (
                f"Your leave application for {leave_dates} is successful. "
                f"You now have {new_balance} leave days left."
            )


@mcp.tool()
def cancel_leaves(employee_id: str, leave_dates: List[str]) -> str:
    """Deletes or cancels a leave for an employee with given employee ID
    for the specified leave_dates, if leave exists.

    Args:
        employee_id (str): The id of the employee e.g. "0001", "0043".
        leave_dates (str): The dates of the leave to cancel e.g.
            ["2025-10-19"], ["2025-10-19", "2025-10-20"].

    Returns:
        str: Success or failure message.
    """
    formatted_dates = [format_date(dt) for dt in leave_dates]
    valid_dates = [is_valid_leave_date(dt) for dt in formatted_dates]
    if False in valid_dates:
        return (
            "An invalid date is found "
            f"{leave_dates[valid_dates.index(False)]}"
            "Dates can only be a valid date and must be a future date."
        )
    found_histories = [
        history
        for history in leave_histories
        if (
            history["employee_id"] == employee_id.lower()
            and history["leave_date"] in formatted_dates
        )
    ]  # no-qa
    if len(found_histories) == 0:
        return "No leave taken by the employee for the date(s) given."
    for history in found_histories:
        leave_histories.remove(history)
    return 'Leaves approved for ""'


@mcp.resource("leave://histories/{employee_id}")
def get_leave_histories(employee_id: str) -> str:
    """Get the leave history of an employee with the provided employee_id.

    Args:
        employee_id (str): The ID of the employee to retrieve leave history.

    Returns:
        str: The leave history of the employee in markdown format.
    """
    found_employee = [
        employee for employee in employees if employee["id"] == employee_id
    ]
    employee_histories = [
        history
        for history in leave_histories
        if history["employee_id"] == employee_id  # no-qa
    ]
    header = dedent(
        f"""
        ### Leave History
        [color blue] **Employee Name:** *{found_employee[0]["name"]} [/color]
        **Leave Balance:** *{found_employee[0]["balance"]}
        """
    )
    formatted_histories = [
        format_leave_history(LeaveHistory(**history))
        for history in employee_histories  # no-qa
    ]
    formatted_histories_md_str = "\n---\n".join(formatted_histories)
    return dedent(
        f"""
            {header}

            ---
            {formatted_histories_md_str}
        """
    )


if __name__ == "__main__":
    mcp.run(transport="sse", mount_path="/leavemanager")
