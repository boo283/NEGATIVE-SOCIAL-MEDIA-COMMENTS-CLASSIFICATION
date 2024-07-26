import pandas as pd
import findspark
import json
findspark.init()
from crawl_facebook_comments import get_url, configure_driver, crawl
from io import StringIO
import time
import utils

def create_producer():
    return utils.create_producer()

def get_data(url, username, password, threshold, ite):
    cnt = 0
    driver = configure_driver()
    cmt_data, cnt = crawl(driver, url, username, password, threshold, ite)
    cmt_data_json = json.dumps(cmt_data, ensure_ascii=False)
    cmts = pd.read_json(StringIO(cmt_data_json), orient='records')
    return cmts, cnt

def produce_comments(producer, cmts):
    for index, row in cmts.iterrows():
        producer.send('StreamComments', value=row.to_dict())
        print(f"Sent comment: {row.to_dict()}")
        time.sleep(1)
    producer.flush()
    print("All comments sent!")
    producer.close()
