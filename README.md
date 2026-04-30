# CECS 323 — Classic Models MongoDB Application

A menu-driven Python application for managing the Classic Models dataset stored in MongoDB. Supports adding orders and employees, browsing reports, and navigating a multi-level menu system.

## Requirements

- Python 3.8+
- MongoDB running locally on port 27017
- `pymongo` library

```bash
pip install pymongo
```

## Setup

1. Ensure MongoDB is running locally.
2. Import the Classic Models dataset into a database named `classicmodels_updated`.
3. Clone this repo and run:

```bash
python main.py
```

## Features

### Add
- **New Order** — Look up a customer, enter order/required dates, add one or more products (validated against inventory), and place the order. Inventory is decremented automatically.
- **New Employee** — Add an employee to an office, assign them as a Manager or Sales Representative, and link subordinates or customers accordingly.

### Reports
- **Employee Hierarchy** — Prints a recursive tree of the reporting structure starting from any employee.
- **Order Report** — Displays all line items for a given customer's order on a specific date, with a running total.

## Project Structure

| File | Purpose |
|------|---------|
| `main.py` | Application entry point and all business logic |
| `menu_definitions.py` | Static menu and option declarations |
| `Menu.py` | `Menu` class — renders options and returns selected action |
| `Option.py` | `Option` class — pairs a display prompt with an action string |
| `db_connection.py` | PyMongo client setup connecting to `classicmodels_updated` |

## Collections Used

- `customers` — customer records with embedded sales rep and order number references
- `orders` — orders with embedded customer info and line-item details
- `products` — product catalog with inventory quantities
- `employees` — employee records with embedded office and reports-to info
- `offices` — office locations with embedded employee lists
- `managers` — manager records with subordinate lists
- `sales_representatives` — sales rep records with customer lists
