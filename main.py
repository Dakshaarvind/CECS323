"""
main.py — Menu-driven front-end for the Classic Models MongoDB application.
"""
from menu_definitions import (menu_main, add_menu, list_menu, delete_menu,
                              update_menu, reports_menu)
from db_connection import db
import random
from datetime import datetime
from pymongo.errors import DuplicateKeyError


# ════════════════════════════════════════════════════════════════════════════
# Sub-menu dispatchers
# ════════════════════════════════════════════════════════════════════════════

def add(db):
    action = ''
    while action != add_menu.last_action():
        action = add_menu.menu_prompt()
        exec(action)

def list_objects(db):
    action = ''
    while action != list_menu.last_action():
        action = list_menu.menu_prompt()
        exec(action)

def delete(db):
    action = ''
    while action != delete_menu.last_action():
        action = delete_menu.menu_prompt()
        exec(action)

def update(db):
    action = ''
    while action != update_menu.last_action():
        action = update_menu.menu_prompt()
        exec(action)

def reports(db):
    action = ''
    while action != reports_menu.last_action():
        action = reports_menu.menu_prompt()
        exec(action)


# ════════════════════════════════════════════════════════════════════════════
# TASK 4a — ADD A NEW ORDER (teammate's implementation, with ordernumbers fix)
# ════════════════════════════════════════════════════════════════════════════

def add_new_order(db):
    print("\n--- Add a New Order ---")

    # --- Customer lookup ---
    cust_name = input("Enter Customer Name (e.g., 'Atelier graphique'): ").strip()
    customer = db.customers.find_one({"customername": cust_name})
    if not customer:
        print("Customer not found in the database. Returning to menu.")
        return

    # --- Order date / required date ---
    while True:
        order_date_str = input("Enter Order Date (YYYY-MM-DD): ").strip()
        required_date_str = input("Enter Required Date (YYYY-MM-DD): ").strip()
        try:
            order_date = datetime.strptime(order_date_str, "%Y-%m-%d")
            required_date = datetime.strptime(required_date_str, "%Y-%m-%d")
            if required_date < order_date:
                print("Error: Required date must be on or after the order date. Try again.")
                continue
            break
        except ValueError:
            print("Invalid date format. Please use exactly YYYY-MM-DD.")

    # --- Product loop ---
    order_details = []
    added_products = set()

    while True:
        prod_code = input("\nEnter Product Code to add (or 'done' to finish): ").strip()
        if prod_code.lower() == 'done':
            if not order_details:
                print("Error: An order must have at least one product. Try again.")
                continue
            break

        if prod_code in added_products:
            print("Error: You already added this product. Choose a different one.")
            continue

        product = db.products.find_one({"_id": prod_code})
        if not product:
            print("Invalid Product Code. Try again.")
            continue

        while True:
            try:
                qty = int(input(f"Quantity to order (In stock: {product['quantityinstock']}): "))
                if qty < 1:
                    print("Quantity must be at least 1.")
                elif qty > product['quantityinstock']:
                    print("Error: Cannot order more than we have in stock!")
                else:
                    break
            except ValueError:
                print("Please enter a valid whole number.")

        msrp = product.get('msrp', 0)
        price_each = round(random.uniform(1.5 * msrp, 2.0 * msrp), 2)

        order_details.append({
            "product": {
                "productcode": prod_code,
                "productname": product['productname']
            },
            "quantityordered": qty,
            "priceeach": price_each
        })
        added_products.add(prod_code)

    # --- Build order document ---
    new_order = {
        "customer": {
            "customernumber": customer["_id"],
            "customername": customer["customername"]
        },
        "orderdate": order_date,
        "requireddate": required_date,
        "shippeddate": None,
        "status": "In Process",
        "details": order_details
    }

    # --- Insert order, update inventory, update customer's ordernumbers ---
    try:
        result = db.orders.insert_one(new_order)
        new_order_id = result.inserted_id

        # Decrement quantityinstock for each product ordered
        for item in order_details:
            db.products.update_one(
                {"_id": item['product']['productcode']},
                {"$inc": {"quantityinstock": -item['quantityordered']}}
            )

        # Keep the customer's ordernumbers list in sync (Warning requirement)
        db.customers.update_one(
            {"_id": customer["_id"]},
            {"$addToSet": {"ordernumbers": new_order_id}}
        )

        print(f"\n  Success! Order {new_order_id} placed and inventory updated.")

    except DuplicateKeyError:
        print("\n  DATABASE ERROR: This customer already has an order on that date "
              "(Constraint orders_uk_01 triggered).")


# ════════════════════════════════════════════════════════════════════════════
# TASK 4b — ADD A NEW EMPLOYEE
# ════════════════════════════════════════════════════════════════════════════

def add_new_employee(db):
    """
    Prompts for a new employee's details, inserts them into employees, and
    also inserts a minimal record into either managers or sales_representatives
    depending on their role.

    If manager   → asks which employees report to them and updates those
                   employees' reportsto field. Also updates the manager's
                   subordinates list.
    If sales rep → asks which customers they serve and updates those
                   customers' salesrep field. Also updates the sales rep's
                   customers list.
    """
    print("\n--- Add a New Employee ---")

    # ── Basic details ────────────────────────────────────────────────────────
    lastname  = input("Last name: ").strip()
    firstname = input("First name: ").strip()
    email     = input("Email: ").strip()
    jobtitle  = input("Job title: ").strip()

    # ── Office ───────────────────────────────────────────────────────────────
    officecode = input("Office code (1-7): ").strip()
    office_doc = db.offices.find_one({"_id": officecode})
    if not office_doc:
        print(f"Office '{officecode}' not found. Returning to menu.")
        return

    # Extension must be unique within the office (employees_uk_01 index)
    while True:
        extension = input(f"Extension (must be unique in {office_doc['city']} office): ").strip()
        clash = db.employees.find_one({"officecode": officecode, "extension": extension})
        if clash:
            print(f"  Extension '{extension}' is already used in that office. Choose another.")
        else:
            break

    # ── Manager or sales rep? ────────────────────────────────────────────────
    while True:
        role = input("Is this employee a (M)anager or a (S)ales Representative? ").strip().upper()
        if role in ('M', 'S'):
            break
        print("Please enter M or S.")

    # ── Who does this employee report to? ───────────────────────────────────
    reportsto_doc = None
    mgr_last  = input("Reports-to last name (leave blank if none): ").strip()
    mgr_first = input("Reports-to first name (leave blank if none): ").strip()
    if mgr_last and mgr_first:
        mgr = db.employees.find_one({"lastname": mgr_last, "firstname": mgr_first})
        if not mgr:
            print(f"  Warning: could not find manager '{mgr_first} {mgr_last}' in employees. "
                  "Setting reportsto to null.")
        else:
            reportsto_doc = {"lastname": mgr_last, "firstname": mgr_first}

    # ── Generate next employee number (max _id + 1) ──────────────────────────
    pipeline = [{"$group": {"_id": None, "max_id": {"$max": "$_id"}}}]
    agg = list(db.employees.aggregate(pipeline))
    new_emp_num = (agg[0]["max_id"] + 1) if agg else 1000

    # ── Build employee document ───────────────────────────────────────────────
    new_employee = {
        "_id":        new_emp_num,
        "lastname":   lastname,
        "firstname":  firstname,
        "extension":  extension,
        "email":      email,
        "officecode": officecode,
        "jobtitle":   jobtitle,
        "office": {
            "officecode": officecode,
            "city":       office_doc["city"],
            "state":      office_doc.get("state"),
            "country":    office_doc["country"]
        },
        "reportsto":  reportsto_doc
    }

    # ── Insert into employees ─────────────────────────────────────────────────
    try:
        db.employees.insert_one(new_employee)
    except DuplicateKeyError:
        print("  DATABASE ERROR: Duplicate key on insert into employees. Aborting.")
        return

    # Also add them to the office's embedded employees array
    db.offices.update_one(
        {"_id": officecode},
        {"$push": {"employees": {
            "employeenumber": new_emp_num,
            "lastname":       lastname,
            "firstname":      firstname,
            "jobtitle":       jobtitle
        }}}
    )

    # ── Role-specific logic ───────────────────────────────────────────────────
    if role == 'M':
        _handle_new_manager(db, new_emp_num, lastname, firstname)
    else:
        _handle_new_sales_rep(db, new_emp_num, lastname, firstname)

    print(f"\n  Success! Employee #{new_emp_num} ({firstname} {lastname}) added.")


def _handle_new_manager(db, emp_num, lastname, firstname):
    """Insert into managers and link subordinates."""

    # Minimal manager record + subordinates list (Warning requirement)
    manager_doc = {
        "_id":         emp_num,
        "lastname":    lastname,
        "firstname":   firstname,
        "subordinates": []
    }
    db.managers.insert_one(manager_doc)

    print(f"\n  '{firstname} {lastname}' added as a manager.")
    print("  Enter the employees who report to this manager.")
    print("  (Leave last name blank when finished.)\n")

    while True:
        sub_last  = input("  Subordinate last name (blank to stop): ").strip()
        if not sub_last:
            break
        sub_first = input("  Subordinate first name: ").strip()

        subordinate = db.employees.find_one({"lastname": sub_last, "firstname": sub_first})
        if not subordinate:
            print(f"    Employee '{sub_first} {sub_last}' not found. Skipping.")
            continue

        # Update employee's reportsto to point to this new manager
        db.employees.update_one(
            {"_id": subordinate["_id"]},
            {"$set": {"reportsto": {"lastname": lastname, "firstname": firstname}}}
        )

        # Add to the manager's subordinates list (Warning requirement)
        db.managers.update_one(
            {"_id": emp_num},
            {"$addToSet": {"subordinates": {
                "employeenumber": subordinate["_id"],
                "lastname":       sub_last,
                "firstname":      sub_first
            }}}
        )
        print(f"    Linked: {sub_first} {sub_last} now reports to {firstname} {lastname}.")


def _handle_new_sales_rep(db, emp_num, lastname, firstname):
    """Insert into sales_representatives and link customers."""

    # Minimal sales rep record + customers list (Warning requirement)
    sr_doc = {
        "_id":       emp_num,
        "lastname":  lastname,
        "firstname": firstname,
        "customers": []
    }
    db.sales_representatives.insert_one(sr_doc)

    print(f"\n  '{firstname} {lastname}' added as a sales representative.")
    print("  Enter the customers this rep will serve.")
    print("  (Leave customer name blank when finished.)\n")

    while True:
        cust_name = input("  Customer name (blank to stop): ").strip()
        if not cust_name:
            break

        customer = db.customers.find_one({"customername": cust_name})
        if not customer:
            print(f"    Customer '{cust_name}' not found. Skipping.")
            continue

        # Update the customer's embedded salesrep reference
        db.customers.update_one(
            {"_id": customer["_id"]},
            {"$set": {"salesrep": {"lastname": lastname, "firstname": firstname}}}
        )

        # Add customer to the sales rep's customers list (Warning requirement)
        db.sales_representatives.update_one(
            {"_id": emp_num},
            {"$addToSet": {"customers": {
                "customernumber": customer["_id"],
                "customername":   cust_name
            }}}
        )
        print(f"    Linked: '{cust_name}' now served by {firstname} {lastname}.")


# ════════════════════════════════════════════════════════════════════════════
# TASK 4c — REPORTS
# ════════════════════════════════════════════════════════════════════════════

# ── Helper: recursive hierarchy printer ─────────────────────────────────────

def _print_hierarchy(db, lastname, firstname, indent=0):
    """
    Recursively prints all employees below the given employee.
    Each level is indented by 4 spaces.
    """
    prefix = "    " * indent + ("└── " if indent > 0 else "")
    print(f"{prefix}{firstname} {lastname}")

    # Find everyone who reports directly to this person
    direct_reports = db.employees.find({
        "reportsto.lastname":  lastname,
        "reportsto.firstname": firstname
    })

    for emp in direct_reports:
        _print_hierarchy(db, emp["lastname"], emp["firstname"], indent + 1)


def employee_hierarchy_report(db):
    """
    Prompts for a starting employee, then prints the full reporting
    hierarchy beneath them in a tree-style format.
    """
    print("\n--- Employee Hierarchy Report ---")

    last  = input("Starting employee last name: ").strip()
    first = input("Starting employee first name: ").strip()

    root = db.employees.find_one({"lastname": last, "firstname": first})
    if not root:
        print(f"Employee '{first} {last}' not found. Returning to menu.")
        return

    print(f"\n  Hierarchy starting from {first} {last}:\n")
    _print_hierarchy(db, last, first)
    print()


# ── Order report ─────────────────────────────────────────────────────────────

def order_report(db):
    """
    Prompts for a customer name and order date, then displays all products
    in that order sorted alphabetically by productcode, with a total.
    """
    print("\n--- Order Report ---")

    cust_name = input("Customer name: ").strip()
    date_str  = input("Order date (YYYY-MM-DD): ").strip()

    try:
        order_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Returning to menu.")
        return

    order = db.orders.find_one({
        "customer.customername": cust_name,
        "orderdate":             order_date
    })

    if not order:
        print(f"No order found for '{cust_name}' on {date_str}. Returning to menu.")
        return

    # Sort details alphabetically by productcode
    details = sorted(order.get("details", []), key=lambda d: d["product"]["productcode"])

    print(f"\n  Order for: {cust_name}")
    print(f"  Order date: {order_date.strftime('%Y-%m-%d')}")
    print(f"  Status: {order['status']}")
    print(f"\n  {'Product Code':<15} {'Product Name':<45} {'Qty':>5}  {'Price Each':>12}  {'Line Total':>12}")
    print("  " + "-" * 95)

    order_total = 0.0
    for item in details:
        code     = item["product"]["productcode"]
        name     = item["product"]["productname"]
        qty      = item["quantityordered"]
        price    = item["priceeach"]
        subtotal = qty * price
        order_total += subtotal
        print(f"  {code:<15} {name:<45} {qty:>5}  ${price:>11.2f}  ${subtotal:>11.2f}")

    print("  " + "-" * 95)
    print(f"  {'ORDER TOTAL':>77}  ${order_total:>11.2f}")
    print()


# ════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('Starting Classic Models application...')

    main_action = ''
    while main_action != menu_main.last_action():
        main_action = menu_main.menu_prompt()
        exec(main_action)

    print('Ending normally.')
