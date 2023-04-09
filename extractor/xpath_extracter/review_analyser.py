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
    email_re = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_re = r'\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b'
    website_re = r'\b(?:https?://)?(?:www\.)?[\w-]+\.[\w]{2,3}\b'
    social_media_re = r'\b(?:https?://)?(?:www\.)?(facebook|twitter|instagram)\.com/\S+\b'
    # Compile regular expressions
    email_regex = re.compile(email_re, re.IGNORECASE)
    phone_regex = re.compile(phone_re, re.IGNORECASE)
    website_regex = re.compile(website_re, re.IGNORECASE)
    social_media_regex = re.compile(social_media_re, re.IGNORECASE)
    # Find all matches in the text
    matches = []
    matches.extend(email_regex.findall(text))
    matches.extend(phone_regex.findall(text))
    matches.extend(website_regex.findall(text))
    matches.extend(social_media_regex.findall(text))
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