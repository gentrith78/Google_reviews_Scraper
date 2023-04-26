import random
import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

try:
    from .helper import AttrHelpers,Contact
    from .xpath_finder import xpath_soup
    from .review_analyser import find_contact_info
except:
    from helper import AttrHelpers, Contact
    from xpath_finder import xpath_soup
    from review_analyser import find_contact_info

attr_helpers = AttrHelpers()

def get_phone(driver):

    pass

if __name__ == '__main__':
    with open('sample.txt','r',encoding='utf8') as f:
        html_data = f.read()
        pass