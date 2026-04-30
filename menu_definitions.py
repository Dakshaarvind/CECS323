"""
menu_definitions.py — Static menu declarations for the Classic Models MongoDB application.
"""
from Menu import Menu
from Option import Option

# ── Main ────────────────────────────────────────────────────────────────────
menu_main = Menu('main', 'Please select one of the following options:', [
    Option("Add",                    "add(db)"),
    Option("List / Report",          "list_objects(db)"),
    Option("Delete",                 "delete(db)"),
    Option("Update",                 "update(db)"),
    Option("Reports",                "reports(db)"),
    Option("Exit this application",  "pass"),
])

# ── Add sub-menu ─────────────────────────────────────────────────────────────
add_menu = Menu('add', 'What would you like to add?', [
    Option("New Order",    "add_new_order(db)"),
    Option("New Employee", "add_new_employee(db)"),
    Option("Exit",         "pass"),
])

# ── List sub-menu ────────────────────────────────────────────────────────────
list_menu = Menu('list', 'What would you like to list?', [
    Option("Exit", "pass"),
])

# ── Delete sub-menu ──────────────────────────────────────────────────────────
delete_menu = Menu('delete', 'What would you like to delete?', [
    Option("Exit", "pass"),
])

# ── Update sub-menu ──────────────────────────────────────────────────────────
update_menu = Menu('update', 'What would you like to update?', [
    Option("Exit", "pass"),
])

# ── Reports sub-menu ─────────────────────────────────────────────────────────
reports_menu = Menu('reports', 'Which report would you like to run?', [
    Option("Employee Hierarchy", "employee_hierarchy_report(db)"),
    Option("Order Report",       "order_report(db)"),
    Option("Exit",               "pass"),
])
