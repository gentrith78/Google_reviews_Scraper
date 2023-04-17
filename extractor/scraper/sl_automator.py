import sys
import time

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
try:
    from xpath_extracter import get_xpath_list
    from logger_m import logger_inst
    from automator_snippets import *
    from gologin_browser import Create_Browser
except:
    sys.path.append('.')
    sys.path.append('..')
    from .xpath_extracter import get_xpath_list
    from .logger_m import logger_inst
    from .automator_snippets import *
    from .gologin_browser import Create_Browser

PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_PATH = os.path.dirname(os.path.dirname(PATH))

print('started')

def get_reviews(keyword):
    for i in range(15):
        try:
            #perform keyword search and click more places
            driver_instance = Create_Browser()
            driver = driver_instance.get_driver()
            url = f'https://www.google.com/search?q={keyword}&hl=en'
            driver.get(url)
            time.sleep(10)
            search_processor = ProcessSearch(keyword,logger_inst)
            paginations = search_processor.process(driver)  # will return a list with paginations url
            break
        except RuntimeError:
            logger_inst.error(f'Failed to find "More Places" button')
            return None
        except WebDriverException:
            logger_inst.error('Error with selenium')
        except Exception as e:
            try:
                driver.close()
                driver_instance.delete_profile()
            except UnboundLocalError:
                #a new browser iscreated but wiull remain unused, delete it
                driver_instance.delete_profile()
                pass
            logger_inst.error(f'Failed search process:{str(e)}')
            logger_inst.error('Creating new browser')
            pass

    if paginations == None: #couldn't process search
        driver.close()
        driver_instance.delete_profile()
        return None
    for ind_page, url in enumerate(paginations):

        #navigating
        driver.get(url+"&hl=en")

        logger_inst.info(f'Navigated to drive:{ind_page+1}')

        place_list_info = get_xpath_list(driver.page_source)

        logger_inst.info(f"Page {ind_page+1} out of {len(paginations)}")
        logger_inst.info(f"Total {len(place_list_info)} Places in Page {ind_page}")

        df = pd.DataFrame(columns=['Name', 'Page', 'Contacts', 'Potential_Response', "Url"])
        try:
            for place in place_list_info:
                place_processor = ProcessPage(place, ind_page,logger_inst)
                place_data = place_processor.process(driver)
                df.loc[len(df)] = [place_data.Name, place_data.Page, place_data.Contacts, place_data.Potential_Response,place_data.Url]

        except Exception as e_inpage:
            logger_inst.error(f"Couldn't process drive {ind_page+1} -- Error: {str(e_inpage)}")

        #save to output
        logger_inst.info(f'Saving Page {ind_page +1}')
        if os.path.exists(os.path.join(PROJECT_PATH,"output",f"{keyword}.csv")):
            pd.concat([pd.read_csv(os.path.join(PROJECT_PATH,"output",f"{keyword}.csv")),df]).to_csv(os.path.join(PROJECT_PATH,"output",f"{keyword}.csv"),index=False)
        else:
            df.to_csv(os.path.join(PROJECT_PATH,"output",f"{keyword}.csv"),index=False)
        logger_inst.info(f'Saved Page {ind_page +1}')

    logger_inst.info('###################################')
    driver.close()
    driver_instance.delete_profile()
    return True

if __name__ == '__main__':
    get_reviews('london restaurants')
    pass