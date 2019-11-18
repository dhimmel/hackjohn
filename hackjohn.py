"""
Bot to monitor for southbound permit spaces on the John Muir Trail
Written by Daniel Himmelstein

Check whether any spaces are available for the
"Donohue Exit Quota and Trailhead Space Available".
This is for people hiking the John Muir Trail starting in Yosemite.

According to the reservations office,
the table is usually updated around 11 AM pacific time
and spaces are usually snatched within ten minutes.
Call the reservation number if there's availability at 209-372-0740.
"""

import pathlib
import re

import requests
import pandas
from pkg_resources import parse_version

# Minimum number of available spaces
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
dates = pandas.date_range(start='2019-08-30', end='2019-10-05', freq='D')
dates

# Write output to this file. If the generated output is identical to
# the existing output at this path, suppress notification. To disable
# writing any files, set output_path=None as shown below.
output_path = pathlib.Path('__file__').parent.joinpath('hackjohn-output.txt')
# output_path = None  # None disables writing to a file

# If the Report Date is before this day, suppress Telegram notification.
# You probably do not need to change this setting unless you have disabled
# output_path
min_report_date = '2019-01-01'


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

    trailhead_df = (
        wide_df
        .melt(id_vars='Date', var_name='Trailhead', value_name='Spaces')
        .dropna()
        .sort_values(by=['Date'], kind='mergesort')
    )
    trailhead_df.Spaces = trailhead_df.Spaces.astype(int)
    assert len(trailhead_df) > 0

    return response, trailhead_df


yose_response, trailhead_df = get_trailhead_df()
trailhead_df.head(2)

# Extract report date. https://github.com/dhimmel/hackjohn/issues/1
try:
    match = re.search(r'Report Date: ([0-9/]+)', yose_response.text)
    report_date = match.group(1)
    report_date = pandas.to_datetime(report_date, dayfirst=False)
except Exception:
    report_date = yose_response.headers['Date']
    report_date = pandas.to_datetime(report_date, utc=True)
report_date = report_date.date().isoformat()

space_df = trailhead_df.query("Date in @dates and Spaces >= @spaces and Trailhead not in @exclude")
space_df

space_str = 'NO VACANCY' if space_df.empty else space_df.to_string(index=False)
text = f'''Spaces available as of {report_date}:

{space_str}

According to {yose_response.url}
Yosemite Reservations: 209-372-0740 (Monday–Friday 9:00am–4:30pm)
'''
print(text)
# Detect if output_path has changed. If so, rewrite output.
output_has_changed = True
if output_path:
    output_path = pathlib.Path(output_path)
    if output_path.is_file():
        previous_text = output_path.read_text()
        output_has_changed = text != previous_text
    if output_has_changed:
        output_path.write_text(text)
print(f'output has changed: {output_has_changed}')

# determine whether to notify
notify = not space_df.empty and output_has_changed and min_report_date <= report_date

## Notifications using MiddlemanBot
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
if notify and enable_middleman:
    mmb_response = requests.post(mmb_url, json=payload)
    print('middleman status code', mmb_response.status_code)
    print(mmb_response.text)

## Notifications using IFTTT

# Set enable_ifttt to True and personalize ifttt_key to receive IFTTT notifications
enable_ifttt = False
event_name = 'hackjohn'
ifttt_key = 'replace-with-ifttt-key'

"""
## IFTTT Setup Instructions

Create you own IFTTT at https://ifttt.com/create.
Select webhooks for this and select "Receive a web request".
Set event name to match `event_name` variable above.
Create a that to respond to the event.
For example, select "Send a rich notification from the IFTTT app"
(IFTTT rich notifications allow click to call options to the reservation line).
You can add 3 values (specified below).
For example, use `{{Value1}}` for the message template and `tel: {{Value2}}` as link action.
Go to https://ifttt.com/maker_webhooks and click on documentation,
copy & paste your key into the `ifttt_key` variable above.
"""

ifttt_hostname = 'https://maker.ifttt.com'
ifttt_url = ifttt_hostname + '/trigger/' + event_name + '/with/key/' + ifttt_key

if notify and enable_ifttt:
    report = {
        "value1": text,
        "value2": '209-372-0740',
    }
    response = requests.post(ifttt_url, data=report)
    print('ifttt status code', response.status_code)
    print(response.text)
