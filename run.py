import os
import pandas as pd
from flask import Flask, render_template, request, session, redirect, url_for
from dotenv import load_dotenv

from app.scraper.ramstore import scrape_ramstore
from app.scraper.tinex import scrape_tinex
from app.scraper.vero import scrape_vero
from app.database.crud import save_products, get_all_products, delete_all_products, count_products

load_dotenv()

app = Flask(__name__)
app.secret_key = 'super-secret-key'

# Load grouped products from CSV once when server starts
grouped_df = pd.read_csv('grouped_products.csv')
grouped_products = grouped_df.groupby('base_product').apply(lambda g: g.to_dict('records')).to_dict()

@app.route("/")
def home():
    query = request.args.get("q", "").lower()
    results = {name: markets for name, markets in grouped_products.items() if query in name.lower()}
    return render_template("home.html", products=results)

@app.route("/add_to_cart/<product_name>")
def add_to_cart(product_name):
    cart = session.get("cart", [])
    cart.append(product_name)
    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    cart = session.get("cart", [])
    market_totals = {}
    cart_items = []

    for name in cart:
        markets = grouped_products.get(name, [])
        cart_items.append({"name": name, "markets": markets})

        for market in markets:
            market_name = market['market']
            market_totals[market_name] = market_totals.get(market_name, 0) + market['average_price']

    return render_template("cart.html", cart_items=cart_items, market_totals=market_totals)

@app.route("/scrape/ramstore")
def scrape_ramstore_route():
    data = scrape_ramstore()[:100]
    return render_template("home.html", products=data)

@app.route("/scrape/vero")
def scrape_vero_route():
    data = scrape_vero()[:100]
    return render_template("home.html", products=data)

@app.route("/scrape/tinex")
def scrape_tinex_route():
    data = scrape_tinex()[:100]
    return render_template("home.html", products=data)

@app.route("/save/all")
def save_all():
    delete_all_products()
    data = scrape_ramstore() + scrape_tinex() + scrape_vero()
    save_products(data)
    return {"status": "Refreshed MySQL DB", "count": len(data)}

@app.route("/scrape/all")
def display_from_db():
    query = request.args.get("q", "")
    sort_field = request.args.get("sort", "price")
    order = request.args.get("order", "asc")
    page = int(request.args.get("page", 1))
    per_page = 20
    offset = (page - 1) * per_page

    total = count_products(search=query)
    total_pages = (total + per_page - 1) // per_page

    data = get_all_products(
        search=query,
        sort_by=sort_field,
        order=order,
        limit=per_page,
        offset=offset
    )

    page_list = generate_page_list(page, total_pages)

    return render_template(
        "home.html",
        products=data,
        current_sort=sort_field,
        current_order=order,
        current_page=page,
        total_pages=total_pages,
        page_list=page_list
    )

def generate_page_list(current_page, total_pages):
    pages = []
    for p in range(1, total_pages + 1):
        if p == 1 or p == 2 or p == total_pages - 1 or p == total_pages or abs(p - current_page) <= 2:
            pages.append(p)
        elif pages[-1] != "...":
            pages.append("...")
    return pages

@app.route("/remove_from_cart/<product_name>")
def remove_from_cart(product_name):
    cart = session.get("cart", [])
    if product_name in cart:
        cart.remove(product_name)
    session["cart"] = cart
    return redirect(url_for("cart"))


if __name__ == "__main__":
    app.run(debug=True)
