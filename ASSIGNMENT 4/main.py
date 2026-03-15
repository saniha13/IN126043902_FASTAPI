from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# -------------------------
# Products Database
# -------------------------

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 299, "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "in_stock": True},
]

cart = []
orders = []
order_id_counter = 1


# -------------------------
# Request Model
# -------------------------

class Checkout(BaseModel):
    customer_name: str
    delivery_address: str


# -------------------------
# Add to Cart
# -------------------------

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f'{product["name"]} is out of stock')

    existing = next((item for item in cart if item["product_id"] == product_id), None)

    if existing:
        existing["quantity"] += quantity
        existing["subtotal"] = existing["quantity"] * existing["unit_price"]

        return {
            "message": "Cart updated",
            "cart_item": existing
        }

    item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": product["price"] * quantity
    }

    cart.append(item)

    return {
        "message": "Added to cart",
        "cart_item": item
    }


# -------------------------
# View Cart
# -------------------------

@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }


# -------------------------
# Remove Item
# -------------------------

@app.delete("/cart/{product_id}")
def remove_item(product_id: int):

    global cart

    item = next((item for item in cart if item["product_id"] == product_id), None)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    cart = [item for item in cart if item["product_id"] != product_id]

    return {"message": "Item removed from cart"}


# -------------------------
# Checkout
# -------------------------

@app.post("/cart/checkout")
def checkout(data: Checkout):

    global order_id_counter
    global cart

    if not cart:
        raise HTTPException(status_code=400, detail="CART_EMPTY")

    orders_placed = []

    for item in cart:

        order = {
            "order_id": order_id_counter,
            "customer_name": data.customer_name,
            "delivery_address": data.delivery_address,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "subtotal": item["subtotal"]
        }

        orders.append(order)
        orders_placed.append(order)

        order_id_counter += 1

    grand_total = sum(item["subtotal"] for item in cart)

    cart = []

    return {
        "message": "Checkout successful",
        "orders_placed": orders_placed,
        "grand_total": grand_total
    }


# -------------------------
# View Orders
# -------------------------

@app.get("/orders")
def view_orders():

    return {
        "orders": orders,
        "total_orders": len(orders)
    }
