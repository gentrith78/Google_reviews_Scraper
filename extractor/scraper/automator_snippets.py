import os
import time
import random

from playwright_stealth import stealth_sync

try:
    from .xpath_extracter import get_search_html_elements, get_more_places_button, get_pages_url,\
        get_reviews_button_xpath, get_lowest_reviews_xpath, get_all_reviews, Place, get_englishLanguage, accept_cookies
except:
    from xpath_extracter import get_search_html_elements, get_more_places_button, get_pages_url,\
        get_reviews_button_xpath, get_lowest_reviews_xpath, get_all_reviews, Place, get_englishLanguage, accept_cookies


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
        print(self.string_proxy)
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
    def process_search(self,page):
        # go to google and make a search with keyword
        try:
            try:
                search_input_xpath = f"/{get_search_html_elements(page.content())}"
            except:
                #didn't find the search input field, can be because the browser language is not English
                #Switching to english
                self.logger_.error(f'While finding "search input", trying to convert to english')
                english_lang_switch_xpath = get_englishLanguage(page.content())
                page.click(f"/{english_lang_switch_xpath}")
                search_input_xpath = f"/{get_search_html_elements(page.content())}"
                self.logger_.info(f'Converted to English')

                pass
            page.type(selector=search_input_xpath,text=str(self.keyword_))

            time.sleep(random.randint(1,3))
            page.keyboard.press("Enter")
            time.sleep(10)
        except Exception as e:
            self.logger_.error(f'Error while filling Search: {str(e)}')
            return False #the search could not be processed, return a value different than none in order for process function to know that has failed

    def process_MorePlaces_button(self,page):
        # got to places
        try:
            more_places_button = f"/{get_more_places_button(page.content())}"
            page.click(more_places_button)
            time.sleep(15)
        except Exception as e:
            try: #sometimes Cookie acception frame occurs, There script tries to find "accept all" button and to click it
                accept_cookies_button_xpath = accept_cookies(page.content())
                page.click(f"/{accept_cookies_button_xpath}")
                time.sleep(3)
                more_places_button = f"/{get_more_places_button(page.content())}"
                page.click(more_places_button)
                time.sleep(15)
            except:
                self.logger_.error(f'Error while Clicking "More Places" button: {str(e)}')
                return False
    def get_pagination_urls(self,page):
        try:
            return get_pages_url(page.content())
        except Exception as e:
            self.logger_.error(f'Error while parsing Pagination urls: {str(e)}')

    def process(self,page):

        # if  self.process_search(page) == None:
        if self.process_MorePlaces_button(page) == None:
            paginations = self.get_pagination_urls(page)
            if paginations != None:
                paginations.insert(0, page.url)
                self.logger_.info(f"{len(paginations)} Pages to paginate")
                return paginations
        raise Exception




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
            time.sleep(random.randint(3, 5))

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
        reviews_data = get_all_reviews(self.logger,page)
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
            try:#try to refresh the page and then click again the place
                page.reload(wait_until = 'networkidle')
                if self.perform_name_click(page) != None:
                    return place_data
            except:
                return place_data

        check_if_reviews_exist = self.perform_lowestReview_click_and_scrollin(page)
        if check_if_reviews_exist != None: #if this isn't None means that playwright couldn't perform click GOOD TO GO
            return place_data
        else:
            place_data = self.perform_reviews_extraction(page)
            if place_data != None:
                return place_data

