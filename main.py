import requests
from bs4 import BeautifulSoup


# https://www.amazon.in/dp/B01EU2M62S
def get_source(base_url, asin):
    proxies = {
        "http": 'http://119.76.140.4:8080',
        "https": 'http://200.98.166.135:3128'
    }

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) ' \
                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    headers = {'User-Agent': user_agent}

    source = requests.get(base_url + asin, proxies=proxies, headers=headers).text
    return source


def get_info(source):
    soup = BeautifulSoup(source, "lxml")

    # get title
    product_title = soup.select('#productTitle')
    product_title = str.strip(product_title[0].text)

    # get price
    # this looks like bad programming, will keep an eye on it in future
    product_price = ""
    try:
        product_price = soup.select("#priceblock_saleprice")
        product_price = str.strip(product_price[0].text)
    except:
        try:
            product_price = soup.select("#priceblock_ourprice")
            product_price = str.strip(product_price[0].text)
        except:
            try:
                product_price = soup.select("#olp_feature_div")
                product_price = product_price[0].select(".a-color-price")
                product_price = str.strip(product_price[0].text)
            except:
                pass

    return [product_title, product_price]


if __name__ == "__main__":
    base_url = "https://www.amazon.in/dp/"
    # asin_list = ["B01EU2M62S"]
    asin_list = ["B01EU2M62S", "B07DDB1ZN1", "B07JCSNXJ6"]
    for asin in asin_list:
        source = get_source(base_url, asin)
        print(get_info(source))
        print()
