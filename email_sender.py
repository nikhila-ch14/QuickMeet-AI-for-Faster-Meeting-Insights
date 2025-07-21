# quickmeet-backend/email_sender.py

import boto3
import os
import logging
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
SOURCE_EMAIL = os.getenv("SOURCE_EMAIL")  # Your verified sender email

if not SOURCE_EMAIL:
    logger.error("SOURCE_EMAIL is not set. Please verify your .env file.")

# Create an SES client
ses_client = boto3.client("ses", region_name=AWS_REGION)


def send_meeting_email(to_addresses, subject, summary_text, action_items_text):
    """
    Sends an email using AWS SES with both plain text and HTML content.
    The HTML content includes the meeting summary and action items, with checkboxes next to each action item.

    Note: SES in sandbox mode requires that both SOURCE_EMAIL and each recipient
    address be verified. Check AWS SES console for your sandbox status.
    """
    # Fallback to empty strings
    summary_text = summary_text or ""
    action_items_text = action_items_text or ""

    # Log inputs
    logger.info(f"Sending email from {SOURCE_EMAIL} to {to_addresses}")
    logger.debug(f"Subject: {subject}")
    logger.debug(f"Summary Text: {summary_text}")
    logger.debug(f"Action Items Text: {action_items_text}")

    # Plain text version of the email
    plain_body = f"Meeting Summary:\n{summary_text}\n\nAction Items:\n{action_items_text}"

    # Convert action_items_text (newline-separated) into HTML with checkboxes
    action_items_html = ""
    for item in action_items_text.splitlines():
        if item.strip():
            action_items_html += f'<label><input type="checkbox" disabled> {item}</label><br>'

    if not action_items_html:
        action_items_html = "<p>No action items.</p>"

    # HTML version of the email
    html_body = f"""
    <html>
      <body>
        <h2>Meeting Summary</h2>
        <p>{summary_text}</p>
        <h2>Action Items</h2>
        {action_items_html}
      </body>
    </html>
    """

    try:
        response = ses_client.send_email(
            Source=SOURCE_EMAIL,
            Destination={'ToAddresses': to_addresses},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': plain_body, 'Charset': 'UTF-8'},
                    'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                }
            }
        )
        message_id = response.get('MessageId')
        logger.info(f"Email sent! Message ID: {message_id}")
        return response

    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to send email: {e}")
        # Re-raise or return a structured error
        raise
