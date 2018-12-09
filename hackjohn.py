"""
Bot to monitor for southbound permit spaces on the John Muir Trail
Written by Daniel Himmelstein

Check whether any spaces are available for the
"Donohue Exit Quota and Trailhead Space Available".
This is for people hiking the John Muir Trail starting in Yosemite.

Accoding to the reservations office,
the table is usually updated around 11 AM pacific time
and spaces are usually snatched within ten minutes.
Call the reservation number if there's availability at 209-372-0740.
"""

import requests
import pandas
from pkg_resources import parse_version

# Mininum number of available spaces
spaces = 2

# Comment out trailheads you'd like to start from
exclude = [
#     'Happy Isles->Little Yosemite Valley',
#     'Happy Isles->Sunrise/Merced Lake (pass through)',
    'Glacier Point->Little Yosemite Valley',
    'Sunrise Lakes',
    'Lyell Canyon',
]

# Dates you'd like to start on (inclusive of end date)
dates = pandas.date_range(start='2018-08-30', end='2018-10-05', freq='D')
dates


def get_trailhead_df():
    """
    Convert the current "Donohue Exit Quota and Trailhead Space Available" HTML table
    to a pandas.DataFrame.
    """
    pandas_version = parse_version(pandas.__version__)._version.release
    if pandas_version[:2] == (0, 23):
        # read_html malfunctions in pandas v0.23
        # https://github.com/pandas-dev/pandas/issues/22135
        raise ImportError('pandas v0.23 is not supported due to https://git.io/fp9Zn')

    url = 'https://www.nps.gov/yose/planyourvisit/fulltrailheads.htm'
    response = requests.get(url)
    response.raise_for_status()

    wide_df, = pandas.read_html(
        response.text,
        header=1,
        attrs = {'id': 'cs_idLayout2'},
        flavor='html5lib',
        parse_dates=['Date'],
    )
    wide_df = wide_df.iloc[:, :6]

    trailhead_df = wide_df.melt(id_vars='Date', var_name='Trailhead', value_name='Spaces')
    trailhead_df = trailhead_df.dropna()
    trailhead_df.Spaces = trailhead_df.Spaces.astype(int)
    assert len(trailhead_df) > 0

    return response, trailhead_df

yose_response, trailhead_df = get_trailhead_df()
trailhead_df.head(2)

space_df = trailhead_df.query("Date in @dates and Spaces >= @spaces and Trailhead not in @exclude")
space_df

space_str = space_df.to_string(index=False)
text = f'''Spaces available as of {yose_response.headers['Date']}

{space_str}

According to {yose_response.url}
Yosemite Reservations: 209-372-0740 (Monday–Friday 9:00am–4:30pm)
'''
print(text)


## Nofications using MiddlemanBot
# Uses https://github.com/n1try/telegram-middleman-bot

# Set enable_middleman to True to receive telegram notification
enable_middleman = False

# Get token from messaging /start to @MiddleManBot on Telegram
# https://telegram.me/MiddleManBot
token = 'replace-with-private-telegram-middlemanbot-token'

hostname = 'https://middleman.ferdinand-muetsch.de'
mmb_url = hostname + '/api/messages'
payload = {
    'recipient_token': token,
    'text': text,
    'origin': 'hackjohn',
}
if enable_middleman and not space_df.empty:
    mmb_response = requests.post(mmb_url, json=payload)
    print('middleman status code', mmb_response.status_code)
    print(mmb_response.text)
