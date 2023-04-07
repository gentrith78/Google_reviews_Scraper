import re

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