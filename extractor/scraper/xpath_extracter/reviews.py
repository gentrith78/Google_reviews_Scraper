import random
import time
from datetime import datetime, timedelta

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

def get_phone(html_data):
    phone_nr = ''
    try:
        soup = BeautifulSoup(html_data, features='html.parser')
        phone_nr = soup.find('a',attr_helpers.phone__a_tag_attr).text.strip()
    except:
        pass
    return phone_nr
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
    reviews_with_responseFromOwner = []
    review_divs = []
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
    response_from_owner = ''
    contacts_phones = ['']
    contacts_emails = ['']
    for review_pack in review_packs:
        for review_div in review_pack:
            if review_div.find('strong') != None and review_div.find('strong').text == 'Response from the owner' :
                review_value = review_div.find('span', {'class': 'lTi8oc z3HNkc'}) # if we find this element into a div inside review pack this means that we have the right review div
                if float(str(review_value['aria-label']).split(' ')[1]) <=3: #check if review if negative (3 stars or lower)
                    reviews_with_responseFromOwner.append(review_div)
                # get the owner reply text
                parent_div = review_div.find('strong').parent.parent.parent  # this div conatins the label "'Response from the owner' and another div the actual review, so i select the second div to get the response data
                actual_response_div = parent_div.find_all('div')[2]
                # check if it contains information
                contacts = find_contact_info(parent_div.text)
                if contacts['phones'] != '':
                    response_from_owner = actual_response_div.text
                    contacts_phones.append(contacts['phones'])
                if contacts['emails'] != '':
                    response_from_owner = actual_response_div.text
                    contacts_emails.append(contacts['emails'])
            try:
                review_value = review_div.find('span', {'class': 'lTi8oc z3HNkc'}) # if we find this element into a div inside review pack this means that we have the right review div
                if float(str(review_value['aria-label']).split(' ')[1]) <=3: #check if review if negative (3 stars or lower)
                    review_divs.append(review_div)
            except:
                pass
    TIMESTAMP,REVIEW = BadReview(reviews_with_responseFromOwner,review_divs).process()
    final = {'main_phone':get_phone(html_data),
             'email extracted':"||".join(list(set(contacts_emails))),
             'phone extracted':"||".join(list(set(contacts_phones))),
             'bad review':REVIEW,
             'timestamp':TIMESTAMP,
             'rfo':response_from_owner
             }
    return final
class BadReview():
    def __init__(self,reviews_with_rfo,review_divs): #reviews_with_rfo is a list with all review divs that have a response from the  owner, a list with all reviews
        self.reviews_with_rfo = reviews_with_rfo
        self.review_divs = review_divs


    def process(self):
        if self.reviews_with_rfo:
            #get latest bad review and return
            return self.latest_bad_review_with_rfo()
            pass
        if self.review_divs:
            return self.latest_bad_review_without_rfo()
            pass
        else:
            return '',''
    def latest_bad_review_with_rfo(self):
        timestamp_and_review = []
        for r_div in self.reviews_with_rfo:
            try:
                timestamp = r_div.find('span', {'class': 'dehysf lTi8oc'}).text
                review_text = r_div.find('span', {'jscontroller': 'MZnM8e'}).text
                try:
                    timestamp_and_review.append({timestamp:review_text})
                except:
                    pass
            except:
                pass
        if timestamp_and_review:
            return self.get_newest_timestamp(timestamp_and_review)
        else:
            return '',''

    def latest_bad_review_without_rfo(self):
        timestamp_and_review = []
        for r_div in self.review_divs:
            try:
                timestamp = r_div.find('span', {'class': 'dehysf lTi8oc'}).text
                review_text = r_div.find('span', {'jscontroller': 'MZnM8e'}).text
                try:
                    timestamp_and_review.append({timestamp:review_text})
                except:
                    pass
            except:
                pass
        if timestamp_and_review:
            return self.get_newest_timestamp(timestamp_and_review)
        else:
            return '', ''

    def get_newest_timestamp(self,timestamp_list):
        # Convert review timestamps to datetime objects
        dates = []
        for review in timestamp_list:
            timestamp = str(list(review.keys())[0]).strip()
            if timestamp.startswith('a'):
                timestamp = timestamp.replace('a','1',1)
            dates.append(self.parse_datestring(timestamp))
        newest_review = max(dates)
        timestamp_and_review = timestamp_list[dates.index(newest_review)]
        pass
        return list(timestamp_and_review.keys())[0],list(timestamp_and_review.values())[0]
    def parse_datestring(self,datestr): #will convert the string to  date object
        try:
            if "day" in datestr:
                return datetime.now() - timedelta(days=int(datestr.split()[0]))
            elif "week" in datestr:
                return datetime.now() - timedelta(weeks=int(datestr.split()[0]))
            elif "month" in datestr:
                return datetime.now() - timedelta(days=30 * int(datestr.split()[0]))
            elif "year" in datestr:
                return datetime.now() - timedelta(days=365 * int(datestr.split()[0]))
        except Exception as e:
            pass


if __name__ == '__main__':
    with open('sample.txt','r',encoding='utf8') as f:
        html_data = f.read()
