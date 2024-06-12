import tkinter as tk
from tkinter import messagebox
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="siva",
    database="inventory"
)

cursor = conn.cursor()


root = tk.Tk()
root.title("INVENTORY MANAGEMENT")
root.geometry('800x800')
root.configure(bg="grey")

class Product:
    def __init__(self, name, price_inr):
        self.name = name
        self.price_inr = price_inr

class Order:
    def __init__(self):
        self.items = []

    def add_item(self, item, quantity):
        self.items.append({"item": item, "quantity": quantity})

    def calculate_total(self):
        total = 0
        for order_item in self.items:
            total += order_item["item"].price_inr * order_item["quantity"]
        return total

    def clear(self):
        self.items = []

class Inventory:
    def __init__(self):
        self.products = []
        self.load_products_from_db()

    def add_product(self, item):
        self.products.append(item)
        self.save_product_to_db(item)

    def save_product_to_db(self, item):
        cursor.execute("INSERT INTO product (name, price_inr) VALUES (%s, %s)", (item.name, item.price_inr))
        conn.commit()

    def load_products_from_db(self):
        cursor.execute("SELECT * FROM product")
        rows = cursor.fetchall()
        self.products.clear()
        for row in rows:
            self.products.append(Product(row[1], row[2]))

    def update_product(self, item_name, new_price):
        cursor.execute("UPDATE product SET price_inr = %s WHERE name = %s", (new_price, item_name))
        conn.commit()
        self.load_products_from_db()

    def delete_product(self, item_name):
        cursor.execute("DELETE FROM product WHERE name = %s", (item_name,))
        conn.commit()
        self.load_products_from_db()

    def display_products(self):
        products_text = "Products:\n"
        for i, item in enumerate(self.products):
            products_text += f"{i+1}. {item.name} - ₹{item.price_inr}\n"
        return products_text

inventory = Inventory()
order = Order()

def order_item():
    try:
        choice_index = int(choice_entry.get()) - 1
        quantity = int(quantity_entry.get())

        if choice_index < 0 or choice_index >= len(inventory.products):
            raise ValueError("Invalid choice. Please enter a valid item number.")

        if quantity <= 0:
            raise ValueError("Invalid quantity. Quantity must be greater than 0.")

        item = inventory.products[choice_index]
        order.add_item(item, quantity)
        order_text.insert(tk.END, f"{quantity} {item.name}(s) added to your order.\n")
    except ValueError as e:
        order_text.insert(tk.END, f"Error: {e}\n")

def display_products():
    order_text.delete('1.0', tk.END)
    products_text = inventory.display_products()
    order_text.insert(tk.END, products_text)

def display_bill():
    total_bill_inr = order.calculate_total()
    order_text.insert(tk.END, f"\nTotal Bill: ₹{total_bill_inr:.2f}\n")
    order_text.insert(tk.END, "Visit again!\n")
    save_bill_to_db(total_bill_inr)
    order.clear()

def clear_order():
    order_text.delete('1.0', tk.END)
    order.clear()

def add_product():
    name = product_name_entry.get()
    price = product_price_entry.get()
    try:
        price = float(price)
        new_item = Product(name, price)
        inventory.add_product(new_item)
        product_name_entry.delete(0, tk.END)
        product_price_entry.delete(0, tk.END)
        messagebox.showinfo("Success", "Product added successfully!")
    except ValueError:
        messagebox.showerror("Error", "Invalid price. Please enter a numeric value.")

def update_product():
    name = product_name_entry.get()
    price = product_price_entry.get()
    try:
        price = float(price)
        inventory.update_product(name, price)
        product_name_entry.delete(0, tk.END)
        product_price_entry.delete(0, tk.END)
        messagebox.showinfo("Success", "Product updated successfully!")
    except ValueError:
        messagebox.showerror("Error", "Invalid price. Please enter a numeric value.")

def delete_product():
    name = product_name_entry.get()
    inventory.delete_product(name)
    product_name_entry.delete(0, tk.END)
    product_price_entry.delete(0, tk.END)
    messagebox.showinfo("Success", "Product deleted successfully!")

def save_bill_to_db(total_bill_inr):
    cursor.execute("INSERT INTO bills (amount) VALUES (%s)", (total_bill_inr,))
    conn.commit()

# GUI components
menu_label = tk.Label(root, text="Enter the number of the product you want to order:", bg="lightgreen")
menu_label.grid(row=0, column=0, sticky="w", padx=20, pady=10)

choice_entry = tk.Entry(root)
choice_entry.grid(row=0, column=1, padx=20)

quantity_label = tk.Label(root, text="Enter the quantity:", bg="lightgreen")
quantity_label.grid(row=1, column=0, sticky="w", padx=20, pady=10)

quantity_entry = tk.Entry(root)
quantity_entry.grid(row=1, column=1, padx=20)

order_button = tk.Button(root, text="Order", bg="yellow", command=order_item)
order_button.grid(row=2, column=0, columnspan=2, pady=10)

menu_display_button = tk.Button(root, text="Display Products", bg="yellow", command=display_products)
menu_display_button.grid(row=3, column=0, columnspan=2, pady=10)

order_text = tk.Text(root, width=60, height=20)
order_text.grid(row=4, column=0, columnspan=2, padx=20, pady=10)

calculate_button = tk.Button(root, text="Display Bill", bg="yellow", command=display_bill)
calculate_button.grid(row=5, column=0, columnspan=2, pady=10)

clear_button = tk.Button(root, text="Clear Order", bg="yellow", command=clear_order)
clear_button.grid(row=6, column=0, columnspan=2, pady=10)

# Additional GUI components for CRUD operations
product_name_label = tk.Label(root, text="Product Name:", bg="lightgreen")
product_name_label.grid(row=1, column=2, sticky="w", padx=20, pady=10)

product_name_entry = tk.Entry(root)
product_name_entry.grid(row=2, column=2, padx=20)

product_price_label = tk.Label(root, text="Product Price:", bg="lightgreen")
product_price_label.grid(row=1, column=3, sticky="w", padx=20, pady=10)

product_price_entry = tk.Entry(root)
product_price_entry.grid(row=2, column=3, padx=20)

add_product_button = tk.Button(root, text="Add Product", bg="lightgreen", command=add_product)
add_product_button.grid(row=4, column=2, columnspan=2, pady=5)

update_product_button = tk.Button(root, text="Update Product", bg="lightblue", command=update_product)
update_product_button.grid(row=5, column=2, columnspan=2, pady=5)

delete_product_button = tk.Button(root, text="Delete Product", bg="lightcoral", command=delete_product)
delete_product_button.grid(row=6, column=2, columnspan=2, pady=5)

root.mainloop()

# Close the database connection when the application closes
conn.close()
