import requests
from bs4 import BeautifulSoup

def scrape_vero():
    base_url = "https://pricelist.vero.com.mk/89_{}.html"
    product_data = []
    page = 1

    while True:
        url = base_url.format(page)
        print(f"Scraping Vero – Page {page}: {url}")

        response = requests.get(url)
        if response.status_code != 200:
            print(f"No page found at {url}. Stopping.")
            break

        soup = BeautifulSoup(response.content, "html.parser")
        trs = soup.find_all("tr")
        if not trs:
            print("No more rows. Stopping.")
            break

        # Skip header row
        for tr in trs[1:]:
            tds = tr.find_all("td")
            cells = [td.get_text(strip=True) for td in tds]

            if len(cells) >= 2:
                name = cells[0]
                price = cells[1]

                # Skip if header-like or price is not numeric
                if "ценовник" in name.lower() or not price.isdigit():
                    continue

                product = {
                    "ime_na_artikal": name,
                    "cena": price,
                    "opis": cells[4] if len(cells) >= 5 else "",
                    "market": "Vero"
                }
                product_data.append(product)

        page += 1

    return product_data
