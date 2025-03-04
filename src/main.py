from utils import Helper
from processor import Processor
import re
import importlib
import json
import asyncio
import logging
from asyncioReq import AsyncRequester

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_single_school(category):
    _processor = Processor()
    items = []
    config_item = {
        "college/university": "Brown University",
        "school name": "Brown Bears",
        "website": "brownbears.com",
        "urls": [
            {
                "url": "https://brownbears.com/sports/womens-ice-hockey/coaches",
                "category": "Women's College Hockey DI Coaches",
                "location": "Rhode Island",
                "conference": "ECAC"
            },
            {
                "url": "https://brownbears.com/sports/mens-ice-hockey/coaches",
                "category":"Men's College Hockey DI Coaches",
                "location": "Rhode Island",
                "conference": "ECAC"
            }
        ],
        "module": "parser.brownbears",
        "class": "Parser"
    }
    
    special = [
        "Lakehead University"
    ]
    
    urls = [url for url in config_item["urls"] if url["category"] in category]
    for url in urls:
        print(f'Processing {config_item["school name"]}')
        _processor.get_module(config_item, url) # set module
        if config_item["college/university"] in special:
            raw_html = AsyncRequester.get(url["url"])
            raw_html = [raw_html, url["url"]]
            items.extend(_processor.get_items(raw_html))
        else:
            coaches_urls = _processor.get_coaches_urls(url)
            raw_html = AsyncRequester().run(coaches_urls)
            items.extend(_processor.multi_process(raw_html))
    print(items)

def new_run(category):
    try:
        _helper = Helper()
        item = [config for config in _helper.read_from_json('config/config_sheet.json') if config["sheet_id"] == category][0]
        if category == "men's ice hockey":
            _helper.clear_csv(item["output"])
            _helper.clear_failed_config()
            Processor().process(item)
        else:
            pass
    except Exception as e:
        print(f"Error: {e}")

# rerun failed config
def rerun(category):
    try:
        _helper = Helper()
        logging.info(f'Rerunning failed config')
        failed_config = _helper.read_from_json("failed_config.json")
        _helper.clear_failed_config()
        item = [config for config in _helper.read_from_json('config/config_sheet.json') if config["sheet_id"] == category][0]
        if category == "men's ice hockey":
            Processor().process(item, failed_config)
        else:
            pass
    except Exception as e:
        logging.error(f'Error in rerun: {e}')

if __name__ == '__main__':
    
    new_run("men's ice hockey")
    # rerun("men's ice hockey")
    
    # category = [
    #         "Men's College Hockey DI Coaches",
    #         "Men's College Hockey DIII Coaches",
    #         "Men's U Sports Hockey Coaches"
    #     ]
    # get_men_hockey()
    