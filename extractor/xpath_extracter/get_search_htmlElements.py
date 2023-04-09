import time

from bs4 import BeautifulSoup

try:
    from .xpath_finder import xpath_soup
    from .helper import AttrHelpers
except:
    from xpath_finder import xpath_soup
    from helper import AttrHelpers

attrhelpers = AttrHelpers

def get_search_html_elements(html_data):
    soup = BeautifulSoup(html_data,features='html.parser')

    try:
        search_area_xpath = xpath_soup(soup.find('textarea',AttrHelpers.search_field_attr))
    except:
        time.sleep(1000)

    return search_area_xpath

def get_more_places_button(html_data):
    soup = BeautifulSoup(html_data,features='html.parser')

    spans = soup.find_all('span')
    for span in spans:
        if span.text == 'More places':
            return xpath_soup(span)


if __name__ == '__main__':
    with open('sample.txt','r',encoding='utf8') as f:
        html_data = f.read()
        print(get_more_places_button(html_data))