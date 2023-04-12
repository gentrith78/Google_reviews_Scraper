import sys
import random
import os
import time

import pandas as pd
from playwright.sync_api import sync_playwright

from extractor.xpath_extracter import get_search_html_elements, get_more_places_button, get_pages_url, get_xpath_list,\
    get_reviews_button_xpath, get_lowest_reviews_xpath, get_all_reviews, Place

try:
    from ..logger_m import logger_inst
except:
    sys.path.append('..')
    from logger_m import logger_inst

PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_PATH = os.path.dirname(os.path.dirname(PATH))

print('started')

def get_reviews(keyword):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False,chromium_sandbox=False)
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        page.goto('https://www.google.com/',wait_until='networkidle')

        # go to google and make a search with keyword
        search_input_xpath = f"/{get_search_html_elements(page.content())}"
        page.type(selector=search_input_xpath,text=str(keyword))

        time.sleep(random.randint(1,3))
        page.keyboard.press("Enter")
        time.sleep(10)

        # got to places
        #TODO add handler when places not found
        more_places_button = f"/{get_more_places_button(page.content())}"
        page.click(more_places_button)
        time.sleep(5)

        # get the urls for each page
        paginations = get_pages_url(page.content())
        # add the current url in the pagination link since it won't find the active page xpath
        paginations.insert(0,page.url)

        logger_inst.info(f"{len(paginations)} to paginate")

        for ind_page, url in enumerate(paginations):

            #navigating
            page.goto(url,wait_until='networkidle')

            logger_inst.info(f'Navigated to page:{ind_page+1}')

            place_list_info = get_xpath_list(page.content())

            logger_inst.info(f"Page {ind_page+1} out of {len(paginations)}")
            logger_inst.info(f"Total {len(place_list_info)} Places in Page {ind_page}")

            df = pd.DataFrame(columns=['Name', 'Page', 'Contacts', 'Potential_Response', "Url"])
            try:
                for place in place_list_info:
                    logger_inst.info(f"Processing {place['place_div_name']}")
                    page.click(f"/{place['place_div_name_div']}")
                    logger_inst.info('Clicked')
                    time.sleep(random.randint(2, 4))

                    #clicking reviews button
                    reviews_button_xpath = get_reviews_button_xpath(html_data=page.content())
                    page.click(f"/{reviews_button_xpath}")
                    logger_inst.info('Clicked Reviews')
                    time.sleep(random.randint(1, 3))

                    #clicking lowest rating
                    try:
                        lowest_rating_reviews_xpath = get_lowest_reviews_xpath(html_data=page.content())
                        if lowest_rating_reviews_xpath == None:
                            # no reviews
                            place_data = Place(Name=place['place_div_name'], Page=str(ind_page + 1),
                                               Contacts="None", Potential_Response="None",Url=page.url)
                            df.loc[len(df)] = [place_data.Name, place_data.Page, place_data.Contacts,
                                               place_data.Potential_Response, place_data.Url]
                            continue
                        page.click(f'/{lowest_rating_reviews_xpath}')
                        logger_inst.info('Clicked Lowest Rating Reviews')
                    except Exception as e:
                        logger_inst.error('Error while clicking "lowest rating":')
                        logger_inst.error(str(e))
                    # Perform scrolling 5 times
                    page.hover(f'/{lowest_rating_reviews_xpath}')
                    for scroll_ in range(5):
                        logger_inst.info('Scrolling')
                        for pg_down in range(4):
                            page.keyboard.press('PageDown')
                            time.sleep(0.5)
                        time.sleep(random.randint(1, 3))

                    logger_inst.info('Scrolled')
                    # Get reviews and check if contacts are detected
                    reviews_data = get_all_reviews(page.content())
                    logger_inst.info(reviews_data['contacts'])
                    place_data = Place(Name=place['place_div_name'],Page=str(ind_page+1),Contacts=reviews_data['contacts'],Potential_Response=reviews_data['response'],Url=page.url)
                    df.loc[len(df)] = [place_data.Name, place_data.Page, place_data.Contacts, place_data.Potential_Response,place_data.Url]
                    logger_inst.info('#########')
            except Exception as e_inpage:
                print(e_inpage)

            #save to output
            logger_inst.info(f'Saving Page {ind_page +1}')
            if os.path.exists(os.path.join(PROJECT_PATH,"output",f"{keyword}.csv")):
                pd.concat([pd.read_csv(os.path.join(PROJECT_PATH,"output",f"{keyword}.csv")),df]).to_csv(os.path.join(PROJECT_PATH,"output",f"{keyword}.csv"),index=False)
            else:
                df.to_csv(os.path.join(PROJECT_PATH,"output",f"{keyword}.csv"),index=False)
            logger_inst.info(f'Saved Page {ind_page +1}')

        logger_inst.info('###################################')
        browser.close()

if __name__ == '__main__':
    get_reviews('london restaurants')