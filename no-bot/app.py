import os
import requests
import logging
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request

# Initialize logging (helps debug if something goes wrong in the cloud)
logging.basicConfig(level=logging.INFO)

# 1. Initialize the Slack App
# These fetch your secret keys from the cloud server's settings
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# 2. Define the command handler
@app.command("/no")
def handle_no_command(ack, respond):
    # Acknowledge the command immediately (required by Slack within 3 seconds)
    ack()
    
    try:
        # Fetch the excuse from the "No as a Service" API
        response = requests.get("https://naas.isalman.dev/no")
        
        if response.status_code == 200:
            data = response.json()
            # Extract the "reason" from the API response
            answer = data.get("reason", "No.")
            say(answer)
        else:
            say(f"Oops, I couldn't find a 'no' right now. (API Status: {response.status_code})")
            
    except Exception as e:
        # Log the error to the console/server logs
        print(f"Error fetching data: {e}")
        say("Something went wrong while trying to say no.")

# 3. Setup Flask to listen for web requests
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

# This route handles the incoming requests from Slack
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

# This block allows you to run it locally if needed
if __name__ == "__main__":

    flask_app.run(port=3000)
