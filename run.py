import os
from datetime import datetime

from extractor import get_reviews, get_contacts

PATH = os.path.abspath(os.path.dirname(__file__))

def get_keywords():
    input_file = os.listdir(os.path.join(PATH,'input'))[-1]
    with open(os.path.join(PATH,'input',input_file),'r') as f:
        keywords_raw = list(k.rstrip() for k in f.readlines())
        print(keywords_raw)
        keywrods = []
        for keyword_ in keywords_raw:
            if keyword_.isdigit() or keyword_.isspace() or keyword_ == '':
                pass
            else:
                keywrods.append(keyword_)
        return keywrods

csv_name = ''
if __name__ == '__main__':
        current_time = datetime.now()
        formatted_current_time = datetime.strftime(current_time, '%d_%m-%H_%M')
        csv_name = f"{formatted_current_time}.csv"
        print(csv_name)
        for keyword_ in get_keywords():
            # get_contacts(keyword_,csv_name)
            get_reviews(keyword_,csv_name)


#TODO change first_start.txt
#TODO enable headless mode
#TODO delete sample html
#TODO delete logs
#TODO add token