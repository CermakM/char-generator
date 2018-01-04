"""Scrape fonts from the given website

NOTES
-----
- you should check a website’s Terms and Conditions before you scrape it
- be careful to read the statements about legal use of data
- usually, the data you scrape should not be used for commercial purposes
"""

import os
import sys

import re
import requests

from bs4 import BeautifulSoup


BASE_URL = 'https://www.1001freefonts.com/'


response = requests.get(BASE_URL)
soup = BeautifulSoup(response.content, 'html.parser')

page_label = soup.find('div', attrs={'class': 'pagingLabelWrapper'})

try:
    # Get number of pages
    pages = re.search(r"(?<=1 of )[0-9]+", page_label.string).group()
    pages = int(pages)
except ValueError:
    print("Wrong page index:", pages or '-', file=sys.stderr)
    exit(1)

# Create font directory
if not os.path.isdir('fonts'):
    os.mkdir('fonts')
else:
    print("fonts folder already exists! Exitting ...", file=sys.stderr)
    exit(1)

for page in range(1, pages + 1):
    url = BASE_URL + "new-fonts-{page}.php".format(page=page)

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get download buttons
    buttons = soup.find_all(
            lambda t: len(dict.get(t.attrs, 'class', [])) == 1,
            attrs={'class': lambda c: c == 'downloadButtonElement'}
            )

    for button in buttons:
        font_url = button.find('a').get('href')
        search = re.search(r"([^/]+)(.zip)$", font_url)
        font_name = search.group(1)
        file_name = search.group(0)

        content = requests.get(font_url).content

        if content and type(content) is bytes:
            font_dir = os.path.join('fonts', font_name)
            try:
                os.mkdir(font_dir)
            except FileExistsError:
                continue

            with open(os.path.join(font_dir, file_name), 'wb') as font_file:
                font_file.write(content)

