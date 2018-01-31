import os
import io
import urllib.parse
from bs4 import BeautifulSoup
import logging

import selenium
import yaml
from prettytable import PrettyTable
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                    )

def get_params():
    config_f_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yml')
    with io.open(config_f_path, 'r', encoding='utf-8') as stream:
        configs = yaml.load(stream)
        return configs



def get_jd_products():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')  # Last I checked this was necessary.
    driver = webdriver.Chrome(chrome_options=options)
    params_dict = get_params()['QueryParams']
    query_params = urllib.parse.urlencode(params_dict)
    url = "https://list.jd.com/list.html?" + query_params
    driver.get(url)
    logging.info("Getting page {}".format(url))
    page_doc = driver.page_source
    soup = BeautifulSoup(page_doc, 'lxml')
    page_count = int(soup.select('span.p-skip > em:nth-of-type(1) > b')[0].get_text())
    logging.info("There are total {} pages".format(page_count))
    for page_index in range(1, page_count+1):
        if page_index == 1:
            product_list = soup.select('div#plist > ul > li')
            logging.info("Got products of Page No.{}".format(page_index))
        else:
            params_dict['page'] = page_index
            query_params = urllib.parse.urlencode(params_dict)
            url = "https://list.jd.com/list.html?" + query_params
            driver.get(url)
            logging.info("Getting page {}".format(url))
            page_doc = driver.page_source
            soup = BeautifulSoup(page_doc, 'lxml')
            product_list.extend(soup.select('div#plist > ul > li'))
            logging.info("Got products of Page No.{}".format(page_index))

    for product in product_list:
        product_name = product.select('div > div[class~=p-name]')[0].get_text().strip().split('\n')[0].strip()
        product_price = product.select('div > div.p-price > strong.J_price > i')[0].get_text()
        yield {
            'product_name': product_name,
            'product_price': product_price
        }

table = PrettyTable(['产品名称','价格'])
table.align['产品名称'] = 'l'
table.align['价格'] = 'r'
for product in get_jd_products():
    table.add_row([product['product_name'], product['product_price']])
print(table)