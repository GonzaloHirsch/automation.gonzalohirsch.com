# automation.gonzalohirsch.com

Repository for automation-related processes to make my life easier.

## Scrapers

Initialise the scraper env:

```
cd scrapers && virtualenv .env && source .env/bin/activate && pip install -r requirements.txt
```

### HSBC

Make sure the `.env.dev` inside the `scrapers` folder has the following:

```
HSBC_USERNAME="<HSBC_USERNAME>"
HSBC_DOWNLOAD_LOCATION="chrome_downloads"
HSBC_DOWNLOAD_PREFIX="hsbc"
```

Then you can run it with:

```
python hsbc.py
```

That will open a Chromium window, and will wait for you to fill in the `Log On Security Code`, so that it can continue. After that, it will iterate some of the accounts and try to download statements for the previous full month. Those will go into the `scrapers/<HSBC_DOWNLOAD_LOCATION>` folder, with a name based on several pieces of information from the account.

## LLM

Initialise the LLM env:

```
cd llm && virtualenv .env && source .env/bin/activate && pip install -r requirements.txt
```

Make sure the LLM library is initialised by running:

```
python -m mlx_lm generate --prompt "hello"
```

To categorise a statement, you can use the following script:

```
./scripts/categorisation.sh <path/to/source.csv> <path/to/destination.csv>
```

## Requirements

Requirements are managed within the specific folders for now. Any requirements file can be updated if you have activated the virtual environment and you run:

```
pip freeze > requirements.txt
```

# VS Code

Copy path to the Python3 bin in the .env and do the 'Select Interpreter', paste that path.
