import random
import os
import time

import pandas as pd
from playwright.sync_api import sync_playwright

from extractor.xpath_extracter import get_search_html_elements, get_more_places_button, get_pages_url, get_xpath_list,\
    get_reviews_button_xpath, get_lowest_reviews_xpath, get_all_reviews, Place

PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_PATH = os.path.dirname(os.path.dirname(PATH))

#TODO add logging system

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

        print(f"{len(paginations)} to paginate")

        for ind_page, url in enumerate(paginations):

            #navigating
            page.goto(url,wait_until='networkidle')

            place_list_info = get_xpath_list(page.content())

            print(f"Page {ind_page+1} out of {len(paginations)}")
            print(f"Total {len(place_list_info)} Places in Page {ind_page}")

            df = pd.DataFrame(columns=['Name', 'Page', 'Contacts', 'Potential_Response', "Url"])

            for place in place_list_info:
                print(f"Processing {place['place_div_name']}")
                page.click(f"/{place['place_div_name_div']}")
                print('Clicked')
                time.sleep(random.randint(2, 4))

                #clicking reviews button
                reviews_button_xpath = get_reviews_button_xpath(html_data=page.content())
                page.click(f"/{reviews_button_xpath}")
                print('Clicked Reviews')
                time.sleep(random.randint(1, 3))

                #clicking lowest rating
                lowest_rating_reviews_xpath = get_lowest_reviews_xpath(html_data=page.content())
                if lowest_rating_reviews_xpath == None:
                    # no reviews
                    place_data = Place(Name=place['place_div_name'], Page=str(ind_page + 1),
                                       Contacts=reviews_data['contacts'], Potential_Response=reviews_data['response'],Url=page.url)
                    df.loc[len(df)] = [place_data.Name, place_data.Page, place_data.Contacts,
                                       place_data.Potential_Response, place_data.Url]
                    continue
                page.click(f'/{lowest_rating_reviews_xpath}')
                print('Clicked Lowest Rating Reviews')

                # Perform scrolling 5 times
                page.hover(f'/{lowest_rating_reviews_xpath}')
                for scroll_ in range(5):
                    print('Scrolling')
                    for pg_down in range(4):
                        page.keyboard.press('PageDown')
                        time.sleep(0.5)
                    time.sleep(random.randint(1, 3))

                print('Scrolled')
                # Get reviews and check if contacts are detected
                reviews_data = get_all_reviews(page.content())
                print(reviews_data['contacts'])
                place_data = Place(Name=place['place_div_name'],Page=str(ind_page+1),Contacts=reviews_data['contacts'],Potential_Response=reviews_data['response'],Url=page.url)
                df.loc[len(df)] = [place_data.Name, place_data.Page, place_data.Contacts, place_data.Potential_Response,place_data.Url]
                print('#########')

            #save to output
            print(f'Saving Page {ind_page +1}')
            if os.path.exists(os.path.join(PROJECT_PATH,"output",f"{keyword}.csv")):
                pd.concat([pd.read_csv(os.path.join(PROJECT_PATH,"output",f"{keyword}.csv")),df]).to_csv(os.path.join(PROJECT_PATH,"output",f"{keyword}.csv"),index=False)
            else:
                df.to_csv(os.path.join(PROJECT_PATH,"output",f"{keyword}.csv"),index=False)
            print(f'Saved Page {ind_page +1}')
        print('###################################')
        browser.close()
