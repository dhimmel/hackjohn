"""
Set the parameters at the top of this file to control which dates and
trailheads you are notified for and which types of notifications you receive.

This should be the only file you need to modify. After you fill in the
parameters in this file, you can run hackjohn.py.
"""

# replace with your 2Captcha API key (required)
CAPTCHA_API_KEY = "your-2Captcha-api-key"

# customize the dates and trailheads you want to be notified for
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

"""
END OF REQUIRED PARAMETERS

--------------------------------------------------------------------------------

MODIFY THE CODE BELOW AT YOUR OWN RISK.

The values below are used in hackjohn.py, but they are not user specific and
you do not need to change them. You should only make changes to these values if
you have a good reason (i.e., the website has changed and hackjohn is broken)
and know what you are doing.
"""

import os
import pathlib

# Write output to this file. If the generated output is identical to the
# existing output at this path, suppress notification. To disable writing any
# files, set to None.
OUTPUT_PATH = pathlib.Path("__file__").parent.joinpath("hackjohn-output.txt")

# If the Report Date is before this day, suppress notification. You probably
# do not need to change this setting unless you have disabled OUTPUT_PATH
MIN_REPORT_DATE = "2019-01-01"

# information required for solving the recaptcha
WEBSITE_URL = "https://yosemite.org/planning-your-wilderness-permit/"
REFERRER_URL = "https://yosemite.org/planning-your-wilderness-permit/"
RECAPTCHA_SITE_KEY = "6LeWjvIUAAAAAC54MkeI2YX6DGTk86-DeDHHB9-J"
RECAPTCHA_REQUEST_URL = "https://yosemite.org/wp-content/plugins/wildtrails/captcha.php"

# how many times to retry recaptcha if there is an exception, and how long between tries
MAX_RETRY_ATTEMPTS = 5
RECAPTCHA_RETRY_INTERVAL = 15  # in seconds

# override CAPTCHA_API_KEY with environment variable if set (used by CI)
CAPTCHA_API_KEY = os.environ.get("HACKJOHN_CAPTCHA_API_KEY") or CAPTCHA_API_KEY

# save cookies to this file so they can be reused if still valid
COOKIE_FILE = pathlib.Path("__file__").parent.joinpath(".cookies.pickle")

# API endpoints
JMT_REPORT_ENDPOINT = "https://yosemite.org/wp-content/plugins/wildtrails/query.php?resource=report&region=jm"
TRAILHEAD_ENDPOINT = "https://yosemite.org/wp-content/plugins/wildtrails/query.php?resource=trailheads"

# phone number for permit office (previous number was 209-372-0740)
PERMIT_OFFICE_PHONE = "209-372-0826"
PERMIT_REQUEST_FORM_URL = "https://yosemite.org/yosemite-wilderness-permit-request-form/"

# URLs for Telegram and IFTTT notifications
TELEGRAM_URL = "https://apps.muetsch.io/webhook2telegram/api/messages"
IFTTT_HOSTNAME = "https://maker.ifttt.com"

# These values are set are set using javascript on the trailhead report website
# (specifically in index.php). I don't know how to dynamically pull the values
# so I'm hard-coding the current values here. They probably won't change anyway.
# Maybe we could dynamically pull them in a future enhancement.
MAX_RESERVE_DAYS = 168
MIN_RESERVE_DAYS = 2
OPEN_DATE = "06-15"   # first calendar date JMT permits are available (MM-DD)
CLOSE_DATE = "09-30"  # last calendar date JMT permits are available (MM-DD)
