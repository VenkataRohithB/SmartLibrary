import os
from constants import SENDGRID_API
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_otp_email(to_email, otp_code):
    email_template = f"""
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Granthek OTP Verification</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            background-color: #ffffff;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        h1 {{
            color: #0055d2; /* Blue text */
        }}
        p {{
            color: #666666;
            line-height: 1.6;
        }}
        .otp-box {{
            font-size: 24px;
            font-weight: bold;
            color: #9faafc; /* Purple */
            padding: 10px;
            border: 2px dashed #FF1744;
            border-radius: 5px;
            display: inline-block;
            margin: 20px 0;
        }}
        .footer {{
            margin-top: 20px;
            text-align: center;
            font-size: 12px;
            color: #999999;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to Granthek!</h1>
        <p>Hi there,</p>
        <p>Thank you for choosing Granthek - Effortless Book Access. To continue with your verification, please use the following One-Time Password (OTP):</p>

        <div class="otp-box">{otp_code}</div>

        <p>Please enter this OTP to complete the process. This OTP is valid for the next 10 minutes.</p>
        <p>If you did not request this, you can safely ignore this email.</p>

        <p>Thanks,<br>The Granthek Team</p>

        <div class="footer">
            <p>&copy; 2024 Granthek. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
    """

    # Create the email message
    message = Mail(
        from_email='rohithboorada.dev@gmail.com',
        to_emails=to_email,
        subject="GRANTHEK Verification OTP",
        html_content=email_template
    )

    # Send the email
    try:
        sg = SendGridAPIClient(SENDGRID_API)
        response = sg.send(message)
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)
    except Exception as e:
        print(str(e))
