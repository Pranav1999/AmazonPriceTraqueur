import json
import os

from prettytable import PrettyTable


def print_logs():
    logs = ""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + "/AmazonPriceTraqueurLog.json", "r") as logs_file:
        logs = json.load(logs_file)

    table = PrettyTable(["ASIN", "Product Title", "Product Price", "Price Threshold", "Email status"])
    for asin in logs.keys():
        info = logs[asin]
        table.add_row([asin, info[0], info[1], info[2], info[3]])

    print(table)


print_logs()
