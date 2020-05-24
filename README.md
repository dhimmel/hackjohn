# Bot to monitor for southbound permit spaces on the John Muir Trail

This repository contains a Python script for monitoring Yosemite's [Donohue Exit Quota and Trailhead Space Available](https://www.nps.gov/yose/planyourvisit/fulltrailheads.htm) online table.
Vacancies in this table indicate the availability of a southbound John Muir Trail permit,
available for immediate reservation by calling the Yosemite Wilderness Permit Reservations at [1-209-372-0740](tel:1-209-372-0740).
This strategy enables securing a soutbound JMT permit after the lottery drawing for a given date.

**Learn more about using hackjohn** and its history of success in the blog post titled [**Introducing the hackjohn bot for southbound John Muir Trail permits**](https://hive.blog/@dhimmel/introducing-the-hackjohn-bot-for-southbound-john-muir-trail-permits) and _The Mercury News_ article titled [**Here’s how to get a coveted reservation to hike the John Muir Trail**](https://www.mercurynews.com/2019/04/22/heres-how-to-get-a-reservation-to-hike-the-john-muir-trail/ "Written by Lisa M. Krieger on April 22, 2019").

## Usage

Modify [`hackjohn.py`](hackjohn.py) with the parameters of your permit search.
To receive [Telegram](https://telegram.org/) notfications, set your `token` for the [MiddleManBot](https://github.com/n1try/telegram-middleman-bot).
Then simply run the hackjohn Python script in the `hackjohn` appropriate environment (described below) with:

```shell
python hackjohn.py
```

The script with print the table of available spaces via stdout.
An example of the output is:

```
Spaces available as of 2020-05-23:

      Date      Trailhead  Spaces
2020-09-27   Lyell Canyon       5
2020-09-28   Lyell Canyon       8
2020-09-29  Sunrise Lakes       5
2020-09-29   Lyell Canyon      15
2020-09-30   Lyell Canyon       7

According to https://www.nps.gov/yose/planyourvisit/fulltrailheads.htm
Yosemite Reservations: 209-372-0740 (Monday–Friday 9:00am–4:30pm)

output has changed: False
```

By default, Hackjohn writes the output to the file `hackjohn-output.txt` (as specified by `output_path`).
To avoid repeated notification, Hackjohn skips Telegram notification if its output matches the pre-existing output.

## Notifications

Hackjohns supports the following services to provide notifications:

1. **the [Telegram](https://telegram.org/) messaging app.**
   Configure `enable_middleman` and `token` in [`hackjohn.py`](hackjohn.py) to use this feature.

2. **If This Than That ([IFTTT](https://ifttt.com/)).**
   To enable IFTTT follow the instructions in `hackjohn.py` to create an IFTTT applet.
   Configure `enable_ifttt` and `ifttt_key` in `hackjohn.py`.
   Thanks Markus Neuhoff for [contributing](https://github.com/dhimmel/hackjohn/pull/4) this feature!

Hackjohn can be run without enabling notifications, which is usefull for prototyping and development, but less useful for automated monitoring.

## Environment

The recommend installation method is to create a virtual environment for just Hackjohn.
This ensures installation does not modify dependencies for other projects.
To install a [virtual environment](https://docs.python.org/3/tutorial/venv.html), run the following:

```shell
# Create a virtual environment in the env directory
python3 -m venv env

# Activate the virtual environment
source env/bin/activate

# Install the required dependencies into the virtual env
pip install --requirement requirements.txt

# Now you can run Hackjohn
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
