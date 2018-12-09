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
