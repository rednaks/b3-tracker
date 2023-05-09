# Description
B3-Tracker, is a tool to track your B3(Bulletin N°3) requests from Tunisian Ministy of the interior portal. On discord https://b3.interieur.gov.tn/demande

# Installing dependencies
```
git clone https://github.com/rednaks/b3-tracker.git
cd b3-tracker
poetry install
cp config.json.example config.json
```

# Setup
After filling the form and paying, you will recieve a tracking id so you can track your request using the form. instead you can just edit `config.json` file to provide your identity number + the tracking number  and the discord channel webhook url.


## Enabling discord webhook
To enable a Discord webhook, you can follow these steps:

1. Open Discord and navigate to the server you want to enable the webhook on.

2. Click on the server settings menu (the gear icon next to the server name) and select "Integrations."

3. Click the "Create Webhook" button, give your webhook a name, and choose the channel you want the webhook to post to.

4. Click "Copy Webhook URL" to copy the webhook URL to your clipboard.

5. Paste the webhook URL into the application or service you want to use the webhook with. The webhook will now be enabled, and any new events or updates will be posted to the Discord channel you selected.


## Automation
You can use a cron to run the script periodically.
Make sure you run the script with `poetry run python ./main.py`
