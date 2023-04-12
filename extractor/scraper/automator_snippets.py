import time
import random

import pandas as pd

from extractor.xpath_extracter import get_search_html_elements, get_more_places_button, get_pages_url, get_xpath_list,\
    get_reviews_button_xpath, get_lowest_reviews_xpath, get_all_reviews, Place


class ProcessSearch():
    def __init__(self,keyword_,logger_):
        self.keyword_ = keyword_
        self.logger_ = logger_
    def process_search(self,page):
        # go to google and make a search with keyword
        try:
            search_input_xpath = f"/{get_search_html_elements(page.content())}"
            page.type(selector=search_input_xpath,text=str(self.keyword_))

            time.sleep(random.randint(1,3))
            page.keyboard.press("Enter")
            time.sleep(10)
        except Exception as e:
            print(str(e))
            self.logger_.error(f'Error while filling Search: {str(e)}')

    def process_MorePlaces_button(self,page):
        # got to places
        try:
            more_places_button = f"/{get_more_places_button(page.content())}"
            page.click(more_places_button)
            page.wait_for_load_state('networkidle')
        except Exception as e:
            self.logger_.error(f'Error while Clicking "More Places" button: {str(e)}')

    def get_pagination_urls(self,page):
        try:
            return get_pages_url(page.content())
        except Exception as e:
            self.logger_.error(f'Error while parsing Pagination urls: {str(e)}')

    def process(self,page):

        if  self.process_search(page) == None:
            if self.process_MorePlaces_button(page) == None:
                paginations = self.get_pagination_urls(page)
                if paginations != None:
                    paginations.insert(0, page.url)
                    self.logger_.info(f"{len(paginations)} Pages to paginate")
                    return paginations
        return None





class ProcessPage():
    def __init__(self,place, ind_page, logger):
        self.place = place
        self.ind_page = ind_page
        self.logger  = logger

    def perform_name_click(self,page):

        page.click(f"/{self.place['place_div_name_div']}")
        time.sleep(random.randint(2, 4))

    def perform_reviews_click(self,page):

        reviews_button_xpath = get_reviews_button_xpath(html_data=page.content())
        page.click(f"/{reviews_button_xpath}")
        time.sleep(random.randint(1, 3))

    def perform_lowestReview_click_and_scrollin(self,page):
        try:
            lowest_rating_reviews_xpath = get_lowest_reviews_xpath(html_data=page.content())

            page.click(f'/{lowest_rating_reviews_xpath}')

            self.logger.info('Clicked Lowest Rating Reviews')

            page.hover(f'/{lowest_rating_reviews_xpath}')
            time.sleep(random.randint(1, 3))

            # scroll
            for scroll_ in range(5):
                for pg_down in range(4):
                    page.keyboard.press('PageDown')
                    time.sleep(0.5)
                time.sleep(random.randint(1, 3))
            self.logger.info('Performed Scrolling')
            return None

        except Exception as e:
            self.logger.error(f'Error while clicking "lowest rating" or  scrolling: {str(e)}')
            return True



    def perform_reviews_extraction(self,page):
        reviews_data = get_all_reviews(page.content())
        if reviews_data != None:
            self.logger.info(f"{reviews_data['contacts']}")
            place_data = Place(Name=self.place['place_div_name'], Page=str(self.ind_page + 1), Contacts=reviews_data['contacts'],
                               Potential_Response=reviews_data['response'], Url=page.url)
            return place_data
        return None
    def process(self,page):

        self.logger.info(f"Processing: {self.place['place_div_name']}")

        #not processed place
        place_data = Place(Name=self.place['place_div_name'], Page=str(self.ind_page + 1),
                           Contacts='None', Potential_Response='None',
                           Url=page.url)

        check_if__placeDiv_is_Clickable = self.perform_name_click(page)
        if check_if__placeDiv_is_Clickable !=  None: #if this isn't None means that playwright couldn't perform click GOOD TO GO
            return place_data

        check_if_reviewButton_is_clickable = self.perform_reviews_click(page)
        if check_if_reviewButton_is_clickable != None: #if this isn't None means that playwright couldn't perform click GOOD TO GO
            return place_data

        check_if_reviews_exist = self.perform_lowestReview_click_and_scrollin(page)
        if check_if_reviews_exist != None: #if this isn't None means that playwright couldn't perform click GOOD TO GO
            return place_data
        else:
            place_data = self.perform_reviews_extraction(page)
            if place_data != None:
                return place_data

