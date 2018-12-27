import requests
from bs4 import BeautifulSoup
import random


# scrape and gets ip proxy
def get_proxy_list():
    url = "https://free-proxy-list.net/"
    source = requests.get(url).text
    soup = BeautifulSoup(source, "lxml")
    proxy_list_table = soup.select("#proxylisttable")
    proxy_list_table = proxy_list_table[0]
    proxy_list_table_body = proxy_list_table.select("tbody")[0]
    proxies = proxy_list_table_body.select("tr")
    proxy_list = list()
    for proxy in proxies:
        proxy_data = proxy.select("td")
        ip = proxy_data[0].text
        port = proxy_data[1].text
        proxy_list.append(ip + ":" + port)

    return proxy_list


# gets html code
def get_source(base_url, asin, proxy_list):
    proxies = {
        "http": random.choice(proxy_list),
        "https": random.choice(proxy_list)
    }

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) ' \
                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    headers = {'User-Agent': user_agent}

    while True:
        try:
            source = requests.get(base_url + asin, proxies=proxies, headers=headers).text
            break
        except:
            proxies = {
                "http": random.choice(proxy_list),
                "https": random.choice(proxy_list)
            }

    return source


# gets product title and price from html
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
    asin_list = ["B01EU2M62S", "B07DDB1ZN1", "B07JCSNXJ6"]
    proxy_list = get_proxy_list()
    for asin in asin_list:
        source = get_source(base_url, asin, proxy_list)
        print(get_info(source))
        print()
