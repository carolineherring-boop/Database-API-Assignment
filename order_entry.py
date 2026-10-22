"""
DATA 4000 - Create and Verify Customer Orders with Python and Supabase

Run with:  python order_entry.py

1. Loads customers and products from Supabase and shows them as tables.
2. Asks for a customer ID, product ID, and quantity, re-prompting on bad input.
3. Shows an order summary and asks Y/N before saving.
4. Inserts the order, then queries Supabase again to verify it was saved.
5. Offers to enter another order until the user chooses to exit.

All API calls go through database.py (supplied in class).
"""

from decimal import Decimal

import database


# ---------- display helpers ----------

def money(value):
    """Format a price from the database as dollars with two decimals."""
    return f"${Decimal(str(value)):,.2f}"


def print_table(headers, rows):
    """Print rows as a simple text table with columns sized to fit."""
    widths = [len(h) for h in headers]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(str(value)))

    line = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    print(line)
    print("| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |")
    print(line)
    for row in rows:
        print("| " + " | ".join(str(v).ljust(widths[i]) for i, v in enumerate(row)) + " |")
    print(line)


def show_customers(customers):
    print("\nCUSTOMERS")
    print_table(["Customer ID", "Customer Name"],
                [(c["customer_id"], c["name"]) for c in customers])


def show_products(products):
    print("\nPRODUCTS")
    print_table(["Product ID", "Product Name", "Price"],
                [(p["product_id"], p["product_name"], money(p["price"])) for p in products])


# ---------- input validation ----------

def ask_existing_id(prompt, valid_ids, label):
    """Ask until the user types an integer that is one of valid_ids."""
    while True:
        text = input(prompt).strip()
        try:
            value = int(text)
        except ValueError:
            print(f"'{text}' is not a valid {label} ID. Please enter a whole number from the table.")
            continue
        if value not in valid_ids:
            print(f"There is no {label} with ID {value}. Please choose an ID from the table.")
            continue
        return value


def ask_quantity():
    """Ask until the user types a positive whole number."""
    while True:
        text = input("Quantity to purchase: ").strip()
        try:
            value = int(text)
        except ValueError:
            print(f"'{text}' is not a whole number. Please enter a quantity like 1, 2, or 3.")
            continue
        if value <= 0:
            print("Quantity must be greater than 0.")
            continue
        return value


def ask_yes_no(prompt):
    """Return True for Y/y and False for N/n; re-prompt on anything else."""
    while True:
        answer = input(prompt).strip().upper()
        if answer == "Y":
            return True
        if answer == "N":
            return False
        print("Please enter Y or N.")


# ---------- one order ----------

def show_summary(customer, product, quantity):
    price = Decimal(str(product["price"]))
    print("\nORDER SUMMARY")
    print(f"  Customer:    {customer['name']}")
    print(f"  Product:     {product['product_name']}")
    print(f"  Quantity:    {quantity}")
    print(f"  Unit price:  {money(price)}")
    print(f"  Order total: {money(price * quantity)}")


def show_saved_order(order):
    """Print the order row returned by the verification query."""
    unit_price = Decimal(str(order["unit_price"]))
    print("\nSAVED ORDER (retrieved from Supabase)")
    print_table(
        ["Order ID", "Customer", "Product", "Quantity", "Unit Price", "Total", "Order Date"],
        [(
            order["order_id"],
            order["customers"]["name"],
            order["products"]["product_name"],
            order["quantity"],
            money(unit_price),
            money(unit_price * order["quantity"]),
            order["order_date"],
        )],
    )


def enter_one_order(customers_by_id, products_by_id):
    """Collect, confirm, save, and verify a single order."""
    customer_id = ask_existing_id("\nEnter a customer ID: ", customers_by_id, "customer")
    product_id = ask_existing_id("Enter a product ID: ", products_by_id, "product")
    quantity = ask_quantity()

    show_summary(customers_by_id[customer_id], products_by_id[product_id], quantity)

    if not ask_yes_no("\nConfirm this order? (Y/N): "):
        print("Order cancelled. Nothing was saved.")
        return

    # create_order reads the current price from Supabase and the database
    # generates order_id, so the user never types either one.
    try:
        saved = database.create_order(customer_id, product_id, quantity)
    except Exception:
        print("Sorry, the order could not be saved because the database request failed.")
        return
    print(f"\nOrder saved successfully. New order ID: {saved['order_id']}")

    # Verify with a brand-new query instead of trusting the insert response.
    try:
        verified = database.get_order(saved["order_id"])
    except Exception:
        print("Verification could not be completed because the database request failed.")
        return
    if verified is None:
        print("Verification could not be completed: no matching order was found.")
        return
    show_saved_order(verified)


# ---------- main ----------

def main():
    print("=== Customer Order Entry ===")
    try:
        customers = database.get_customers()
        products = database.get_products()
    except ValueError as error:
        # config.py raises ValueError with a safe message when .env is incomplete.
        print(f"Configuration problem: {error}")
        return
    except Exception:
        print("Could not load data from Supabase. Check your .env settings and internet connection.")
        return

    customers_by_id = {c["customer_id"]: c for c in customers}
    products_by_id = {p["product_id"]: p for p in products}

    while True:
        show_customers(customers)
        show_products(products)
        enter_one_order(customers_by_id, products_by_id)
        if not ask_yes_no("\nWould you like to enter another order? (Y/N): "):
            break

    print("Goodbye!")


if __name__ == "__main__":
    main()
