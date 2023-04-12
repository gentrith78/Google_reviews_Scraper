import os
import time

from extractor import get_reviews
from first_start import check_firstStart

#Dependencies will be installed while running for the first time
check_firstStart()


PATH = os.path.abspath(os.path.dirname(__file__))

def get_keywords():
    input_file = os.listdir(os.path.join(PATH,'input'))[0]
    with open(os.path.join(PATH,'input',input_file),'r') as f:
        keywords_raw = list(k.rstrip() for k in f.readlines())
        keywrods = []
        for keyword_ in keywords_raw:
            if keyword_.isdigit() or keyword_.isspace() or keyword_ == '':
                pass
            else:
                keywrods.append(keyword_)
        return keywrods

if __name__ == '__main__':
        for keyword_ in get_keywords():
            get_reviews(keyword_)


#TODO change first_start.txt
#TODO enable headless mode
#TODO