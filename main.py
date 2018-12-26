import requests
from bs4 import BeautifulSoup


# https://www.amazon.in/dp/B01EU2M62S
def get_source(base_url, asin):
    source = requests.get(base_url + asin).text
    return source


def get_info(source):
    soup = BeautifulSoup(source, "lxml")

    # get title
    product_title = soup.select('#productTitle')
    product_title = str.strip(product_title[0].text)

    

    return [product_title]


if __name__ == "__main__":
    base_url = "https://www.amazon.in/dp/"
    asin_list = ["B01EU2M62S", "B07DDB1ZN1"]
    for asin in asin_list:
        source = get_source(base_url, asin)
        print(get_info(source))
        print()
