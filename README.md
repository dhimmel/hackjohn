# Bot to monitor for southbound permit spaces on the John Muir Trail



## Usage

Modify [`hackjohn.py`](hackjohn.py) with the parameters of your permit search.
To receive [Telegram](https://telegram.org/) notfications, set your `token` for the [MiddleManBot](https://github.com/n1try/telegram-middleman-bot).
Then simply run the hackjohn Python script in the `hackjohn` conda environment (described below) with:

```
python hackjohn.py
```

The script with print the table of available spaces via stdout.

## Environment

This repository uses [conda](http://conda.pydata.org/docs/) to manage its environment as specified in [`environment.yml`](environment.yml).
Install the environment with:

```sh
conda env create --file environment.yml
```

Then use `conda activate hackjohn` and `conda deactivate` to activate or deactivate the environment.

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
