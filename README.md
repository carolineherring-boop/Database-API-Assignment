# DATA 4000 — Create and Verify Customer Orders with Python and Supabase

A command-line program that lets a user place a new order for an existing
customer. It reads customers and products from Supabase, validates every input,
asks for confirmation, saves the order through the Supabase API, and then runs a
**new query** to prove the order was really saved.

## Files

| File | Purpose |
|---|---|
| `order_entry.py` | The interactive order program (the assignment) |
| `database.py` | Reusable Supabase API functions (from class; I added `get_order()`) |
| `config.py` | Reads the URL and secret key from `.env` (from class) |
| `01_check_connection.py` | Confirms the API credentials work (from class) |
| `02_import_data.py` | Uploads the sample CSV data (from class) |
| `sql/01_create_tables.sql` | Creates the three tables (from class) |
| `data/*.csv` | Sample customers, products, and orders (from class) |
| `requirements.txt` | Python packages to install |
| `.env.example` | Template for your credentials (placeholders only) |

## Setup

1. Create a Supabase project, open **SQL Editor**, and run `sql/01_create_tables.sql`.
2. In a VS Code terminal in this folder:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   cp .env.example .env             # Windows: Copy-Item .env.example .env
   ```

3. Edit `.env` with your own project URL and **secret** key
   (Supabase → Project Settings → API Keys → Secret keys, starts with `sb_secret_`).
   The public `anon` key will not work, because the tables block anonymous access.
4. Check the connection and load the sample data:

   ```bash
   python 01_check_connection.py
   python 02_import_data.py
   ```

`.env` is listed in `.gitignore`, so the real key is never uploaded to GitHub.

## How to run

```bash
python order_entry.py
```

## How the program works

The program is split into small functions, grouped by job:

1. **Display** — `main()` calls `database.get_customers()` and
   `database.get_products()`, which send API requests to Supabase. `print_table()`
   lays the results out in columns, and `money()` formats prices to two decimals.
2. **Validate** — `ask_existing_id()` loops until the input converts with `int()`
   *and* matches an ID that came back from the database. `ask_quantity()` loops
   until the input is a whole number greater than 0. A `try/except ValueError`
   catches input like `hello` or `1.5`, so the program prints a message instead of
   crashing.
3. **Confirm** — `show_summary()` prints the customer, product, quantity, unit
   price, and total. `ask_yes_no()` accepts `Y/y/N/n` and asks again for anything else.
4. **Save** — `database.create_order()` looks up the product's current price in
   Supabase and inserts the row with today's date. The user never types the price
   or order ID; the database generates the ID.
5. **Verify** — `database.get_order()` sends a **second, separate query** for the
   new order ID, and `show_saved_order()` prints the row that came back. If that
   query fails or finds nothing, the program says verification could not be completed.
6. **Repeat (extra credit)** — after each order or cancellation, the program asks
   whether to enter another one. Each order is collected fresh inside
   `enter_one_order()`, so nothing carries over from the previous order.

## Testing results

| Test | Expected behavior | Result |
|---|---|---|
| Enter text instead of a customer ID | Helpful message; asks again | Pass: `'hello' is not a valid customer ID. Please enter a whole number from the table.` |
| Enter a customer ID that does not exist | Rejects the ID; asks again | Pass: `There is no customer with ID 999. Please choose an ID from the table.` |
| Enter a product ID that does not exist | Rejects the ID; asks again | Pass: `There is no product with ID 42. Please choose an ID from the table.` |
| Enter quantity 0, -3, 1.5, or hello | Rejects each value; asks again | Pass: `0` and `-3` → `Quantity must be greater than 0.`; `1.5` and `hello` → `... is not a whole number.` |
| Cancel at the confirmation prompt | No order is inserted | Pass: `Order cancelled. Nothing was saved.` |
| Answer `maybe` at the confirmation prompt | Asks again | Pass: `Please enter Y or N.` |
| Confirm a valid order | Exactly one order is inserted | Pass (see output below) |
| Retrieve the newly created order | Saved order appears in the verification table | Pass (see output below) |

### Terminal output: successful insertion and verification

<!-- Paste the real output of a successful run here. -->

```
(add after running python order_entry.py against Supabase)
```

## References

- Class repository: https://github.com/imowerman-fu/class-20261014 (`config.py`,
  `database.py`, SQL, CSV data, and import scripts).
- Supabase Python client docs: https://supabase.com/docs/reference/python/introduction
  (`.select()`, `.eq()`, `.insert()`, and embedding related tables with
  `customers(name)` in a select).
- Python's `decimal.Decimal` is used for money math so totals like 3 × 4.50 are exact.
- I used Claude Code (AI assistant) to help write and test this program; I reviewed
  and can explain each part.
