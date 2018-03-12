"""
Helper library for sending emails. It uses standard Python library class :py:class:`email` to send the email.
"""

# Copyright (C) 2017 Skylark Drones

import logging
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger('Folder-Monitor')


def send_email(recipients, subject, description, username='dmcskylark@gmail.com', password='skylarkdrones',
               attachments=None):
    """
    Function to send email (via Gmail) using the SMTP protocol. It takes in all the arguments such
    as from email credentials, file attachments, subject and body to create the email.

    :param str username: email address of sender
    :param str password: password of email address of sender
    :param list recipients: recipient(s) to whom the email has to be sent
    :param str subject: one line summary of email
    :param str description: email body
    :param list attachments: file attachments

    :exception: If unable to open any of the attachments or unable to send the email for any reason
    """
    # Create the enclosing (outer) message
    outer_msg = MIMEMultipart()
    outer_msg['Subject'] = subject
    outer_msg['To'] = ', '.join(recipients)
    outer_msg['From'] = username
    outer_msg.attach(MIMEText(description))
    outer_msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    # Add the attachments to the message
    if attachments is not None:
        for file in attachments:
            try:
                with open(file, 'rb') as fp:
                    msg = MIMEBase('application', "octet-stream")
                    msg.set_payload(fp.read())
                encoders.encode_base64(msg)
                msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
                outer_msg.attach(msg)
            except:
                logger.error("Unable to open one of the attachments!", exc_info=True)

    composed = outer_msg.as_string()

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(username, password)
            s.sendmail(username, recipients, composed)
            s.close()
        logger.info("Email sent!")
        is_email_sent = True
    except:
        logger.error("Unable to send the email!", exc_info=True)
        is_email_sent = False

    return is_email_sent
