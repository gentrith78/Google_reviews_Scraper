import sys
import random
import os
import time

import pandas as pd
from playwright.sync_api import sync_playwright

from extractor.xpath_extracter import  get_xpath_list

try:
    from ..logger_m import logger_inst
    from .automator_snippets import ProcessPage, ProcessSearch, GetProxy, GetContext
except:
    sys.path.append('..')
    from automator_snippets import ProcessPage, ProcessSearch, GetProxy, GetContext
    from logger_m import logger_inst

PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_PATH = os.path.dirname(os.path.dirname(PATH))

print('started')

def get_reviews(keyword):
    with sync_playwright() as p:

        for i in range(50):
            try:
                #perform keyword search and click more places
                browser = GetContext(p)
                page = browser.get_page()
                page.goto('https://www.google.com/', wait_until='networkidle')

                search_processor = ProcessSearch(keyword,logger_inst)
                paginations = search_processor.process(page)  # will return a list with paginations url
                break
            except RuntimeError:
                logger_inst.error(f'Failed to find "More Places" button')
                return None
            except Exception as e:
                browser.close()
                logger_inst.error(f'Failed search process:{str(e)}')
                logger_inst.error('Creating new browser')
                pass

        if paginations == None: #couldn't process search
            browser.close()
            return None
        print(paginations)
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
                    place_processor = ProcessPage(place, ind_page,logger_inst)
                    place_data = place_processor.process(page)
                    df.loc[len(df)] = [place_data.Name, place_data.Page, place_data.Contacts, place_data.Potential_Response,place_data.Url]

            except Exception as e_inpage:
                logger_inst.error(f"Couldn't process page {ind_page+1} -- Error: {str(e_inpage)}")

            #save to output
            logger_inst.info(f'Saving Page {ind_page +1}')
            if os.path.exists(os.path.join(PROJECT_PATH,"output",f"{keyword}.csv")):
                pd.concat([pd.read_csv(os.path.join(PROJECT_PATH,"output",f"{keyword}.csv")),df]).to_csv(os.path.join(PROJECT_PATH,"output",f"{keyword}.csv"),index=False)
            else:
                df.to_csv(os.path.join(PROJECT_PATH,"output",f"{keyword}.csv"),index=False)
            logger_inst.info(f'Saved Page {ind_page +1}')

        logger_inst.info('###################################')
        browser.close()
        return True

if __name__ == '__main__':
    get_reviews('london restaurants')