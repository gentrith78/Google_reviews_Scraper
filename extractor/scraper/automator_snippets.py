import os
import time
import random

from playwright_stealth import stealth_sync
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
try:
    from .xpath_extracter import get_search_html_elements, get_more_places_button, get_pages_url,\
        get_reviews_button_xpath, get_lowest_reviews_xpath, get_all_reviews, Place, get_englishLanguage, accept_cookies, get_next_bussinesses_page
except:
    from xpath_extracter import get_search_html_elements, get_more_places_button, get_pages_url,\
        get_reviews_button_xpath, get_lowest_reviews_xpath, get_all_reviews, Place, get_englishLanguage, accept_cookies, get_next_bussinesses_page


PATH = os.path.abspath(os.path.dirname(__file__))

class GetUserAgent():
    def get(self):
        with open(os.path.join(PATH,'user_agents.txt'),'r') as f:
            user_agent = str(random.choice(f.readlines())).strip()
            return user_agent

class GetProxy():
    def __init__(self):
        self.username = 'goroyal'
        self.password = 'reviewsproxies'
        self.string_proxy = ''
        with open(os.path.join(PATH,'Proxy_list.txt'),'r') as f:
            proxy_string = random.choice(f.readlines())
            self.string_proxy = proxy_string.replace('\n','')

    def get_proxy(self):
        return {
            'server': f"http://{self.string_proxy}",
            'username':self.username,
            'password':self.password,
        }
class GetContext():
    def __init__(self,p):
        self.p = p
        self.proxy = GetProxy().get_proxy()
        self.browser = ''
    def get_page(self):
        self.browser = self.p.chromium.launch(headless=False,chromium_sandbox=False,proxy=self.proxy,)
        context = self.browser.new_context(no_viewport=True,user_agent=GetUserAgent().get())
        page = context.new_page()
        stealth_sync(page)
        return page
    def close(self):
        self.browser.close()


class ProcessSearch():
    def __init__(self,keyword_,logger_):
        self.keyword_ = keyword_
        self.logger_ = logger_

    def morePlacesOrBusiness_button_clicking(self, driver):
        # got to places
        try:
            more_places_button = get_more_places_button(driver.page_source)
            if more_places_button['mode'] == 'place':
                self.logger_.info('MODE -- PLACE')
                more_places_button = f"/{more_places_button['xpath']}"
                driver.find_element(By.XPATH, more_places_button).click()
                time.sleep(10)
            else:
                if more_places_button['mode'] == 'business':
                    self.logger_.info('MODE -- BUSINESS')
                    more_places_button = f"/{more_places_button['xpath']}"
                    driver.find_element(By.XPATH, more_places_button).click()
                    time.sleep(10)
                    try:
                        next_btn_xpath = get_next_bussinesses_page(driver.page_source) #paginations can be  presented by  a next  button in business mode, if  so, returns a list to be processed in business mode
                    except:
                        return None
                    return ['business', next_btn_xpath] # we are telling the app that MODE IS BUSINESS

        except Exception as e:
            try: #sometimes Cookie acception frame occurs, There script tries to find "accept all" button and to click it
                accept_cookies_button_xpath = accept_cookies(driver.page_source)
                driver.find_element(By.XPATH,f"/{accept_cookies_button_xpath}").click()
                time.sleep(3)
                more_places_button = f"/{get_more_places_button(driver.page_source)}"
                driver.find_element(By.XPATH, more_places_button).click()
                time.sleep(15)
            except:
                self.logger_.error(f'Error while Clicking "More Places" button: {str(e)}')
                return False
    def get_pagination_urls(self,driver):
        try:
            return get_pages_url(driver.page_source)
        except Exception as e:
            self.logger_.error(f'Error while parsing Pagination urls: {str(e)}')

    def process(self, driver):

        # if  self.process_search(driver) == None:
        button_clickin_process = self.morePlacesOrBusiness_button_clicking(driver)
        if button_clickin_process == None:
            paginations = self.get_pagination_urls(driver)
            if paginations != None:
                paginations.insert(0, driver.current_url)
                self.logger_.info(f"{len(paginations)} Pages to paginate")
                return paginations
        elif button_clickin_process[0] == 'business':
            return button_clickin_process
        raise Exception




class ProcessPage():
    def __init__(self,place, ind_page, logger):
        self.place = place
        self.ind_page = ind_page
        self.logger  = logger

    def perform_name_click(self,driver):
        driver.find_element(By.XPATH,f"/{self.place['place_div_name_div']}").click()
        time.sleep(random.randint(2, 4))

    def perform_reviews_click(self,driver):

        reviews_button_xpath = get_reviews_button_xpath(html_data=driver.page_source)
        driver.find_element(By.XPATH,f"/{reviews_button_xpath}").click()
        time.sleep(random.randint(1, 3))

    def perform_lowestReview_click_and_scrollin(self,driver):
        try:
            lowest_rating_reviews_xpath = get_lowest_reviews_xpath(html_data=driver.page_source)
            try:
                driver.find_element(By.XPATH,f"/{lowest_rating_reviews_xpath}").click()
            except WebDriverException:
                self.logger.error('No reviews')
                return True

            self.logger.info('Clicked Lowest Rating Reviews')
            time.sleep(random.randint(1,3))
            # scroll
            for scroll_ in range(5):
                for pg_down in range(4):
                    driver.find_element(By.XPATH,f"/{lowest_rating_reviews_xpath}").send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.5)
                time.sleep(random.randint(1, 3))
            self.logger.info('Performed Scrolling')
            return None

        except Exception as e:
            self.logger.error(f'Error while clicking "lowest rating" or  scrolling: {str(e)}')
            return True



    def perform_reviews_extraction(self,driver):
        reviews_data = get_all_reviews(self.logger,driver)
        if reviews_data != None:
            self.logger.info(f"{reviews_data['contacts']}")
            place_data = Place(Name=self.place['place_div_name'], Page=str(self.ind_page + 1), Contacts=reviews_data['contacts'],
                               Potential_Response=reviews_data['response'], Url=driver.current_url)
            return place_data
        return None
    def process(self,driver):

        self.logger.info(f"Processing: {self.place['place_div_name']}")

        #not processed place
        place_data = Place(Name=self.place['place_div_name'], Page=str(self.ind_page + 1),
                           Contacts='None', Potential_Response='None',
                           Url=driver.current_url)

        check_if__placeDiv_is_Clickable = self.perform_name_click(driver)
        if check_if__placeDiv_is_Clickable !=  None: #if this isn't None means that playwright couldn't perform click GOOD TO GO
            return place_data

        check_if_reviewButton_is_clickable = self.perform_reviews_click(driver)
        if check_if_reviewButton_is_clickable != None: #if this isn't None means that playwright couldn't perform click GOOD TO GO
            try:#try to refresh the driver and then click again the place
                driver.refresh()
                if self.perform_name_click(driver) != None:
                    return place_data
            except:
                return place_data

        check_if_reviews_exist = self.perform_lowestReview_click_and_scrollin(driver)
        if check_if_reviews_exist != None: #if this isn't None means that playwright couldn't perform click GOOD TO GO
            return place_data
        else:
            place_data = self.perform_reviews_extraction(driver)
            if place_data != None:
                return place_data

