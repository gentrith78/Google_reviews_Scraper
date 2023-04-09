from bs4 import BeautifulSoup
try:
    from xpath_extracter.helper import AttrHelpers
except:
    from xpath_extracter.helper import AttrHelpers

# Attribute Data for the div elements that contains all places
attr_helpers = AttrHelpers()

def xpath_soup(element):
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name
            if siblings == [child] else
            '%s[%d]' % (child.name, 1 + siblings.index(child))
            )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)






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

        place_data['place_div_xpath'] = str(xpath_soup(place))
        place_data['place_div_id'] = str(attrs['id'])
        place_data['place_div_name_div'] = str(xpath_soup(place.find('div', attr_helpers.name_div_of_place)))

        output_data.append(place_data)

    return output_data


if __name__ == '__main__':

    # 1: Find the list div
    with open('xpath_extracter/sample.txt', 'r', encoding='utf8') as f:
        html_data = str(f.read())
        a = get_xpath_list(html_data)
        for aa in a:
            print(aa)
            print('###########################')