from bs4 import BeautifulSoup
from requester import Requester

class Parser():
    def __init__(self, school, base_url, category, location, conference):
        self.school = school
        self.base_url = base_url
        self.category = category
        self.location = location
        self.conference = conference
    
    def process(self, raw_html, url):
        try:
            item = self.get_item(self.school, raw_html, url)
            return item
        except Exception as e:
            return []
        
    def raw_html_to_soup(self, raw_html):
        return BeautifulSoup(raw_html, 'html.parser')
    
    def get_item(self, school, raw_html, url):
        _soup = self.raw_html_to_soup(raw_html)
        item = {}
        item['First Name'], item['Last Name']  = self.get_name(_soup)
        item['Title'] = self.get_title(_soup)
        item['School'] = school
        item['Email'] = self.get_email(_soup)
        item['Phone'] = self.get_number(_soup)
        item['Profile URL'] = url
        item['Category'] = self.category
        item['Location'] = self.location
        item['Conference'] = self.conference
        
        return item
    
    def get_coaches_url(self, *args, **kwargs):
        try:
            soup = self.raw_html_to_soup(kwargs['raw_data'])
            urls = []
            parent_tag = soup.select_one('#coaching-staff')
            if parent_tag:
                next_tag = parent_tag.find_next_sibling()
                tags = next_tag.select('.card-body a')
                if tags:
                    urls = [f"{self.base_url}{tag.get('href')}" for tag in tags]
            return urls
        except:
            return None
    
    def get_name(self, soup):
        try:
            f_name = None
            l_name = None
            tag = soup.select_one('.name')
            if tag:
                name =  tag.get_text().strip().split(' ')
                name = [item for item in name if item] # Cleanse or remove empty strings
                f_name = name[0]
                l_name = name[1]
            return f_name, l_name
        except:
            return None, None
        
    def get_title(self, soup):
        try:
            title = None
            tag = soup.find(lambda tag: tag.name == "dl" and "Title" in tag.text)
            if tag:
                title = tag.select_one('dd').get_text().strip()
            return title
        except:
            return None
        
    def get_email(self, soup):
        try:
            email = None
            tag = soup.find(lambda tag: tag.name == "dl" and "Email" in tag.text)
            if tag:
                email = tag.select_one('dd').get_text().strip()
            return email
        except:
            return None
    
    def get_number(self, soup):
        try:
            number = None
            tag = soup.find(lambda tag: tag.name == "dl" and "Phone" in tag.text)
            if tag:
                number = tag.select_one('dd').get_text().strip()
            return number
        except:
            return None