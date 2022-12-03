#!/bin/python3

from pathlib import Path
import requests as req
import os
import sys
import json

# -- Run file -- #
# python3 script.py <API_KEY>
# or
# ./script.py <API_KEY>

# -- Install if needed -- #
# pip3 install requests


end = '\033[0m'
Q = f'\033[0;34m[?]{end}'
O = f'\033[0;32m[!]{end}'
W = f'\033[0;31m[!!]{end}'


def validate():
    if len(sys.argv) != 2:
        print(f'\n{W} Use: python3 {sys.argv[0]} <API_KEY>\n')
        sys.exit(1)
    return sys.argv[1]


def get_data(api_key):
    headers = {}
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    place_id = input(f'\n{Q} What PLACE ID are you looking for: ')
    params = dict(
        place_id=place_id,
        key=api_key
    )

    res = req.get(url, headers=headers, params=params)
    data = res.json().get('result')

    def err():
        print(f'\n{W} Request error...\n{W} Request URL: {res.url}\n')
        sys.exit(1)

    return data if data else err()


def extract_values(data):
    name = data['name']
    rating = int(data['rating'])
    phone_number = data['formatted_phone_number']
    opening_hours = data['opening_hours']['weekday_text']
    website = data['website']

    look_up = ['author_name', 'rating', 'text',
               'profile_photo_url', 'relative_time_description']

    reviews = []
    for review in data['reviews']:
        reviews.append({k: v for k, v in review.items() if k in look_up})

    adrs_lst = data['formatted_address'].split(',')

    address = dict(
        street='',
        number='',
        zipCode='',
        city=''
    )

    try:
        for i, k in enumerate(address):
            if k == 'zipCode':
                address[k] = adrs_lst[i].split()[0]
            elif k == 'city':
                address[k] = adrs_lst[i-1].split()[1]
            elif k == 'number':
                address[k] = int(adrs_lst[i])
            else:
                address[k] = adrs_lst[i].strip()
    except IndexError:
        print(
            f'\n{W} Error while extracting data. Check the Google maps API response...\n')
        sys.exit(1)

    return rating, reviews, phone_number, address, opening_hours, website, name


def results(pl):
    reviews = pl[1]
    print(
        f'\n{O} Results: \n\t- Name: {pl[6]} \n\t- Rating: {pl[0]} \n\t- N of reviews: {len(reviews)}\n\t- Phone number: {pl[2]}\n\t- Website: {pl[5]}\n\t- Address: {pl[3]}\n\t- Opening hours: {pl[4]}')

    detail = input(f'\n{Q} Would you like to see the reviews [y/N]: ') or 'N'

    if detail in 'yY':
        i = input(
            f'\n{Q} Which review whould you like to see? There are {len(reviews)} reviews. [1-{len(reviews)}/a]: ')

        if i.isdigit() and int(i) <= len(reviews):
            review = reviews[int(i)-1]
            print(f'\n{O} Review number {i}:\n\n{i} - {review}')

        elif i in 'aA':
            print(f'\n{O} All reviews:')
            for i, rev in enumerate(reviews):
                print(f'\n{i+1} - {rev}')

    elif detail in 'nN':
        return


def output(pl):
    ra, re, ph, ad, op, we, na = pl

    r = input(
        f'\n{Q} Would you like to write the results to a JSON file [y/N]: ') or 'N'

    if r in 'yY':
        path = Path(__file__).resolve().parent
        target_path = os.path.join(path, 'results')
        file_name = input(f'\n{O} Please type the new file name: ')
        full_path = os.path.join(target_path, file_name)

        parsed_data = dict(
            name=na,
            address=ad,
            extraInfo={'website': we, 'tel': ph},
            openingHours=op,
            punctuation={'rating': ra, 'reviews': re}
        )

        try:
            os.chdir(target_path)
            with open(f'{file_name}.json', 'w') as f:
                json.dump(parsed_data, f)
                print(f'{O} File {full_path}.json written...')
        except FileNotFoundError:
            print(f'\n{W} Make sure that the results folder exists...')
            sys.exit(1)


def repeat():
    rep = input(
        f'\n{Q} Make another request with a different PLACE ID [Y/n]: ') or 'Y'

    if rep in 'nN':
        print(f'\n{O} Exiting... Bye!\n')
        sys.exit(0)


def main():
    api_key = validate()
    while True:
        try:
            data = get_data(api_key)
            payload = extract_values(data)
            results(payload)
            output(payload)
            repeat()
        except KeyboardInterrupt:
            print(f'\n\n{W} Process interrupted by user...')
            sys.exit(1)


if __name__ == '__main__':
    main()
