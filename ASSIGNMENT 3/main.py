from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Initial product list
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

# Model for new product
class NewProduct(BaseModel):
    name: str
    price: float
    category: str
    in_stock: bool = True


# Helper function to find product
def find_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


# GET all products
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}

@app.get("/products/audit")
def products_audit():

    total_products = len(products)

    in_stock_products = [p for p in products if p["in_stock"]]
    in_stock_count = len(in_stock_products)

    out_of_stock_names = [p["name"] for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in products if p["in_stock"])

    most_expensive_product = max(products, key=lambda p: p["price"])

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_names": out_of_stock_names,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive_product["name"],
            "price": most_expensive_product["price"]
        }
    }


# GET product by id
@app.get("/products/{product_id}")
def get_product(product_id: int, response: Response):
    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    return product


# POST add product
@app.post("/products")
def add_product(new_product: NewProduct, response: Response):

    # Check duplicate name
    for p in products:
        if p["name"].lower() == new_product.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Product with this name already exists"}

    next_id = max(p["id"] for p in products) + 1

    product = {
        "id": next_id,
        "name": new_product.name,
        "price": new_product.price,
        "category": new_product.category,
        "in_stock": new_product.in_stock
    }

    products.append(product)

    response.status_code = status.HTTP_201_CREATED
    return {
        "message": "Product added",
        "product": product
    }


# PUT update product
@app.put("/products/discount")
def apply_discount(category: str, discount_percent: int):

    if discount_percent < 1 or discount_percent > 99:
        return {"error": "discount_percent must be between 1 and 99"}

    updated_products = []

    for product in products:
        if product["category"].lower() == category.lower():

            new_price = int(product["price"] * (1 - discount_percent / 100))
            product["price"] = new_price

            updated_products.append({
                "name": product["name"],
                "new_price": new_price
            })

    if not updated_products:
        return {"message": f"No products found in category '{category}'"}

    return {
        "category": category,
        "discount_applied": f"{discount_percent}%",
        "products_updated": len(updated_products),
        "updated_products": updated_products
    }

@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    response: Response = None
):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return {
        "message": "Product updated",
        "product": product
    }


# DELETE product
@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    products.remove(product)

    return {"message": f"Product '{product['name']}' deleted"}
