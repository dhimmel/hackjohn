# Bot to monitor for southbound permit spaces on the John Muir Trail

[![Hackjohn CI](https://github.com/dhimmel/hackjohn/workflows/Hackjohn%20CI/badge.svg?branch=master)](https://github.com/dhimmel/hackjohn/actions)

This repository contains a Python script for monitoring Yosemite's [permit availability report](https://yosemite.org/planning-your-wilderness-permit/).
Vacancies in this table indicate the availability of a southbound John Muir 
Trail permit, available for immediate reservation by filling out the online 
[permit request form](https://yosemite.org/yosemite-wilderness-permit-request-form/).
This strategy enables securing a soutbound JMT permit after the lottery drawing
for a given date.

**Learn more about using hackjohn** and its history of success in the blog post
titled [**Introducing the hackjohn bot for southbound John Muir Trail permits**](https://hive.blog/@dhimmel/introducing-the-hackjohn-bot-for-southbound-john-muir-trail-permits)
and _The Mercury News_ article titled [**Here’s how to get a coveted reservation to hike the John Muir Trail**](https://www.mercurynews.com/2019/04/22/heres-how-to-get-a-reservation-to-hike-the-john-muir-trail/ "Written by Lisa M. Krieger on April 22, 2019").

## Usage

Modify [`hackjohn.py`](hackjohn.py) with the parameters of your permit search.
Add your 2Captcha API key (see the Captcha solving service section) and then 
set your tokens for Telegram, IFTTT, and/or Twilio to receive notifications 
(see the Notifications section). Then simply run the hackjohn Python script in 
the `hackjohn` appropriate environment (see Environment section) with:

```shell
python hackjohn.py
```

The script will print some progress messages and at the end it will print a
message containing available permit details. The same message will be sent via
whichever notification services you set up. An example of the report is:

```
2021-08-20:
5 permits for Happy Isles->Little Yosemite Valley
2 permits for Lyell Canyon

2021-09-03:
1 permit for Happy Isles->Little Yosemite Valley

Report last updated 2021-03-20 10:34:32 AM PDT.

Permit request form: https://yosemite.org/yosemite-wilderness-permit-request-form/
Permit office phone: 209-372-0826
```

By default, hackjohn writes the output to the file `hackjohn-output.txt` (as 
specified by the `OUTPUT_PATH` variable in `config.py`). To avoid repeated 
notification, hackjohn skips sending notifications if its output matches the 
pre-existing output.

## Captcha solving service

As of June 22, 2020, the trailhead report switched to a new website that moved
the permit report behind a Recaptcha (the "I am not a robot" thing). This made 
it more difficult for bots to access the report. 

hackjohn uses [2Captcha](https://2captcha.com) to solve the Recaptcha and get 
to the permit report. You will need to create a 2Captcha account and
upload some funds, then copy your 2Captcha API key into the `CAPTCHA_API_KEY`
variable in [`hackjohn.py`](hackjohn.py). 

This costs money, but it is very cheap (a few dollars will get you 1000 
Recaptchas). hackjohn reuses the same Recaptcha authorization as long as it is
still valid, so it only calls the 2Captcha service when necessary (currently
the authentication lasts about a day, but that is subject to change).
Realistically, it will cost you at most a couple dollars to run hackjohn 
multiple times per day for an entire year.

**Note:** There are many alternatives to 2Captcha and they all work pretty much
the same way. I didn't have any particular reason for choosing 2Captcha. Feel 
free to use a different Captcha solving service, but you will need to make
modifications to the code.

## Notifications

hackjohn supports the following services to provide notifications:

* **The Telegram messaging app.** Refer to the 
[webhook2telegram repo](https://github.com/muety/webhook2telegram) for more
details.
  1. Download the Telegram app at https://telegram.org. Mobile and desktop apps
  are available.
  2. Message "\start" to @MiddleManBot. It will send back a token.
  3. In [`hackjohn.py`](hackjohn.py), set `ENABLE_TELEGRAM` to True and set 
  `TELEGRAM_TOKEN` to the token you received in the previous step.

* **If This Then That (IFTTT).** (Thanks Markus Neuhoff for 
[contributing](https://github.com/dhimmel/hackjohn/pull/4) this feature!)
  1. Create an applet at https://ifttt.com/create. (You will also need to create
  an IFTTT account.)
  2. In the "If This" section of your applet, click "Webhooks" and then 
  "Receive a web request". Give it a name (e.g., "hackjohn"). Add this name to 
  the `IFTTT_EVENT_NAME` variable in [`hackjohn.py`](hackjohn.py).
  3. In the "Then That" section of your applet, select the type of notification
  you would like to receive. For example, "Notifications -> Send a rich 
  notification from the IFTTT app" or "Email -> Send me an email".
  4. Go to https://ifttt.com/maker_webhooks, click on documentation, and copy 
  your key at the top of the screen into the `IFTTT_KEY` variable and set
  `ENABLE_IFTTT` to True in [`hackjohn.py`](hackjohn.py).

* **SMS text messages with Twilio.**
  1. Create an account at https://www.twilio.com.
  2. In the "Project Info" section of your Twilio dashboard, copy your Account
  SID and Auth Token values into the `TWILIO_ACCOUNT_SID` and 
  `TWILIO_AUTH_TOKEN` variables in [`hackjohn.py`](hackjohn.py), respectively.
  3. Click "Get a trial phone number" in your Twilio dashboard. Twilio will
  generate a phone number for your account. Copy this phone number into the 
  `TWILIO_PHONE_NUMBER` variable in [`hackjohn.py`](hackjohn.py).
  4. Set the `TWILIO_TO_PHONE` variable to the phone number you want to send
   notifications to (i.e., your phone number) and set`ENABLE_TWILIO` to True in
   [`hackjohn.py`](hackjohn.py).
  5. **Note:** It costs a small amount of money to operate your Twilio account
  (currently $1 per month to maintain your phone number plus $0.0075 per 
  message sent). It is often possible to find promos that will add money to 
  your account. For example, there is currently a promo code for $50 in free
  credits in the "Basic Training" section in [Twilio Quest](https://www.twilio.com/quest)
  (working as of March 2021).

hackjohn can be run without enabling notifications, which is useful for 
prototyping and development, but less useful for automated monitoring.

## Environment

The recommended installation method is to create a virtual environment for just
hackjohn. This ensures installation does not modify dependencies for other 
projects. To install a [virtual environment](https://docs.python.org/3/tutorial/venv.html), 
run the following:

```shell
# Create a virtual environment in the env directory
python3 -m venv env

# Activate the virtual environment
source env/bin/activate

# Install the required dependencies into the virtual env
pip install --requirement requirements.txt

# Now you can run hackjohn
python hackjohn.py
```

## Automation

You can automate the running of `hackjohn.py` at scheduled times every day.
According to the Yosemite permit office, the trailhead quotas are often updated around 11 AM Pacific Time.

I used `cron`, which despite its awful interface got the job done.
Therefore, I added the following lines to my `crontab` configuration (replacing `ABOSOLUTE_REPO_PATH` with the absolute path to the directory containing `hackjohn.py`):

```
# hackjohn bot scheduling (configured for a system on Eastern Time)
0 13 * * * ABOSOLUTE_REPO_PATH/hackjohn.py >> ABOSOLUTE_REPO_PATH/hackjohn.log
44 13 * * * ABOSOLUTE_REPO_PATH/hackjohn.py >> ABOSOLUTE_REPO_PATH/hackjohn.log
59 13 * * * ABOSOLUTE_REPO_PATH/hackjohn.py >> ABOSOLUTE_REPO_PATH/hackjohn.log
14 14 * * * ABOSOLUTE_REPO_PATH/hackjohn.py >> ABOSOLUTE_REPO_PATH/hackjohn.log
30 14 * * * ABOSOLUTE_REPO_PATH/hackjohn.py >> ABOSOLUTE_REPO_PATH/hackjohn.log
40 14 * * * ABOSOLUTE_REPO_PATH/hackjohn.py >> ABOSOLUTE_REPO_PATH/hackjohn.log
00 15 * * * ABOSOLUTE_REPO_PATH/hackjohn.py >> ABOSOLUTE_REPO_PATH/hackjohn.log
19 15 * * * ABOSOLUTE_REPO_PATH/hackjohn.py >> ABOSOLUTE_REPO_PATH/hackjohn.log
00 19 * * * ABOSOLUTE_REPO_PATH/hackjohn.py >> ABOSOLUTE_REPO_PATH/hackjohn.log
```

Run `crontab -e` to edit your cron configuration.
In order to for the cron-scheduled script to run in the proper environment, you must add a shebang pointing to which Python to use.
For example, replace the following with the output of `which python` when you have activated the right environment:

```python
#!/home/username/path/to/hackjohn/env/bin/python
```
