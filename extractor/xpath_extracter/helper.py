from dataclasses import dataclass



@dataclass
class AttrHelpers(): #so we are gonna use this data to find the elements through bs4
    search_field_attr = {'title':'Search','type':'search'}

    pages_table_attr = {'jsname':'TeSSVd'} #this is a <tr> elements that contains <td> elements, inside each <td> is an href for the next page of the search results
    div_of_pages_table = {'aria-label':'Local Results Pagination'} # the above table is located inside this div
    list_div_attr = {'class':'rlfl__tls rl_tls'} #class="rlfl__tls rl_tls"
    place_div_attr = {'jscontroller':'AtSb'}
    name_div_of_place = {'class':'rllt__details'}
    review_button = {'jsname':'AznF2e','data-index':'1'}
    lowest_review_button = {'data-sort-id':'ratingLow'}
    review_div_attrs = {'jscontroller':'I1e3hc','jsaction':'rcuQ6b:npT2md'} #this only contains a list of  divs where on each div exist the review data.

    review_more_link = {'class':'review-more-link'}                                                                            #for each scroll a new similar div is created and it contains 10 new reviews
    def get_second_helper_SEARCHINPUT(self):
        self.search_field_attr['type'] = 'text'
        return self.search_field_attr



@dataclass
class Place():
    Name:str
    Page:str
    Contacts:str
    Potential_Response:str
    Url:str

@dataclass
class Places():
    keyword_processed:str
    places:list


# Get all the response from the owners in a review and  save so we can check  then after scraping that page of reviews.
