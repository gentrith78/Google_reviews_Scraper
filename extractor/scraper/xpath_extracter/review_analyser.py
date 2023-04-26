import re

desired_domains = ['.com','.net','.org','.ca','.co.uk',
                   '.management','.biz','.us','.co','.com.au'
                   ,'edu','.nz','.pub','.uk','eu','.biz']

phone_nr_keywords = [
    'call',
    'phone number',
    'telephone number',
]

def check_email_match(email):
    if "@" in str(email):
        if len(email) <= 7:
            return email
    for el in desired_domains:
        if str(email).endswith(el):
            return email
    return False

def find_by_text_algo(text):
    for keyword in phone_nr_keywords:
        if keyword in text:
            possible_match = re.search('\d{9,}',text).group()
            return possible_match
    return None
def find_contact_info(text):
    # Define regular expressions for different types of contact info
    email_url_re_with_hhtps = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
    email_url_re_without_https = r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
    us_phonenumbers_pattern = r'^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$'
    non_us_phonenumber_patterns = r'^(\+0?1\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$'
    non_standard_phonenumbers_pattern = r'^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'
    # Find all matches in the text
    phone_numbers = []
    emails = []
    try:
        email_regex = re.search(email_url_re_with_hhtps, text, re.MULTILINE).group()
        emails.append(email_regex)
    except:
        pass

    try:
        for email in re.compile(email_url_re_without_https).finditer(text):
            email = check_email_match(email.group())
            if email:
                emails.append(email)
            else:
                pass
    except:
        pass
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
        match_algo_phone = find_by_text_algo(text)
        if match_algo_phone != None:
            phone_numbers.append(match_algo_phone)
    except:
        pass

    # Remove duplicates
    emails = list(set(emails))
    phone_numbers = list(set(phone_numbers))
    final_emails = []
    final_phones = []
    for contact in phone_numbers:
        if contact == "" or str(contact).isspace() or len(contact) <= 7:
            continue
        final_phones.append(contact)
    for contact in emails:
        if contact == "" or str(contact).isspace() or len(contact) <= 7:
            continue
        final_emails.append(contact)


    return {'phones':"||".join(final_phones),"emails":'||'.join(final_emails)}


if __name__ == '__main__':
    textemail = """
    Thank you for taking the time to review your recent visit.I am sorry that the manager on duty & host we can discuss any problems you â€¦Thank you for taking the time to review your recent visit.I am sorry that the manager on duty & host were an issue if you could contact me feedbackliverpool@gustorestaurants.uk.com we can discuss any problems you encountered.RegardsLisa DixonGeneral ManagerMore
    """
    text_phone = """
    Hi Peter,I am sorry to see you have rated your visit with us this afternoon just 1*. â€¦Hi Peter,I am sorry to see you have rated your visit with us this afternoon just 1*.Please do not hesitate to contact us if you wish to discuss your visit further info@panoramic34.com or you call 01512365534.More
    """
    print(find_contact_info(textemail))