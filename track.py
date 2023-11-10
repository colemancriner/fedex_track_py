import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time
import config,configSand

class FedExClient:
    AUTHORIZATION_URL = 'https://apis.fedex.com/oauth/token'
    TRACKING_ENDPOINT = 'https://apis.fedex.com/track/v1/trackingnumbers'
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.expires_at = datetime.min
        self.tracking_info = None
        self.description = None
        self.type = None
        self.get_token()

    def get_token(self):
        time.sleep(1.1) # Ensures rate limits are not reached
        if self.expires_at <= datetime.now():
            client_credentials = 'client_credentials'
            token_payload = {
                "grant_type": client_credentials,
                "client_id": str(self.client_id),
                "client_secret": str(self.client_secret)
            }
            token_headers = {
                "content-type": "application/x-www-form-urlencoded"
            }

            response = requests.post(self.AUTHORIZATION_URL, data=token_payload, headers=token_headers)
            token_response = json.loads(response.content)
            self.token = token_response['access_token']
            expires_in = token_response['expires_in']
            self.expires_at = datetime.now() + timedelta(seconds=int(expires_in)) - timedelta(seconds=2) # Subtracting 2sec to ensure token is not expired

        return self.token

    def get_tracking(self, tracking_num):
        self.get_token()
        payload = {
            "trackingInfo": [
                {
                    "trackingNumberInfo": {
                        "trackingNumber": str(tracking_num)
                    }
                }
            ],
            "includeDetailedScans": True
        }
        payload = json.dumps(payload)

        headers = {
            "content-type": "application/json",
            "X-locale": "en_US",
            "Authorization": f"Bearer {self.token}"
        }

        response = requests.post(self.TRACKING_ENDPOINT, data=payload, headers=headers)
        response = json.loads(response.content)
        serviceDetail_description = response['output']['completeTrackResults'][0]['trackResults'][0]['serviceDetail']['description']
        serviceDetail_type = response['output']['completeTrackResults'][0]['trackResults'][0]['serviceDetail']['type']

        df = pd.DataFrame({'description': [serviceDetail_description],
                           'type': [serviceDetail_type]})
        time.sleep(.01)
        self.tracking_info = df
        self.description = df['description'][0]
        self.type = df['type'][0]
        return df

# Example usage
if __name__ == "__main__":
    CLIENT_ID = config.CLIENT_ID
    CLIENT_SECRET = config.CLIENT_SECRET
    tracking_num = '783216607940' # Description: FedEx Home Delivery; Type: GROUND_HOME_DELIVERY

    fedex_client = FedExClient(CLIENT_ID, CLIENT_SECRET)
    tracking = fedex_client.get_tracking(tracking_num)
    description = fedex_client.description
    tracking_type = fedex_client.type
    print("Description:", description)
    print("Type:", tracking_type)

