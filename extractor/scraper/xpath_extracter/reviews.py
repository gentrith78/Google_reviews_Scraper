import random
import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

try:
    from .list_place_extractor import get_xpath_list
    from .helper import AttrHelpers,Contact
    from .xpath_finder import xpath_soup
    from .review_analyser import find_contact_info
except:
    from list_place_extractor import get_xpath_list
    from helper import AttrHelpers, Contact
    from xpath_finder import xpath_soup
    from review_analyser import find_contact_info

attr_helpers = AttrHelpers()



def get_reviews_button_xpath(html_data):
    soup = BeautifulSoup(html_data, features='html.parser')

    # get the place frame
    place_frame = soup.find('async-local-kp')

    # find the review button
    reviews_button_xpath = xpath_soup(place_frame.find('a', attr_helpers.review_button))
    parent_div = place_frame.find('a', attr_helpers.review_button).parent
    for el in parent_div:
        if 'reviews' in str(el.text).lower():
            reviews_button_xpath = xpath_soup(el)

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

def get_all_reviews(logger,driver):
    """
    assuming that the bot has scrolled 5 times
    this function will get all of the reviews

    remember:
    after scrolling 5 times reviews are saved in a div
    for each scroll a new div is created containing 10 reviews
    each of these div has same attr:jscontroller="I1e3hc" ~ jsaction="rcuQ6b:npT2md"
    """
    html_data = driver.page_source
    soup = BeautifulSoup(html_data, features='html.parser')

    place_frame = soup.find('async-local-kp')

    review_packs = place_frame.find_all('div',attr_helpers.review_div_attrs) #this is a list of div that contains 10 more divs with reviews inside

    #click more buttons
    for review_pack in review_packs:
        more_links = review_pack.find_all('a', attr_helpers.review_more_link)
        for more in more_links:
            try:
                driver.find_element(By.XPATH, f"/{xpath_soup(more)}").click()
                time.sleep(random.randint(0,2))
            except:
                pass

    #get reviews
    html_data = driver.page_source
    soup = BeautifulSoup(html_data, features='html.parser')

    place_frame = soup.find('async-local-kp')

    review_packs = place_frame.find_all('div',attr_helpers.review_div_attrs) #this is a list of div that contains 10 more divs with reviews inside

    random_response = '' #this is only a random potential response
    contacts_final = []
    for review_pack in review_packs:
        for review_div in review_pack:
            if review_div.find('strong') != None and review_div.find('strong').text == 'Response from the owner':
                # get the owner reply text
                parent_div = review_div.find('strong').parent.parent.parent  # this div conatins the label "'Response from the owner' and another div the actual review, so i select the second div to get the response data
                actual_response_div = parent_div.find_all('div')[-1]
                # check if it contains information
                contacts = find_contact_info(actual_response_div.text)
                if len(contacts) > 0:
                    contacts_final.append(contacts)
                    random_response = actual_response_div.text

    if len(contacts_final) > 0:
        return {'response': random_response, 'contacts': contacts_final}
    return {'response': 'None', 'contacts': "None"}



if __name__ == '__main__':
    with open('sample.txt','r',encoding='utf8') as f:
        html_data = f.read()
