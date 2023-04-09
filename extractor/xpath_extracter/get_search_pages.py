from bs4 import BeautifulSoup

try:
    from .helper import AttrHelpers
except:
    from helper import AttrHelpers

attr_helpers = AttrHelpers

def get_pages_url(html_data):
    pages_urls = []

    soup = BeautifulSoup(html_data,features='html.parser')

    #get div of pages table
    page_table_div = soup.find('div',attr_helpers.div_of_pages_table)

    #get table rows
    pages_table_rows = page_table_div.find_all('td')
    for page in pages_table_rows:
        try:
            pages_urls.append(f"https://www.google.com{page.find('a')['href']}")
        except:
            # the "href" will not be found in active page
            pass
    return pages_urls


if __name__ == '__main__':
    with open('sample.txt','r',encoding='utf8') as f:
        html_data = f.read()
        print(get_pages_url(html_data))