import requests
from bs4 import BeautifulSoup

import json
import csv

FIELDS = [
    'institution.displayName',
    'ranking.sortRank',
    'ranking.isTied'
]

DETAILED = True
DETAIL_FIELDS = [
    'Visit School Website'
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
}


def traverse(root, path):
    value = root
    for segment in path.split('.'):
        if segment.isdigit():
            value = value[int(segment)] if len(value) > int(segment) else None
        else:
            value = value.get(segment, None)
    return value


def fetch_results_page(url, writer, num_pages=20, index=0):
    if index >= num_pages:
        return
    
    print('Fetching ' + url + '...')
    resp = requests.get(url, headers=HEADERS)
    json_data = json.loads(resp.text)
    for school in json_data['data']['items']:
        row = []
        for field in FIELDS:
            row.append(traverse(school, field))

        if DETAILED:
            resp = requests.get('https://www.usnews.com/best-colleges/' + traverse(school, 'institution.urlName') + '-'
                                + traverse(school, 'institution.primaryKey'), headers=HEADERS)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for field in DETAIL_FIELDS:
                field_element = soup.find(text=field)
                if field_element is None:
                    row.append(None)
                    continue
                parent = field_element.parent.parent
                if field == 'Visit School Website':
                    row.append(parent.a['href'] if parent.a else None)
                else:
                    row.append(parent.find_all('p')[-1].text)

        writer.writerow(row)

    if json_data['meta']['rel_next_page_url']:
        fetch_results_page(json_data['meta']['rel_next_page_url'], writer, num_pages, index + 1)
    else:
        print('Done!')

def main(n_pages):
    with open('C:/Users/Tony Zheng/codestuff/Hobby Projects/College-Font-Rankings/Scraper/data-detailed.csv' if DETAILED else 'data.csv', 'w') as data_file:
        data_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        data_writer.writerow(FIELDS + (DETAIL_FIELDS if DETAILED else []))
        fetch_results_page('https://www.usnews.com/best-colleges/api/search?_sort=rank&_sortDirection=asc&_page=1',
                        data_writer, n_pages)

if __name__ == "__main__":
    main()