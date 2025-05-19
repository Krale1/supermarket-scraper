import requests
from bs4 import BeautifulSoup

def scrape_ramstore():
    url = "https://ramstore.com.mk/marketi/ramstore-siti-mol/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    product_data = []

    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows[1:]: 
            cells = row.find_all("td")
            values = [cell.get_text(strip=True) for cell in cells]
            if len(values) >= 4:
                product = {
                    "ime_na_artikal": values[0],  
                    "cena": values[1],            
                    "opis": values[3],            
                    "market": "Ramstore"
                }
                product_data.append(product)

    return product_data
