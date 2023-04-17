import time

from bs4 import BeautifulSoup

try:
    from .xpath_finder import xpath_soup
    from .helper import AttrHelpers
except:
    from xpath_finder import xpath_soup
    from helper import AttrHelpers

attrhelpers = AttrHelpers()

def get_search_html_elements(html_data):
    soup = BeautifulSoup(html_data,features='html.parser')

    try:
        search_area_xpath = xpath_soup(soup.find('textarea',AttrHelpers.search_field_attr))
    except:
        search_area_xpath = xpath_soup(soup.find('input',attrhelpers.get_second_helper_SEARCHINPUT()))

    return search_area_xpath

def get_more_places_button(html_data):
    soup = BeautifulSoup(html_data,features='html.parser')

    spans = soup.find_all('span')
    for span in spans:
        if span.text == 'More places' or str(span.text) == 'More businesses' :
            return xpath_soup(span)


def get_englishLanguage(html_data):
    soup = BeautifulSoup(html_data,features='html.parser')
    english_button_div = soup.find('div',attrhelpers.search_field_attr)

    return xpath_soup(english_button_div.find_all('a')[-1]) #this div has only on <a> tag

def accept_cookies(html_data):
    soup = BeautifulSoup(html_data,features='html.parser')
    for btn in soup.find_all('button'):
        if btn.text == 'Accept all':
            return xpath_soup(btn)

if __name__ == '__main__':
    with open('sample.txt','r',encoding='utf8') as f:
        html_data = f.read()
        print(get_more_places_button(html_data))