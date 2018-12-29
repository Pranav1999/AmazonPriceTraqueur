#!/usr/bin/python3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup
import random
import json
import os


def get_config():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + "/config.json") as f:
        return json.load(f)


def send_email(message, config_data):
    s = smtplib.SMTP(host=config_data["email"]["mailing_server"], port=config_data["email"]["mailing_server_port"])
    s.starttls()

    try:
        s.login(config_data["email"]["user_id"], config_data["email"]["user_password"])
    except:
        print(
            "Authentication failure, check ID/Password for mistake or check your account for third party authentication")
        return -1

    msg = MIMEMultipart()
    msg['From'] = config_data["email"]["user_id"]
    msg['To'] = config_data["email"]["user_id"]
    msg['Subject'] = "price drop"
    msg.attach(MIMEText(message, 'plain'))

    s.send_message(msg)
    s.quit()
    print("Email sent successfully")
    return 0


# returns a list of user agents
def get_user_agent_list():
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
        'Mozilla/5.0 (X11; U; Linux Core i7-4980HQ; de; rv:32.0; compatible; JobboerseBot; http://www.jobboerse.com/bot.htm) Gecko/20100101 Firefox/38.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Safari/604.1.38']

    return user_agents


# scrape and gets ip proxy
def get_proxy_list(user_agent_list):
    url = "https://free-proxy-list.net/"

    user_agent = random.choice(user_agent_list)
    headers = {'User-Agent': user_agent}
    try:
        source = requests.get(url, headers=headers).text
    except:
        print("Connection Error")
        exit(0)
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
def get_source(base_url, asin, proxy_list, user_agent_list):
    proxies = {
        "http": random.choice(proxy_list),
        "https": random.choice(proxy_list)
    }

    user_agent = random.choice(user_agent_list)
    headers = {'User-Agent': user_agent}

    while True:
        try:
            source = requests.get(base_url + asin, proxies=proxies, headers=headers).text
            if source.find("captcha") > 0:
                raise Exception("Captcha encountered")

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
    try:
        product_title = soup.select('#productTitle')
        product_title = str.strip(product_title[0].text)
    except:
        return ["Page not found", "Page not found"]

    # get price
    # this looks like bad programming, will keep an eye on it in future
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
                product_price = "Currently unavailable"

    return [product_title, product_price]


if __name__ == "__main__":
    config_data = get_config()
    base_url = config_data["base_url"]
    asin_list = config_data["items"]
    user_agent_list = get_user_agent_list()
    proxy_list = get_proxy_list(user_agent_list)

    logs_dict = dict()

    for asin in asin_list:
        source = get_source(base_url, asin, proxy_list, user_agent_list)
        info = get_info(source)
        print(info)

        log = info.copy()

        product_title = info[0]
        product_price = info[1]
        product_price = product_price.split('.')
        product_price = product_price[0]
        product_price = product_price.replace(',', '')
        if product_price.isdigit():
            if int(product_price) <= asin_list[asin]:
                email_msg = product_title + " is available at " + product_price + " bucks"
                email_status = send_email(email_msg, config_data)
                if email_status == 0:
                    log.append("email successful")
                else:
                    log.append("email unsuccessful")

            else:
                log.append("email not sent")

        else:
            log.append("email not sent")

        logs_dict[asin] = log

    with open("AmazonPriceTraqueur.json", "w") as log_file:
        json.dump(logs_dict, log_file)
