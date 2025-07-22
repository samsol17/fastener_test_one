from bs4 import BeautifulSoup
import requests

url = "https://www.grainger.com/category/fasteners/washers/flat-washers?attrs=Material%7CTitanium&filters=attrs&searchQuery=Flat+Washer&sst=4&tv_optin=true&gwwRemoveElement=true"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
print("hi")


rows = soup.select('tr[aria-label^="Product"]')
for row in rows:
    print("count")
    cells = row.find_all('td')
    size = cells[0].get('title')
    inside_dia = cells[1].get('title')
    outside_dia = cells[2].get('title')
    thickness = cells[3].get('title')
    standard = cells[4].get('title')
    price = cells[5].find('span', class_='O6u-EO').text.strip()
    sku_link = cells[5].find('a')
    sku = sku_link.text.strip()
    product_url = "https://www.grainger.com" + sku_link.get('href')

    print(f"SKU: {sku}, Price: {price}, Size: {size}, URL: {product_url}")
