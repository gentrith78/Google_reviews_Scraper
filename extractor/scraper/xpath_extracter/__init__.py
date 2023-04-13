"""
- By giving the html  content as input:
    - A module to find all places/restaurant div and extract each xpath for each place/restaurant and the id "ig="tsuid_29"
    - A module that for each click on a places/restaurant will find the "review" tab, will get  the id "lowest" and will find all reviews
"""

"""
main script will:
 - Search the keyword on google 
 - will call this  module to get the places div
 - will click on each place and  will called the other module that will get the review  and then click again the xpath until it finds the "owner reply" or reaches the threshhold

"""
from .list_place_extractor import get_xpath_list
from .reviews import get_reviews_button_xpath, get_lowest_reviews_xpath, get_all_reviews
from .helper import Place, Places
from .get_search_pages import get_pages_url
from .get_search_htmlElements import get_search_html_elements, get_more_places_button, get_englishLanguage, accept_cookies
