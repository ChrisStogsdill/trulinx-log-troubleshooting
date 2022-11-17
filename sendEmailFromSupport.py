import json
import os
import msal
import requests

def sendEmail(message = "test message", subject = "test subject", emailTo = "cstogsdill@midwesthose.com", emailFrom = "mwhsupport@midwesthose.com"):

    # get config file from the ignored directory
    script_dir = os.path.dirname(__file__)
    relativeConfigFilePath = "ignored/sendEmailConfig.json"
    fullConfigPath = os.path.join(script_dir, relativeConfigFilePath)

    config = json.load(open(fullConfigPath))

    # Create a preferably long-lived app instance that maintains a token cache.
    app = msal.ConfidentialClientApplication(
        config["client_id"], authority=config["authority"],
        client_credential=config["secret"]
        )

    scopes = ["https://graph.microsoft.com/.default"]

    result = None
    result = app.acquire_token_silent(scopes, account=None)

    if not result:
        print(
            "No suitable token exists in cache. Let's get a new one from Azure Active Directory.")
        result = app.acquire_token_for_client(scopes=scopes)

    # if "access_token" in result:
    #     print("Access token is " + result["access_token"])


    if "access_token" in result:
        userId = emailFrom
        endpoint = f'https://graph.microsoft.com/v1.0/users/{userId}/sendMail'
        toUserEmail = emailTo
        email_msg = {'Message': {'Subject': subject,
                                'Body': {'ContentType': 'Text', 'Content': message},
                                'ToRecipients': [{'EmailAddress': {'Address': toUserEmail}}]
                                },
                    'SaveToSentItems': 'true'}
        r = requests.post(endpoint,
                        headers={'Authorization': 'Bearer ' + result['access_token']}, json=email_msg)
        if r.ok:
            print('Send Email script - Sent email successfully')
        else:
            print(r.json())
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))