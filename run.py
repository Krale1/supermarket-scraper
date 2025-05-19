from flask import Flask, render_template
from app.scraper.ramstore import scrape_ramstore
from app.scraper.tinex import scrape_tinex
from app.scraper.vero import scrape_vero
from app.database.crud import save_products
from app.database.crud import get_all_products
from flask import request
from dotenv import load_dotenv
load_dotenv()



app = Flask(__name__)

@app.route("/")
def home():
    return {"message": "Supermarket Scraper is live!"}

@app.route("/scrape/ramstore")
def scrape():
    data = scrape_ramstore()[:100]  
    return render_template("ramstore_table.html", products=data)

@app.route("/scrape/vero")
def scrape_vero_route():
    data = scrape_vero()[:100]
    return render_template("ramstore_table.html", products=data)


@app.route("/scrape/tinex")
def scrape_tinex_route():
    data = scrape_tinex()[:100]
    return render_template("ramstore_table.html", products=data)

from app.database.crud import delete_all_products

@app.route("/save/all")
def save_all():
    delete_all_products()
    data = scrape_ramstore() + scrape_tinex() + scrape_vero()
    save_products(data)
    return {"status": "Refreshed MySQL DB", "count": len(data)}


from math import ceil
from app.database.crud import get_all_products, count_products

@app.route("/scrape/all")
def display_from_db():
    query = request.args.get("q", "")
    sort_field = request.args.get("sort", "price")
    order = request.args.get("order", "asc")
    page = int(request.args.get("page", 1))
    per_page = 20
    offset = (page - 1) * per_page

    total = count_products(search=query)
    total_pages = ceil(total / per_page)

    data = get_all_products(
        search=query,
        sort_by=sort_field,
        order=order,
        limit=per_page,
        offset=offset
    )

    page_list = generate_page_list(page, total_pages)

    return render_template(
    "ramstore_table.html",
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
        if (
            p == 1 or
            p == 2 or
            p == total_pages - 1 or
            p == total_pages or
            abs(p - current_page) <= 2
        ):
            pages.append(p)
        elif pages[-1] != "...":
            pages.append("...")

    return pages


if __name__ == "__main__":
    app.run(debug=True)
