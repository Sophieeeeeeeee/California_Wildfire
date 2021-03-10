"""
Download data from the website
"""
import pprint
import datetime
import requests
import re
import time
from bs4 import BeautifulSoup
from typing import Tuple, List, Dict

# NUM_TO_MONTH = {1: 'January', 2: 'February', 3: 'March', 4: 'April',
#                 5: 'May', 6: 'June', 7: 'July', 8: 'August',
#                 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

MONTH = ('January', 'February', 'March', 'April', 'May', 'June',
         'July', 'August', 'September', 'October', 'November', 'December')


def get_date_temp(date: datetime.datetime, date_temp: dict):
    return date_temp[date.year][MONTH[date.month - 1]][date.day - 1][1:]


def get_years_temp(begin_year: int, end_year: int, show_process=True) -> Dict:
    years_temp = {}
    for year in range(begin_year, end_year + 1):
        years_temp = {**years_temp, **get_year_temp(year, show_process)}
    return years_temp


def get_year_temp(year: int, show_process: bool) -> Dict:
    month_to_temp = {}
    for month in MONTH:
        if show_process:
            print('\r', 'Collecting temperature in', year, month + '...', end='')
        month_to_temp[month] = get_month_max_min_temp(str(year), month)
        if show_process:
            print('\r', '       Got temperature in', year, month, end='')
        time.sleep(1)
    if show_process:
        print('\r', 'Collected all temperatures in', year, 'successfully')
    return {year: month_to_temp}


def get_month_max_min_temp(year: str, month: str) -> Tuple:
    url = 'https://www.usclimatedata.com/ajax/load-history-content'
    data = {'token': 'd53b354840835415f751abd5f1ac1bd2ShpyrPAjs1iF3xuZGWfHrLyqo/gqAXYWzP6hcMYXSjZxBF7qHg==',
            'page': 'climate',
            'location': 'usca0967',
            'month_year': month + ' ' + year,
            'tab': '#history',
            'unit': 'american',
            'unit_required': 0,
            'unit_changed': 0
            }
    response = requests.post(url, data)
    json_response = response.json()
    html_temp_table = json_response['table']
    soup_table = BeautifulSoup(html_temp_table, "html.parser")
    all_max = soup_table.find_all('td', class_='high text-right')
    all_min = soup_table.find_all('td', class_='low text-right')
    day_num = len(all_max)

    max_min_temp = form_month_date(int(year), MONTH.index(month) + 1, day_num)
    for i in range(day_num):
        max_min_temp[i] += ((float(re.search("\d+(\.\d+)?", str(all_max[i])).group()),
                             float(re.search("\d+(\.\d+)?", str(all_min[i])).group())))
    return tuple(max_min_temp)


def form_month_date(year: int, month: int, day_num: int) -> List[Tuple]:
    month_date = []
    for x in range(1, day_num + 1):
        month_date.append((datetime.date(year, month, x),))
    return month_date


if __name__ == '__main__':
    # print(get_month_max_min_temp('2007', 'February'))
    # print(form_month_date(2010, 12, 31))
    x = get_years_temp(2007, 2007, show_process=True)
    pprint.pprint(x)
    print(get_date_temp(datetime.datetime(2007, 9, 2, 11, 40), x))
