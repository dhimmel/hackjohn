"""
MODIFY THIS FILE AT YOUR OWN RISK.

Configuration variables for the hackjohn.py script. You should only make changes
to these values if you have a good reason and know what you are doing.
"""
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
