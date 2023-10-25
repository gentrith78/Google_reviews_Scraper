import os
import re
import sys
import time
from pathlib import Path
from typing import List, Dict, Union
from datetime import datetime
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

try:
    from xpath_extracter import get_xpath_list
    from logger_m import logger_inst
    from automator_snippets import *
    from gologin_browser import Create_Browser
    from structured_data import WebsiteInstance, phone_numbers_patterns
except:
    sys.path.append('.')
    sys.path.append('..')
    from .xpath_extracter import get_xpath_list
    from .logger_m import logger_inst
    from .automator_snippets import *
    from .gologin_browser import Create_Browser
    from .structured_data import WebsiteInstance, phone_numbers_patterns


def get_contacts(keyword, csv_name):
    for i in range(15):
        try:
            # perform keyword search and click more places
            driver_instance = Create_Browser()
            driver = driver_instance.get_driver()
            url = f'https://www.google.com/search?tbs=lf:1,lf_ui:14&tbm=lcl&q={keyword.strip().replace(" ", "+")}' \
                  f'&rflfq=1&num=10&sa=X&ved=2ahUKEwjrnbTatcX-AhX{random.randint(1, 5)}gP0HHY' \
                  f'{random.choice(["Q", "W", "E", "R", "T", "Y"])}fDW4QjGp{random.randint(1, 9)}BAgWEAE&biw=1264'
            driver.get(url)
            time.sleep(5)
            search_processor = ProcessSearch(keyword, logger_inst)
            paginations = search_processor.process(
                driver)  # will return a list with pagination's url or a list with two items: item1 'business' item2
            # 'next page button xpath'
            break
        except RuntimeError:
            logger_inst.error(f'Failed to find "More Places" button')
            return None
        except WebDriverException as de:
            logger_inst.error('Error with selenium')
            logger_inst.error(str(de))
        except Exception as e:
            try:
                driver.close()
                driver_instance.delete_profile()
            except UnboundLocalError:
                # a new browser iscreated but wiull remain unused, delete it
                driver_instance.delete_profile()
            logger_inst.error(f'Failed search process:{str(e)}')
            logger_inst.error('Creating new browser')
            pass

    if paginations == None:  # couldn't process search
        driver.close()
        driver_instance.delete_profile()
        return None

    instance = ContactExtractor(driver_instance, driver, paginations, keyword)
    instance.process()
    logger_inst.info('###################################')


class DriverManager():
    def __init__(self, driver, gologinBroser: Create_Browser):
        self.driver = driver
        self.gologinBroser: Create_Browser = gologinBroser

    def get_page_Selenium(self, url):
        try:
            self.driver.get(url)
            time.sleep(5)
        except:
            self.gologinBroser.delete_profile()
            self.driver = self.gologinBroser.get_driver()
            self.driver.get(url)
            time.sleep(5)

    def get_pageSourceSelenium(self):
        try:
            return self.driver.page_source
        except:
            self.gologinBroser.delete_profile()
            self.driver = self.gologinBroser.get_driver()
            return self.driver.page_source

    def finish_selenium(self):
        self.driver.close()


class PlaywrightInstance():
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True, chromium_sandbox=False)
        self.context = self.browser.new_context(no_viewport=True, user_agent=self.getUserAgent())
        self.page = self.context.new_page()
    def get_page(self, url):
        try:
            self.page.goto(url, wait_until='domcontentloaded')
        except:
            time.sleep(30)
            self.page.goto(url, wait_until='domcontentloaded')

    def reload_page(self):
        try:
            self.page.reload(wait_until='domcontentloaded')
        except:
            time.sleep(30)
            self.page.reload(wait_until='domcontentloaded')

    def get_pageSource(self) -> str:
        try:
            return self.page.content()
        except:
            time.sleep(30)
            return self.page.content()

    def get_CurrentURL(self) -> str:
        return self.page.url

    def getUserAgent(self) -> str:
        with open(os.path.join(PATH, 'user_agents.txt'), 'r') as f:
            user_agent = str(random.choice(f.readlines())).strip()
            return user_agent


class ParseContactInformation():
    def __init__(self):
        self.email_pattern = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[" \
                             r"a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
        self.us_phonenumbers_pattern = r'^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$'
        self.non_us_phonenumber_patterns = r'\d{4,5}(?:\s?\d{3}\s?\d{3}|\s?\d{6})'
        self.non_standard_phonenumbers_pattern = r'^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'

    def get_numbers(self, soup) -> List[str]:
        contacts = []
        for element in soup.find_all(['p', 'span', 'h1', 'h2', 'strong', 'a']):
            if element.name == 'a':
                contacts.extend(re.findall(self.us_phonenumbers_pattern, element.get('href', '')))
                contacts.extend(re.findall(self.non_us_phonenumber_patterns, element.get('href', '')))
                contacts.extend(re.findall(self.non_standard_phonenumbers_pattern, element.get('href', '')))
                contacts.extend(self._other_numbers_search(element.get('href', '')))
                if element.text != '' or element.text.isspace() or len(element.text) < 6:
                    continue
                contacts.extend(self._other_numbers_search(element.text))
            else:
                if element.text != '' or element.text.isspace() or len(element.text) < 6:
                    continue
                contacts.extend(self._other_numbers_search(element.text))
                contacts.extend(re.findall(self.us_phonenumbers_pattern, element.text))
                contacts.extend(re.findall(self.non_us_phonenumber_patterns, element.text))
                contacts.extend(re.findall(self.non_standard_phonenumbers_pattern, element.text))

        return self._filter_numbers(contacts)

    def _other_numbers_search(self, text: str) -> List[str]:
        phones = []
        for p in phone_numbers_patterns:
            phones.extend(re.findall(p, text))

        return phones

    def get_emails(self, soup) -> List[str]:
        contacts: List[str] = []

        for element in soup.find_all(['p', 'span', 'h1', 'h2', 'strong', 'a']):
            if element.name == 'a':
                contacts.extend(re.findall(self.email_pattern, element.get('href', '').strip()))
                contacts.extend(re.findall(self.email_pattern, element.text.strip()))
            else:
                contacts.extend(re.findall(self.email_pattern, element.text.strip()))

        return self._filter_emails(contacts)

    def _filter_numbers(self, numbers: List[str]) -> List[str]:
        filtered_numbers: List[str] = []

        for el in numbers:
            if el.isspace() or el == '' or len(el) < 8 or not '' in el:
                continue
            filtered_numbers.append(el.strip())

        return list(set(filtered_numbers))

    def _filter_emails(self, emails: List[str]) -> List[str]:
        filtered_mails: List[str] = []
        for el in emails:
            if el.isspace() or el == '' or len(el) < 8 or not '@' in el:
                continue
            filtered_mails.append(el)
        return list(set(emails))

    def __advanced_contact_info(self, text: str) -> List[str]:  # NOT USED
        # Define regular expressions for different types of contact info
        email_url_re_with_hhtps = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
        email_url_re_without_https = r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
        us_phonenumbers_pattern = r'^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$'
        non_us_phonenumber_patterns = r'^(\+0?1\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$'
        non_standard_phonenumbers_pattern = r'^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'
        # Find all matches in the text
        phone_numbers = []

        try:
            phone_regex1 = re.search(us_phonenumbers_pattern, text).group()
            phone_numbers.append(phone_regex1)
        except:
            pass
        try:
            phone_regex2 = re.search(non_us_phonenumber_patterns, text).group()
            phone_numbers.append(phone_regex2)
        except:
            pass
        try:
            phone_regex3 = re.search(non_standard_phonenumbers_pattern, text).group()
            phone_numbers.append(phone_regex3)
        except:
            pass
        try:
            match_algo_phone = self.__find_by_text_algo(text)
            if match_algo_phone != None:
                phone_numbers.append(match_algo_phone)
        except:
            pass

        # Remove duplicates
        phone_numbers = list(set(phone_numbers))
        final_emails = []
        final_phones = []
        for contact in phone_numbers:
            if contact == "" or str(contact).isspace() or len(contact) <= 7:
                continue
            final_phones.append(contact)

        return final_phones

    def __find_by_text_algo(self, text):  # NOT USED
        phone_nr_keywords = [
            'call',
            'phone number',
            'telephone number',
        ]
        for keyword in phone_nr_keywords:
            if keyword in text:
                possible_match = re.search('\d{9,}', text).group()
                return possible_match
        return None


class ContactExtractor(DriverManager, ParseContactInformation, PlaywrightInstance):
    def __init__(self, gologinBroser: Create_Browser, driver, paginations: List[str], keyword: str):
        DriverManager.__init__(self, driver, gologinBroser)
        ParseContactInformation.__init__(self)
        PlaywrightInstance.__init__(self)
        self.PATH = os.path.abspath(os.path.dirname(__file__))
        self.paginations: List[str] = paginations
        self.keyword: str = keyword
        self.websites: List[WebsiteInstance] = []
        self.bad_words = ['facebook', 'instagram', 'youtube', 'twitter', 'wiki', 'linkedin']

    def process(self):
        # extract all businesses and their websites
        self._get_websites()
        # get the contacts for each website
        self._get_contacts()
        # write to csv
        self._write_to_csv()
        # close browser session
        self.browser.close()
        self.playwright.stop()

    def _get_websites(self):
        for ind_page, url in enumerate(self.paginations):
            # navigating
            self.get_page_Selenium(url + "&hl=en")
            time.sleep(10)
            websites = get_xpath_list(self.get_pageSourceSelenium(), contactMode=True)
            for web in websites:
                should_i_skip = False
                if len(self.websites) >= 100:
                    self.finish_selenium()
                    return
                for bad_word in self.bad_words:
                    if bad_word in web[1]:
                        should_i_skip = True
                if web[1].isspace() or len(web[1]) < 10 or web[1] == '' or should_i_skip:
                    continue
                web_inst = WebsiteInstance(
                    name=web[0],
                    website=web[1]
                )
                self.websites.append(web_inst)
        self.finish_selenium()

    def _get_contacts(self):
        for web in self.websites:
            self.get_page(web.website)
            main_page_contacts = self.__parseContacts
            contact_or_aboutContacts = self.__get_contact_us_page()
            web.website = self.get_CurrentURL()  # since we change the url with self.__get_contact_us_page()
            web.contacts.extend(main_page_contacts)
            web.contacts.extend(contact_or_aboutContacts)
            web.contacts = list(set(el for el in web.contacts if not el.isspace() and not el == ''))
            print(web)

    def _write_to_csv(self):
        rows: List[pd.DataFrame] = []
        # create dataframes
        for web in self.websites:
            df = pd.DataFrame(self.__serialised_row(web))
            rows.append(df)
        # save csv
        path_to_save = Path(self.PATH).parent.parent.joinpath('output')
        if not path_to_save.exists():
            os.mkdir(str(path_to_save))
            path_to_save = str(path_to_save.joinpath(
                f"{self.keyword.replace(' ', '_').replace('.', '-')}--{datetime.now().strftime('%d-%B_at_%H-%M-%S')}.csv"))

        else:
            path_to_save = str(path_to_save.joinpath(
                f"{self.keyword.replace(' ', '_').replace('.', '-')}--{datetime.now().strftime('%d-%B_at_%H-%M-%S')}.csv"))
        # write csv
        pd.concat(rows).to_csv(path_to_save, index=False)

    def __get_contact_us_page(self) -> List[str]:
        links = []
        html_content = self.get_pageSource()
        soup = BeautifulSoup(html_content, 'html.parser')
        for link in soup.find_all('a'):
            if link.has_attr('href'):
                links.append(link['href'])
        if links:
            for link in links:
                link = urljoin(self.get_CurrentURL(), link)
                for bad_word in self.bad_words:
                    if bad_word in link.lower():
                        continue
                if 'contact' in link.lower():
                    self.get_page(link)
                    return self.__parseContacts
                # if 'about' in link.lower():
                #     self.get_page(link)
                #     return self.__parseContacts
        return []

    @property
    def __parseContacts(self) -> List[str]:
        contacts: List[str] = []
        html_content = self.get_pageSource()
        soup = BeautifulSoup(html_content, 'html.parser')

        contacts.extend(self.get_emails(soup))
        contacts.extend(self.get_numbers(soup))

        return contacts

    def __serialised_row(self, website_instance: WebsiteInstance) -> Dict:
        serialized_inst = {
            'Name': [website_instance.name],
            'Website': [website_instance.website]
        }

        phones = []
        emails = []
        for ind, c in enumerate(website_instance.contacts):
            if '@' in c:
                emails.append(c)
            else:
                phones.append(c)

        serialized_inst.update({'Emails':' || '.join(emails)})
        serialized_inst.update({'Phones':' || '.join(phones)})

        return serialized_inst


if __name__ == '__main__':
    PATH = os.path.abspath(os.path.dirname(__file__))
    print(Path(PATH).parent.parent.joinpath('output'))