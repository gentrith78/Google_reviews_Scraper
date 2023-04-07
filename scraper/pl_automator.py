import random
import dataclasses
import time

import pandas as pd
from playwright.sync_api import sync_playwright

from xpath_extracter import get_search_html_elements, get_more_places_button, get_pages_url, get_xpath_list,\
    get_reviews_button_xpath, get_lowest_reviews_xpath, get_all_reviews, Place

url = 'https://www.google.com/search?q=paris+restaurants&biw=1920&bih=1000&tbm=lcl&sxsrf=APwXEdd8BpDYF8kTf77gFQ_quRcqUChnPg%3A1680826441316&ei=SWAvZNb3EpHnrgT09omwDA&ved=0ahUKEwiWwNq3vpb-AhWRs4sKHXR7AsYQ4dUDCAk&uact=5&oq=paris+restaurants&gs_lcp=Cg1nd3Mtd2l6LWxvY2FsEAMyDQgAEA0QgAQQsQMQgwEyBwgAEA0QgAQyBwgAEA0QgAQyBwgAEA0QgAQyBwgAEA0QgAQyBggAEAcQHjIGCAAQBxAeMgcIABANEIAEMgYIABAHEB4yBwgAEA0QgAQ6BAgjECc6BggAEAUQHjoGCAAQCBAeOgcIABCABBANOgoIABCABBANELEDOgsIABCKBRCxAxCDAVDoDViuFWC8GWgAcAB4AIABlwGIAa4GkgEDNi4ymAEAoAEBwAEB&sclient=gws-wiz-local#rlfi=hd:;si:;mv:[[48.890128399999995,2.3674626],[48.8432807,2.3118749]];tbs:lrf:!1m4!1u3!2m2!3m1!1e1!1m4!1u5!2m2!5m1!1sgcid_3french_1restaurant!1m4!1u5!2m2!5m1!1sgcid_3restaurant_1brasserie!1m4!1u2!2m2!2m1!1e1!1m4!1u1!2m2!1m1!1e1!1m4!1u1!2m2!1m1!1e2!2m1!1e2!2m1!1e5!2m1!1e1!2m1!1e3!3sIAEqAkZS,lf:1,lf_ui:9'
places_as_df_list = []

if __name__ == '__main__':
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False,chromium_sandbox=False)
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        page.goto('https://www.google.com/',wait_until='networkidle')

        #TODO go to google and make a search with keyword
        search_input_xpath = f"/{get_search_html_elements(page.content())}"
        page.type(selector=search_input_xpath,text='luxemburg restaurants')
        time.sleep(random.randint(1,3))
        page.keyboard.press("Enter")
        time.sleep(10)

        #TODO got to places
        more_places_button = f"/{get_more_places_button(page.content())}"
        page.click(more_places_button)
        time.sleep(5)

        #TODO get the urls for each page
        paginations = get_pages_url(page.content())
        print(f"{len(paginations)} to paginate")

        for ind_page, url in enumerate(paginations):
            place_list_info = get_xpath_list(page.content())

            print(f"Page {ind_page+1} out of {len(paginations)}")
            print(f"Total {len(place_list_info)} Places in Page {ind_page}")

            places_data_list = []

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
                place_data = Place(name=place['place_div_name'],respnse=reviews_data['response'],contacts=reviews_data['contacts'])
                places_data_list.append(dataclasses.asdict(place_data))
                print('#########')

            df_place = pd.DataFrame(places_data_list)
            df_place.to_csv("London_Restaurants.csv")
            places_as_df_list.append(df_place)
            time.sleep(random.randint(1,5))

        print('###################################')
        browser.close()


