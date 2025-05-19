import requests
from bs4 import BeautifulSoup

def scrape_tinex():
    base_url = "http://ceni.tinex.mk/"
    product_data = []
    page = 1

    while page <= 61:  # ✅ Fixed max page

        print(f"Scraping Tinex – Page {page}")  # Debug output

        params = {
            "org": "512",
            "search": "",
            "perPage": "100",
            "page": str(page)
        }
        response = requests.get(base_url, params=params)
        soup = BeautifulSoup(response.content, "html.parser")

        table = soup.find("table")
        if not table:
            print("No table found, stopping.")
            break

        rows = table.find_all("tr")[1:]
        if not rows:
            print("No rows found on page", page)
            break

        for row in rows:
            cells = row.find_all("td")
            values = [cell.get_text(strip=True) for cell in cells]
            if len(values) >= 4:
                product = {
                    "ime_na_artikal": values[0],
                    "cena": values[1],
                    "opis": values[3],
                    "market": "Tinex"
                }
                product_data.append(product)

        page += 1

    return product_data
