from bs4 import BeautifulSoup
try:
    from .helper import AttrHelpers
    from .xpath_finder import xpath_soup
except:
    from xpath_extracter.helper import AttrHelpers
    from xpath_finder import xpath_soup


# Attribute Data for the div elements that contains all places
attr_helpers = AttrHelpers()

def get_xpath_list(html_data):
    output_data = []

    soup = BeautifulSoup(html_data, features='html.parser')
    list_div = soup.find('div', attr_helpers.list_div_attr)
    for place in list_div:
        place_data = {
            'place_div_xpath': '',
            'place_div_id': '',
            'place_div_name_div': '',
        }

        attrs = place.attrs
        # checking if the element is a place
        if place.text.replace('\n', '') == '' or 'id' not in attrs:
            continue
        if place.find('div', attr_helpers.name_div_of_place) == None:
            # couldn't find the name div
            # handle the error
            continue

        place_data['place_div_id'] = str(attrs['id'])
        place_data['place_div_name_div'] = str(xpath_soup(place.find('div', attr_helpers.name_div_of_place)))
        place_data['place_div_name'] = place.find('div', attr_helpers.name_div_of_place).find('span').text

        output_data.append(place_data)

    return output_data

if __name__ == '__main__':
    pass