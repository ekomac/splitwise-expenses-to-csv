from math import exp
import os
from typing import Any
from click import group
from dotenv import load_dotenv
from splitwise import Splitwise
from splitwise.user import ExpenseUser, User
from splitwise.receipt import Receipt
from splitwise.category import Category
from splitwise.debt import Debt
import sys


load_dotenv()

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
API_KEY = os.getenv("API_KEY")


def get_group_id(splitwise_obj: Splitwise, group_name: str) -> int | None:
    """
    Retrieves the ID of a Splitwise group based on its name.

    Args:
        splitwise_obj (Splitwise): An instance of the Splitwise class.
        group_name (str): The name of the Splitwise group.

    Returns:
        int | None: The ID of the group if found, None otherwise.
    """
    groups = splitwise_obj.getGroups()
    return next((group.id for group in groups if group.name == group_name), None)


def get_all_expenses_from_group(splitwise_obj: Splitwise, group_id: int):
    expenses = splitwise_obj.getExpenses(limit=10000, group_id=group_id)
    return expenses


def save_as_csv(expenses: list[dict[str, Any]], file_name="expenses.csv"):
    """
    Save the expenses to a CSV file.

    Args:
        expenses (list[dict[str, Any]]): A list of expenses to be saved.
        file_name (str): The name of the CSV file to be saved.
    """
    with open(file_name, "w", encoding="utf-8") as f:
        f.write("id,description,details,cost,created_at,category_name\n")
        for expense in expenses:
            f.write(
                f'"{expense["id"]}","{expense["description"]}","{expense["details"]}","{expense["cost"]}","{expense["created_at"]}","{expense["category_name"]}"\n'
            )


def flatten_expense(expense):
    """
    Flatten the expense object into a dictionary.

    Args:
        expense (Expense): The expense object to be flattened.

    Returns:
        dict: A dictionary containing the flattened expense details.
            - id: The ID of the expense.
            - description: The description of the expense.
            - details: The details of the expense.
            - cost: The cost of the expense.
            - created_at: The creation date of the expense.
            - category_name: The name of the expense category.
    """
    return {
        "id": expense.id,
        "description": expense.description,
        "details": expense.details,
        "cost": expense.cost,
        "created_at": expense.created_at,
        "category_name": expense.category.name,
    }


if __name__ == "__main__":
    group_name = sys.argv[1]
    splitwise_obj = Splitwise(CONSUMER_KEY, CONSUMER_SECRET, api_key=API_KEY)

    group_id = get_group_id(splitwise_obj, group_name)
    if group_id is None:
        print("Group not found")
        sys.exit(1)

    expenses = get_all_expenses_from_group(splitwise_obj, group_id)
    total = len(expenses)
    expenses = map(flatten_expense, expenses)

    save_as_csv(expenses)

    print(f"Saved {total} expenses to CSV")
    sys.exit(0)
