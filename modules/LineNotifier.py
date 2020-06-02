import requests
import traceback
from pathlib import Path

def SendNotifyMessage(token, msg, imageFilePath=None):
    try:
        NotifiyApiUrl = "https://notify-api.line.me/api/notify"

        headers = {
          "Authorization": "Bearer " + token
          # "Content-Type" : "application/x-www-form-urlencoded"
        }
        payload = {'message': msg}

        if imageFilePath:
            with open(imageFilePath, 'rb') as f:
                files = {'imageFile': f}
                r = requests.post(NotifiyApiUrl, headers = headers, params = payload, files = files)
                print(r)
                return r.status_code
        else:
            r = requests.post(NotifiyApiUrl, headers = headers, params = payload)
            print(r)
            return r.status_code
    except Exception as e:
        print(traceback.format_exc())
