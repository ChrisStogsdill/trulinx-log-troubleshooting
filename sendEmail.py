import boto3

# Make sure to setup AWS credentials when using this

def sendEmail(message = "test message", subject = "test subject", emailTo = "cstogsdill@midwesthose.com", emailFrom = "chris1stogsdill@gmail.com"):
    ses_client = boto3.client("ses", region_name="us-east-1")
    CHARSET = "UTF-8"

    response = ses_client.send_email(
        Destination={
            "ToAddresses": [
                emailTo,
            ],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": CHARSET,
                    "Data": message,
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data": subject,
            },
        },
        Source= emailFrom,
    )
