import logging
from bs4 import BeautifulSoup
from requester import Requester

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Parser():
    def __init__(self, school, base_url, category, location, conference):
        self.school = school
        self.base_url = base_url
        self.category = category
        self.location = location
        self.conference = conference
        logging.info(f'Initialized Parser for {school}')

    def process(self, raw_html, url):
        try:
            logging.info(f'Processing URL: {url}')
            item = self.get_item(self.school, raw_html, url)
            return item
        except Exception as e:
            logging.error(f'Error processing URL {url}: {e}')
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
        item['Image URL'] = self.image_url(_soup)
        item['Profile URL'] = url
        item['Category'] = self.category
        item['Location'] = self.location
        item['Conference'] = self.conference
        
        
        return item

    def get_coaches_url(self, *args, **kwargs):
        try:
            soup = self.raw_html_to_soup(kwargs['raw_data'])
            urls = []
            tags = soup.select('[class="info"] p a')
            if tags:
                urls = [f"{self.base_url}{tag.get('href')}" for tag in tags if tag.get('href').startswith('/sports')]
            logging.info(f'Found coaches URLs: {urls}')
            return urls
        except Exception as e:
            logging.error(f'Error getting coaches URLs: {e}')
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
        except Exception as e:
            logging.error(f'Error getting name: {e}')
            return None, None

    def get_title(self, soup):
        try:
            title = None
            tag = soup.find(lambda tag: tag.name == "tr" and "Title" in tag.text)
            if tag:
                title = tag.select_one('td').find_next_sibling().get_text().strip()
            return title
        except Exception as e:
            logging.error(f'Error getting title: {e}')
            return None

    def get_email(self, soup):
        try:
            email = None
            tag = soup.find(lambda tag: tag.name == "tr" and "Email" in tag.text)
            if tag:
                email = tag.select_one('td').find_next_sibling().get_text().strip()
            return email
        except Exception as e:
            logging.error(f'Error getting email: {e}')
            return None

    def get_number(self, soup):
        try:
            number = None
            tag = soup.find(lambda tag: tag.name == "tr" and "Phone" in tag.text)
            if tag:
                number = tag.select_one('td').find_next_sibling().get_text().strip()
            return number
        except Exception as e:
            logging.error(f'Error getting number: {e}')
            return None

    def image_url(self, soup):
        try:
            tag = soup.select_one('.player-headshot img')
            if tag:
                image_url = tag.get('src')
                return image_url
            return None
        except Exception as e:
            logging.error(f'Error getting image URL: {e}')
            return None