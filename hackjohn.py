"""
Bot to monitor for southbound permit spaces on the John Muir Trail
Written by Daniel Himmelstein

Check whether any spaces are available for the
"Donohue Exit Quota and Trailhead Space Available".
This is for people hiking the John Muir Trail starting in Yosemite.

According to the reservations office,
the table is usually updated around 11 AM pacific time
and spaces are usually snatched within ten minutes.
Fill out the online permit request form if there are available permits:
https://yosemite.org/yosemite-wilderness-permit-request-form/
"""

import pathlib
import requests
import json
from datetime import datetime, timedelta
import pytz
from twocaptcha import TwoCaptcha
from typing import Tuple, Union, List
import warnings
import pickle
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type
)

# some variables are set in config.py -- not intended to be modified
import config


######################
# Set these parameters
######################
CAPTCHA_API_KEY = "your-api-key"  # replace with your 2Captcha API key
MIN_SPACES = 1  # minimum number of available spaces
START_DATE = "2021-06-15"  # earliest date you would like to start your hike
END_DATE = "2021-09-30"    # latest date you would like to start your hike
NOTIFY_IF_NO_PERMITS = True  # send daily notification even if no permits are found?
OUTPUT_TIME_ZONE = "US/Pacific"  # what time zone to show in notifications (must be in pytz.all_timezones)

# Comment out trailheads you'd like to start from (don't change the trailhead names)
EXCLUDE_TRAILHEADS = [
    # "Happy Isles->Little Yosemite Valley",
    # "Happy Isles->Sunrise/Merced Lake (pass through)",
    # "Glacier Point->Little Yosemite Valley",
    # "Sunrise Lakes",
    # "Lyell Canyon",
]

## Telegram notification setup (optional)
ENABLE_TELEGRAM = False
TELEGRAM_TOKEN = "replace-with-personal-telegram-token"
TELEGRAM_FROM_NAME = "hackjohn"

## IFTTT notification setup (optional)
ENABLE_IFTTT = False
IFTTT_KEY = "replace-with-personal-IFTTT-key"
IFTTT_EVENT_NAME = "hackjohn"  # must match the name of the event you created

## Twilio SMS notification setup (optional)
ENABLE_TWILIO = False
TWILIO_ACCOUNT_SID = "your-twilio-account-sid"
TWILIO_AUTH_TOKEN = "your-twilio-auth-token"
TWILIO_PHONE_NUMBER = "your-twilio-account-phone-number"   # +1xxxxxxxxxx format
TWILIO_TO_PHONE = "phone-number-to-receive-notifications"  # +1xxxxxxxxxx format

###################
# end of parameters
###################


def main():
    # pull permit and trailhead data
    trailheads = get_trailhead_descriptions()
    jmt_report, timestamp = get_jmt_report()

    # choose dates, look for available permits for those dates, and create text report
    permits = find_available_permits(jmt_report, timestamp, trailheads)
    text = create_text_report(timestamp, permits, trailheads)

    # send notifications as appropriate
    notify = decide_whether_to_notify(text, permits, timestamp)
    if notify:
        if ENABLE_TELEGRAM:
            send_telegram_notification(text)
        if ENABLE_IFTTT:
            send_IFTTT_notification(text)
        if ENABLE_TWILIO:
            send_twilio_notification(text)

    print("")
    print(text)


def get_trailhead_descriptions() -> dict:
    """
    Get trailhead information (names, quotas, etc.). Returns a dictionary with
    an entry for each trailhead.

    For example, this is the entry for "j01a":
    {
        'id': 'j01a',
        'name': 'Happy Isles to Sunrise/Merced Lake Pass Thru (Donohue Pass only)',
        'wpsName': 'Happy Isles->Sunrise/Merced Lake (pass through)',
        'region': 'jm',
        'latitude': None,
        'longitude': None,
        'description': '...',
        'quota': 6,
        'capacity': 10,
        'alert': None,
        'notes': '...'
    }
    """
    print("pulling trailhead information...")
    raw_data = get_json_from_api(config.TRAILHEAD_ENDPOINT)
    trailheads = raw_data["response"]["values"]
    return trailheads


def get_jmt_report() -> Tuple[dict, datetime]:
    """
    Get the number of reserved permits from each trailhead for each date.
    Returns a dictionary with keys for dates. Each value is a dictionary with
    a key for each JMT trailhead. Also returns the timestamp of when the report
    was last updated (in PST). The raw report is a list of dicts. The list is
    reformatted into a dictionary to make it easier to work with.

    Here is a sample of the output. There is one entry per date.
    {
        '2021-08-01': {
            'j01a': 6,
            'j01b': 18,
            'j03a': 6,
            'j19': 9,
            'j24b': 21,
            'd01': 20,
            'd02': 15
        },
    }
    """
    print("pulling JMT permit availability report...")
    raw_data = get_json_from_api(config.JMT_REPORT_ENDPOINT)

    # get the timestamp
    report_timestamp = raw_data["response"]["timestamp"]
    report_timestamp = datetime.strptime(report_timestamp, "%Y-%m-%dT%H:%M:%S")
    pacific = pytz.timezone("US/Pacific")
    report_timestamp = pacific.localize(report_timestamp)

    # get the reserved permit counts and reformat
    report_vals = {}
    for val_dict in raw_data["response"]["values"]:
        date = val_dict["date"]
        report_vals[date] = val_dict.copy()
        report_vals[date].pop("date")

    return report_vals, report_timestamp


@retry(
    stop=stop_after_attempt(config.MAX_RETRY_ATTEMPTS),
    retry=retry_if_exception_type(),
    reraise=True,
)
def get_json_from_api(api_url: str) -> dict:
    """
    Get the raw data from the specified API. Sends a GET request to the URL
    provided. Uses saved cookies from the last run if they exist, otherwise
    authenticates a new session.

    The response for the yosemite.org APIs is a JSON file with keys for
    "status" and "response". The "status" entry contains a message about
    whether data was found. The "response" entry contains the data and will be
    set to None if no data was found.

    If an exception is raised, this function will be retried up to
    config.MAX_RETRY_ATTEMPTS times.

    :param api_url: URL for the GET request
    :return: JSON response from the request
    """
    cookie_file = pathlib.Path(config.COOKIE_FILE)
    if cookie_file.is_file():
        print("using saved cookies...")
        with open(cookie_file, "rb") as f:
            cookies = pickle.load(f)
        s = requests.session()
        s.cookies.update(cookies)

    else:
        print("did not find saved cookies -- getting new session...")
        s = get_authorized_session(api_key=CAPTCHA_API_KEY)

    # pull the data (should be near instantaneous, but sometimes there are
    # timeout errors which go away upon retrying)
    query = s.get(api_url, timeout=2)
    data = json.loads(query.text)

    # data["response"] will be a dict if successful, or None if not authorized
    if data["response"] is None:
        print("cookies were not valid -- deleting cookies and retrying with "
              "new session...")
        cookie_file.unlink(missing_ok=True)
        raise ValueError(f"session is not authorized")

    return data


@retry(
    stop=stop_after_attempt(config.MAX_RETRY_ATTEMPTS),
    wait=wait_fixed(config.RECAPTCHA_RETRY_INTERVAL),
    retry=retry_if_exception_type(),
    reraise=True,
)
def get_authorized_session(api_key: str) -> requests.Session:
    """
    Solve the recaptcha, then authenticate browser by sending the recaptcha
    response in a POST request. Return the authorized session.

    If an exception is raised, this function will be retried up to
    config.MAX_RETRY_ATTEMPTS times, waiting config.RECAPTCHA_RETRY_INTERVAL
    seconds between attempts.

    :param api_key: API key for the captcha solving service
    """
    print("solving captcha...")
    try:
        recaptcha_response = get_recaptcha_response(api_key)
        s = requests.session()
        r = s.post(
            url=config.RECAPTCHA_REQUEST_URL,
            data={
                "g-recaptcha-response": recaptcha_response,
                "referrer": config.REFERRER_URL,
            },
        )
        r.raise_for_status()  # raise exception if the request didn't work

        # save cookies to a file so we can try reusing later
        with open(config.COOKIE_FILE, "wb") as f:
            pickle.dump(s.cookies, f)

        return s

    except Exception as e:
        print(f"\nerror solving recaptcha -- waiting {config.RECAPTCHA_RETRY_INTERVAL} "
              f"seconds and trying again...")
        raise e


def get_recaptcha_response(api_key: str) -> str:
    """
    Solve the recaptcha  and return the response. This takes a minute or two.

    NOTE: This is configured to use 2Captcha as the captcha solving service. If
    you want to use a different service you'll have to modify this function.
    """
    solver = TwoCaptcha(apiKey=api_key)
    balance = solver.balance()
    print(f"2Captcha current balance: ${balance}...")
    if balance < 0.1:
        warnings.warn(f"2Captcha balance is running low")
    r = solver.recaptcha(sitekey=config.RECAPTCHA_SITE_KEY, url=config.WEBSITE_URL)
    return r["code"]


def find_available_permits(jmt_report: dict, timestamp: datetime, trailheads: dict) -> dict:
    """
    Search for available permits at JMT trailheads for the appropriate dates.
    Only include if there are at least MIN_SPACES available. Do not include any
    trailheads listed in EXCLUDE_TRAILHEADS.

    Logic:
    - raw report contains number of reserved permits from each trailhead per day
    - trailhead file contains the entry quota for the trailhead, as well as the
      exit quota for Donohue Pass (note that Lyell Canyon has different Donohue
      exit quota)
    - entry permits available = trailhead quota - trailhead reserved
    - Donohue exits available = Donohue quota - Donohue reserved
    --> overall available = min(entry permits available, Donohue exits available)

    Returns a dictionary of available permits. For example:
    {
        "2021-08-06: {
            "j01a": 1,
            "j24b": 2,
        },
        "2021-08-11": {
            "j01b": 1,
        }
    }

    :param jmt_report: dictionary of reserved permits (output of get_jmt_report)
    :param timestamp: timestamp of the last report update
    :param trailheads: dictionary of trailhead information (output of
    get_trailhead_descriptions)
    """
    # get appropriate date range based on user input and today's date
    start_date, end_date = get_start_end_dates(jmt_report, timestamp)
    print(f"searching for open permits from {start_date} through {end_date}...")

    available_permits = {}
    for date in date_range(start_date, end_date):
        permit_data = jmt_report[date]
        for trailhead_id in permit_data:
            if trailhead_id in ["d01", "d02"]:
                continue  # these are exit quotas, not real trailheads
            if trailheads[trailhead_id]["wpsName"] in EXCLUDE_TRAILHEADS:
                continue

            quota = trailheads[trailhead_id]["quota"]
            taken = permit_data[trailhead_id]
            trailhead_available = quota - taken

            # Lyell Canyon trailhead has a different Donohue Pass exit quota
            dh = "d02" if trailhead_id == "j24b" else "d01"
            dh_quota = trailheads[dh]["quota"]
            dh_taken = permit_data[dh]
            dh_available = dh_quota - dh_taken

            available = min(trailhead_available, dh_available)
            available = max(available, 0)

            if available >= max(MIN_SPACES, 1):
                if date not in available_permits:
                    available_permits[date] = {}
                available_permits[date][trailhead_id] = available

    return available_permits


def get_start_end_dates(jmt_report: dict, timestamp: datetime) -> Tuple[str, str]:
    """
    Choose the date range to look for permits.

    Start date must be greater than or equal to:
    - START_DATE defined at top of script
    - first date in the JMT report
    - last report date + MIN_RESERVE_DAYS (currently 2)
    - JMT trailhead opening date (currently June 15)

    End date must be less than or equal to:
    - END_DATE defined at top of script
    - last date in the JMT report
    - last report date + MAX_RESERVE_DAYS (currently 168)
    - JMT trailhead close date (currently September 30)

    :param jmt_report: dictionary of reserved permits (output of get_jmt_report)
    :param timestamp: timestamp of the last report update

    :return: start date and end date in YYYY-MM-DD format
    """
    min_found_date = min(jmt_report)
    max_found_date = max(jmt_report)
    report_date = timestamp.date()
    min_reserve_date = (report_date + timedelta(days=config.MIN_RESERVE_DAYS)).strftime("%Y-%m-%d")
    max_reserve_date = (report_date + timedelta(days=config.MAX_RESERVE_DAYS)).strftime("%Y-%m-%d")
    open_date = f"{report_date.year}-{config.OPEN_DATE}"
    close_date = f"{report_date.year}-{config.CLOSE_DATE}"
    start_date = max(START_DATE, min_found_date, min_reserve_date, open_date)
    end_date = min(END_DATE, max_found_date, max_reserve_date, close_date)
    return start_date, end_date


def create_text_report(timestamp: datetime, available_permit_dict: dict, trailheads: dict) -> str:
    """
    Convert the dictionary of available permits to a text report with human
    readable trailhead names. This is the text that will be written to the
    output file and sent in notifications.
    """
    out_tz = pytz.timezone(OUTPUT_TIME_ZONE)
    timestamp_str = timestamp.astimezone(out_tz).strftime("%Y-%m-%d %-I:%M:%S %p %Z")
    update_str = f"Report last updated {timestamp_str}.\n"
    if len(available_permit_dict) == 0:
        text = f"NO AVAILABLE PERMITS\n\n{update_str}"
    else:
        text_list = []
        for date in available_permit_dict:
            date_text = f"{date}:"
            for trailhead_id in available_permit_dict[date]:
                n = available_permit_dict[date][trailhead_id]
                trailhead_name = trailheads[trailhead_id]["wpsName"]
                date_text += f"\n{n} permit{'s' if n != 1 else ''} for {trailhead_name}"
            text_list.append(date_text)

        text = "\n\n".join(text_list)
        text += f"\n\n{update_str}"
        text += f"\nPermit request form: {config.PERMIT_REQUEST_FORM_URL}"
        text += f"\nPermit office phone: {config.PERMIT_OFFICE_PHONE}"

    return text


def decide_whether_to_notify(text: str, permits: dict, timestamp: datetime) -> bool:
    """
    Write output file and decide whether to notify. Send notification if all of
    the following are true:
    - there are available permits (or NOTIFY_IF_NO_PERMITS is True)
    - the contents of the output file have changed
    - the updated happened after MIN_REPORT_DATE
    """
    # Detect if output_path has changed. If so, rewrite output.
    output_has_changed = True
    if config.OUTPUT_PATH is not None:
        output_path = pathlib.Path(config.OUTPUT_PATH)
        if output_path.is_file():
            previous_text = output_path.read_text()
            output_has_changed = text != previous_text
        if output_has_changed:
            print(f"writing to {output_path.absolute()}")
            output_path.write_text(text)
        else:
            print("no change since last run")

    # determine whether to notify
    notify = (
        ((len(permits) > 0) or NOTIFY_IF_NO_PERMITS)
        and output_has_changed
        and (config.MIN_REPORT_DATE <= timestamp.strftime("Y-%m-%d"))
    )
    return notify


def date_range(
    start: str,
    end: str,
    date_format: str = "%Y-%m-%d",
    inclusive_end: bool = True,
) -> str:
    """Return a generator for looping through a range of dates."""
    start = datetime.strptime(start, date_format)
    end = datetime.strptime(end, date_format)
    i = 1 if inclusive_end else 0
    for n in range(int((end - start).days) + i):
        yield (start + timedelta(n)).strftime(date_format)


def send_telegram_notification(text: str):
    """
    Send a notification to the Telegram app. Uses the TELEGRAM_TOKEN and
    TELEGRAM_FROM_NAME parameters at the top of this script.
    """
    payload = {
        "recipient_token": TELEGRAM_TOKEN,
        "text": text,
        "origin": TELEGRAM_FROM_NAME,
        "options": {
            "disable_link_previews": True
        },
    }
    r = requests.post(config.TELEGRAM_URL, json=payload)
    r.raise_for_status()


def send_IFTTT_notification(text: str):
    """
    Send a notification using your IFTTT applet. Uses the IFTTT_EVENT_NAME and
    IFTTT_KEY parameters at the top of this script.
    """
    report = {
        "value1": text.replace("\n", "<br />"),
        "value2": config.PERMIT_OFFICE_PHONE,
    }
    url = f"{config.IFTTT_HOSTNAME}/trigger/{IFTTT_EVENT_NAME}/with/key/{IFTTT_KEY}"
    r = requests.post(url, data=report)
    r.raise_for_status()


# only need the twilio package if we're sending SMS
if ENABLE_TWILIO:
    from twilio.rest import Client


def send_twilio_notification(
        text: str,
        from_phone: str = TWILIO_PHONE_NUMBER,
        to_phone: Union[str, List[str]] = None,
):
    """
    Send SMS text message using Twilio. Uses the TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, and TWILIO_TO_PHONE parameters at
    the top of this script.

    :param text: contents of text message
    :param from_phone: phone number to send message (Twilio phone number)
    :param to_phone: phone number(s) to receive message
    """
    # send SMS message(s)
    to_phone = to_phone or TWILIO_TO_PHONE
    to_phone = _force_to_list(to_phone)
    from_phone = _parse_phone_number(from_phone)
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    for x in to_phone:
        client.messages.create(
            body=text,
            from_=from_phone,
            to=_parse_phone_number(x),
        )

    # report twilio balance
    balance_data = client.api.v2010.balance.fetch()
    balance = float(balance_data.balance)
    currency = balance_data.currency
    print(f"current twilio balance: {balance} {currency}")
    if balance < 0.1:
        warnings.warn(f"twilio balance is running low")


def _parse_phone_number(phone_number: str) -> str:
    """Parse the digits from a string and format as +1xxxxxxxxxx"""
    phone_number = "".join(filter(str.isdigit, phone_number))
    if len(phone_number) == 10:
        phone_number = f"1{phone_number}"
    return f"+{phone_number}"


def _force_to_list(x) -> list:
    if not isinstance(x, list):
        x = [x]
    return x


if __name__ == "__main__":
    main()
