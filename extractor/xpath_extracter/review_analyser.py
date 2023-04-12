import re


def get_phones(text):
    patterns = [
        r"(?:\+1)?\s*\(?(\d{3})\)?[\s.-]*(\d{3})[\s.-]*(\d{4})",
        r"(?:\+44\s*(?:\(|0)(\d{1,5})\)?[\s.-]*(\d{4})[\s.-]*(\d{4}))",
        r"\+(?P<country_code>\d{1,3})\s*(?P<area_code>\d{1,5})\s*(?P<phone_number>\d{6,10})",
        r"\d{3}-\d{3}-\d{4}",
        r'\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b'
    ]
    numbers = []
    for pattern in patterns:
        matches = re.findall(pattern,text)
        for match in matches:
            print(match)
            numbers.append('-'.join(list(match)))
    if numbers:
        return numbers
    return None
def find_contact_info(text):
    # Define regular expressions for different types of contact info
    email_url_re_with_hhtps = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
    email_url_re_without_https = r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
    us_phonenumbers_pattern = r'^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$'
    non_us_phonenumber_patterns = r'^(\+0?1\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$'
    non_standard_phonenumbers_pattern = r'^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'
    # Compile regular expressions
    email_regex = re.compile(email_url_re_with_hhtps, re.IGNORECASE)
    email_regex2 = re.compile(email_url_re_without_https, re.IGNORECASE)
    phone_regex1 = re.compile(us_phonenumbers_pattern, re.IGNORECASE)
    phone_regex2 = re.compile(non_us_phonenumber_patterns, re.IGNORECASE)
    phone_regex3 = re.compile(non_standard_phonenumbers_pattern, re.IGNORECASE)
    # Find all matches in the text
    matches = []
    matches.extend(email_regex.findall(text))
    matches.extend(email_regex2.findall(text))
    matches.extend(phone_regex1.findall(text))
    matches.extend(phone_regex2.findall(text))
    matches.extend(phone_regex3.findall(text))
    # Remove duplicates
    matches = list(set(matches))
    return matches

if __name__ == '__main__':
    text = """
    Hey there,

I wanted to reach out and let you know that our website, www.example.com, is now live! You can check it out and let me know what you think.

Also, I noticed that you left your phone number in our contact form. If you'd like, we can give you a call to discuss our services further. Our number is 555-123-4567.

And finally, I wanted to connect with you on social media. Here's a link to our Facebook page: https://www.facebook.com/example. And if you're on Twitter, you can follow us here: https://twitter.com/example.
 +49 1234 56789
Looking forward to hearing back from you soon.

Best regards,
John Doe
"My phone number is +44 (0) 20 1234 5678
john.doe@example.com
    """
    print(get_phones(text))
    print(find_contact_info(text))