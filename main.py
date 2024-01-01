from math import exp
import os
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


def save_as_csv(expenses):
    pass


def flatten_expenses(expenses):
    for expense in expenses:
        mapped_expense = {}
        for k, v in expense.__dict__.items():
            if isinstance(v, Debt):
                mapped_expense[f"{k}_amount"] = v.amount
                mapped_expense[f"{k}_currency_code"] = v.currency_code
                mapped_expense[f"{k}_from_user_id"] = v.from_user_id
                mapped_expense[f"{k}_to_user_id"] = v.to_user_id

            elif isinstance(v, Receipt):
                continue
            elif isinstance(v, ExpenseUser):
                pass
            elif isinstance(v, User):
                mapped_expense[f"{k}_id"] = v.id
                mapped_expense[f"{k}_first_name"] = v.first_name
                mapped_expense[f"{k}_last_name"] = v.last_name
                mapped_expense[f"{k}_email"] = v.email
            else:
                mapped_expense[k] = v


if __name__ == "__main__":
    group_name = sys.argv[1]
    splitwise_obj = Splitwise(CONSUMER_KEY, CONSUMER_SECRET, api_key=API_KEY)

    group_id = get_group_id(splitwise_obj, group_name)
    if group_id is None:
        print("Group not found")
        sys.exit(1)

    expenses = get_all_expenses_from_group(splitwise_obj, group_id)
    for expense in expenses:
        mapped_expense = {}
        for k, v in expense.__dict__.items():
            if isinstance(v, ExpenseUser):
                mapped_expense.update(v)

    print(expenses[0].__dict__)

    save_as_csv(expenses)

    total = len(list(expenses))
    print(f"Saved {total} expenses to CSV")
    sys.exit(0)
