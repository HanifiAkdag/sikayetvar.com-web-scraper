from bs4 import BeautifulSoup
from cloudscraper import create_scraper
import lxml
from time import sleep
import json
import csv
import os
import sys

DOMAIN = 'https://www.sikayetvar.com'


def get_max_page(brand):
    scraper = create_scraper()
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.1.2222.33 Safari/537.36",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
    }
    page = scraper.get(f'{DOMAIN}/{brand}', headers=headers)
    if page.status_code != 200:
        wait_time = int(page.headers['Retry-after'])
        print(f"Error: {page.status_code}")
        print(f"Sleeping for {wait_time+1} seconds")
        sleep(wait_time+1)
        page = scraper.get(f'{DOMAIN}/{brand}', headers=headers)
    soup = BeautifulSoup(page.content, "lxml")
    return int(soup.find("ul", {'class':'pagination'}).text.split()[-1])


def extract_complaint(url):
    scraper = create_scraper()
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.1.2222.33 Safari/537.36",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
    }
    page = scraper.get(url, headers=headers)
    if page.status_code != 200:
        wait_time = int(page.headers['Retry-after'])
        print(f"Error: {page.status_code}")
        print(f"Sleeping for {wait_time+1} seconds")
        sleep(wait_time+1)
        page = scraper.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "lxml")
    try:
        data = json.loads(soup.find('script', type='application/ld+json').text)
        return data
    except AttributeError:
        print(url)
        return "ERROR"


def iter_complaint_urls(brand, page_num):
    scraper = create_scraper()
    url = f'{DOMAIN}/{brand}?page={page_num}'
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.1.2222.33 Safari/537.36",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
    }
    page = scraper.get(url, headers=headers)
    if page.status_code != 200:
        wait_time = int(page.headers['Retry-after'])
        print(f"Error: {page.status_code}")
        print(f"Sleeping for {wait_time+1} seconds")
        sleep(wait_time+1)
        page = scraper.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "lxml")

    for i in soup.find_all('div', {'class':'read-more-container'}):
        yield DOMAIN + i.find('span')['data-url']


def iter_pages(brand, start, end):
    end = min(end, get_max_page(brand))
    for page_num in range(start, end+1):
        print(f"Scraping page {page_num}")
        for url in iter_complaint_urls(brand, page_num):
            yield url
        print()


def write_to_csv(complaint, file_name):
    with open(file_name, mode='a+', encoding='utf-8', newline='') as f:
        field_names = ['text', 'date_published', 'headline', 'url']
        writer = csv.DictWriter(f, fieldnames=field_names)
        try:
            writer.writerow({'text': complaint['mainEntity']['articleBody'].replace('\n', ' ').replace('\r', ' '),
                         'date_published': complaint['mainEntity']['datePublished'],
                         'headline': complaint['headline'],
                         'url': complaint['url']})
        except KeyError:
            print("KeyError")


def scrap(brand, start, end, respond):
    file_name = f'{brand}_complaints.csv'
    if os.path.isfile(f'{brand}_complaints.csv'):
        respond = input("A csv file already exists. Do you want to overwrite (w), append (a) or create a new file (n)? ")
        if respond == 'w':
            os.remove(f'{brand}_complaints.csv')
        elif respond == 'n':
            tmp = 1
            while os.path.isfile(f'{brand}_complaints_{tmp}.csv'):
                tmp += 1
            file_name = f'{brand}_complaints_{tmp}.csv'
            
    for url in iter_pages(brand, start, end):
        complaint = extract_complaint(url)
        write_to_csv(complaint, file_name)
    print("Done")
    
if __name__ == "__main__":
    if len(sys.argv) == 4:
        scrap(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    else:
        print("Usage: python scraper.py <brand> <start_page> <end_page>")