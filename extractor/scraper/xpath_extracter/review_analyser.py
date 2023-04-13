import re


def find_contact_info(text):
    # Define regular expressions for different types of contact info
    email_url_re_with_hhtps = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
    email_url_re_without_https = r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
    us_phonenumbers_pattern = r'^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$'
    non_us_phonenumber_patterns = r'^(\+0?1\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$'
    non_standard_phonenumbers_pattern = r'^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'
    # Find all matches in the text
    matches = []

    try:
        email_regex = re.search(email_url_re_with_hhtps, text,re.IGNORECASE).group()
        matches.append(email_regex)
    except:
        pass

    try:
        email_regex2 = re.search(email_url_re_without_https, text,re.IGNORECASE).group()
        matches.append(email_regex2)
    except:
        pass

    try:
        phone_regex1 = re.search(us_phonenumbers_pattern, text,re.IGNORECASE).group()
        matches.append(phone_regex1)
    except:
        pass
    try:
        phone_regex2 = re.search(non_us_phonenumber_patterns, text,re.IGNORECASE).group()
        matches.append(phone_regex2)
    except:
        pass
    try:
        phone_regex3 = re.search(non_standard_phonenumbers_pattern, text,re.IGNORECASE).group()
        matches.append(phone_regex3)
    except:
        pass



    # Remove duplicates
    matches = list(set(matches))
    final_contacts = []
    for contact in matches:
        if contact == "" or str(contact).isspace() or len(contact) < 7:
            continue
        final_contacts.append(final_contacts)

    return matches

if __name__ == '__main__':
    text = """
Hi Georgia, I'm so sorry to hear that you were not fully happy with your experience. Could you please send us an email at Reservations@ikoyilondon.com and we can further discuss this? Thank you.
    """
    print(find_contact_info(text))