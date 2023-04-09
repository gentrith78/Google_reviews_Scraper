import time
from tkinter import messagebox

from bs4 import BeautifulSoup

try:
    from .list_place_extractor import get_xpath_list
    from .helper import AttrHelpers
    from .xpath_finder import xpath_soup
    from .review_analyser import find_contact_info
except:
    from list_place_extractor import get_xpath_list
    from helper import AttrHelpers
    from xpath_finder import xpath_soup
    from review_analyser import find_contact_info

attr_helpers = AttrHelpers()



def get_reviews_button_xpath(html_data):
    soup = BeautifulSoup(html_data, features='html.parser')

    # get the place frame
    place_frame = soup.find('async-local-kp')

    # find the review button
    try:
        reviews_button_xpath = xpath_soup(place_frame.find('a', attr_helpers.review_button))
    except:
        # sometimes the review button has data-index='1' instead of data-index='2'
        reviews_button_xpath = xpath_soup(place_frame.find('a', attr_helpers.get_reviews_button_second_method()))
        pass
    return reviews_button_xpath

def get_lowest_reviews_xpath(html_data):
    soup = BeautifulSoup(html_data, features='html.parser')

    # get the place frame
    place_frame = soup.find('async-local-kp')

    # get lowest reviews button xpath
    try:
        lowest_reviews_button_xpath = xpath_soup(place_frame.find('div',attr_helpers.lowest_review_button))
        return lowest_reviews_button_xpath
    except:
        #means that no reviews or little number of reviews was founded
        pass

def get_all_reviews(html_data):
    """
    assuming that the bot has scrolled 5 times
    this function will get all of the reviews

    remember:
    after scrolling 5 times reviews are saved in a div
    for each scroll a new div is created containing 10 reviews
    each of these div has same attr:jscontroller="I1e3hc" ~ jsaction="rcuQ6b:npT2md"
    :param html_data:
    :return:
    """

    soup = BeautifulSoup(html_data, features='html.parser')

    place_frame = soup.find('async-local-kp')

    review_packs = place_frame.find_all('div',attr_helpers.review_div_attrs) #this is a list of div that contains 10 more divs with reviews inside

    for review_pack in review_packs:
        for review_div in review_pack:
            if review_div.find('strong') != None and review_div.find('strong').text == 'Response from the owner':
                pass
                # get the owner reply text
                parent_div = review_div.find('strong').parent.parent #this div conatins the label "'Response from the owner' and another div the actual review, so i select the second div to get the response data
                actual_response_div = parent_div.find_all('div')[-1]
                #check if it contains information
                contacts = find_contact_info(actual_response_div.text)
                if len(contacts) > 0:
                    return {'response':actual_response_div.text,'contacts':contacts}
    return {'response': 'None', 'contacts': 'None'}


if __name__ == '__main__':
    with open('sample.txt','r',encoding='utf8') as f:
        html_data = f.read()
        print(get_all_reviews(html_data))