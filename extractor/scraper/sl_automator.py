import random
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

def get_reviews(keyword,csv_name):
    for i in range(15):
        try:
            #perform keyword search and click more places
            driver_instance = Create_Browser()
            driver = driver_instance.get_driver()
            url = f'https://www.google.com/search?tbs=lf:1,lf_ui:14&tbm=lcl&q={keyword.strip().replace(" ","+")}' \
                  f'&rflfq=1&num=10&sa=X&ved=2ahUKEwjrnbTatcX-AhX{random.randint(1,5)}gP0HHY' \
                  f'{random.choice(["Q","W","E","R","T","Y"])}fDW4QjGp{random.randint(1,9)}BAgWEAE&biw=1264'
            driver.get(url)
            time.sleep(5)
            search_processor = ProcessSearch(keyword,logger_inst)
            paginations = search_processor.process(driver)  # will return a list with paginations url or a list with two items: item1 'bussines' item2 'next page button xpath'
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
    if paginations[0] == 'business':
        business_mode_process = BusinessProcess(paginations[-1],driver,logger_inst,keyword)
        business_mode_process.process()
        #TODO process bussines extraction mode
        pass
    else:
        place_mode_processor = PlaceProcess(driver, logger_inst, csv_name, paginations)
        place_mode_processor.process()

    logger_inst.info('###################################')
    driver.close()
    driver_instance.delete_profile()
    return True

class BusinessProcess():
    def __init__(self, next_button_xpath, driver,logger_inst, csv_name,):
        self.next_button_xpath = next_button_xpath
        self.page_index = -1 #to match the 0 starting index
        self.driver = driver
        self.logger_inst = logger_inst
        self.df = pd.DataFrame(columns=['Name', 'Page', 'Contacts', 'Potential_Response', "Url"])
        self.csv_name = csv_name
    def process_Places(self, ind_page):
        place_list_info = get_xpath_list(self.driver.page_source)
        logger_inst.info(f"Total {len(place_list_info)} Places in Page {ind_page}")
        try:
            for place in place_list_info:
                place_processor = ProcessPage(place, ind_page,self.logger_inst)
                place_data = place_processor.process(self.driver)
                self.df.loc[len(self.df)] = [place_data.Name, place_data.Page, place_data.Contacts, place_data.Potential_Response,place_data.Url]

        except Exception as e_inpage:
            self.logger_inst.error(f"Couldn't process drive {ind_page+1} -- Error: {str(e_inpage)}")
    def save_page_to_csv(self, ind_page):
        #save to output
        self.logger_inst.info(f'Saving Page {ind_page +1}')
        if os.path.exists(os.path.join(PROJECT_PATH,"output",f"{self.csv_name}.csv")):
            pd.concat([pd.read_csv(os.path.join(PROJECT_PATH,"output",f"{self.csv_name}.csv")),self.df]).to_csv(os.path.join(PROJECT_PATH,"output",f"{self.csv_name}.csv"),index=False)
        else:
            self.df.to_csv(os.path.join(PROJECT_PATH,"output",f"{self.csv_name}.csv"),index=False)
        self.logger_inst.info(f'Saved Page {ind_page +1}')

    def process(self):
        #navigating
        try:
            self.driver.find_element(By.XPATH,self.next_button_xpath).click()
            self.page_index+=1
        except WebDriverException:
            logger_inst.error('Error Clicking NEXT')
            return None

        time.sleep(10)

        logger_inst.info(f"Page {self.page_index + 1} out of NOT KNOWN (Business Mode)")
        logger_inst.info(f'Navigated to Page:{self.page_index+1}')

        self.df = pd.DataFrame(columns=['Name', 'Page', 'Contacts', 'Potential_Response', "Url"])

        #process each place
        self.process_Places(self.page_index)

        # save to csv
        self.save_page_to_csv(self.page_index)
class PlaceProcess():
    def __init__(self,driver,logger_inst, csv_name, paginations):

        self.logger_inst = logger_inst
        self.df = pd.DataFrame(columns=['Business Name', 'main phone', 'email extracted', 'phone extracted', "Bad review", "Time stamp of the bad review ", "Response from the owner","Url"])
        self.csv_name = csv_name
    def process_Places(self, ind_page):
        place_list_info = get_xpath_list(self.driver.page_source)
        logger_inst.info(f"Total {len(place_list_info)} Places in Page {ind_page}")
        try:
            for place in place_list_info:
                place_processor = ProcessPage(place, ind_page,self.logger_inst)
                place_data = place_processor.process(self.driver)
                self.df.loc[len(self.df)] = [place_data.Name, place_data.Main_Phone, place_data.Email_Extracted, place_data.Phone_Extracted,place_data.Bad_Review,place_data.Timestamp,place_data.RFO,place_data.Url]
                pass
        except Exception as e_inpage:
            self.logger_inst.error(f"Couldn't process drive {ind_page+1} -- Error: {str(e_inpage)}")

    def save_page_to_csv(self, ind_page):
        #save to output
        self.logger_inst.info(f'Saving Page {ind_page +1}')
        if os.path.exists(os.path.join(PROJECT_PATH,"output",f"{self.csv_name}.csv")):
            pd.concat([pd.read_csv(os.path.join(PROJECT_PATH,"output",f"{self.csv_name}.csv")),self.df]).to_csv(os.path.join(PROJECT_PATH,"output",f"{self.csv_name}.csv"),index=False)
        else:
            self.df.to_csv(os.path.join(PROJECT_PATH,"output",f"{self.csv_name}.csv"),index=False)
        self.logger_inst.info(f'Saved Page {ind_page +1}')

    def process(self):
        #navigating
        for ind_page, url in enumerate(self.paginations):
            #navigating
            self.driver.get(url+"&hl=en")
            time.sleep(10)

            logger_inst.info(f"Page {ind_page + 1} out of {len(self.paginations)}")
            logger_inst.info(f'Navigated to Page:{ind_page+1}')

            self.df = pd.DataFrame(columns=['Business Name', 'main phone', 'email extracted', 'phone extracted', "Bad review", "Time stamp of the bad review ", "Response from the owner","Url"])

            #process each place
            self.process_Places(ind_page)

            # save to csv
            self.save_page_to_csv(ind_page)

