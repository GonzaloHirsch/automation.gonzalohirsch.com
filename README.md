# automation.gonzalohirsch.com

Repository for automation-related processes to make my life easier.

## Scrapers

Initialise the scraper env:

```
cd scrapers && virtualenv .env && source .env/bin/activate
```

## HSBC

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

# VS Code

Copy path to the Python3 bin in the .env and do the 'Select Interpreter', paste that path.
