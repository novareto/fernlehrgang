# -*- coding: utf-8 -*-

import os
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders


def send_mail(send_from, send_to, subject, text, files=[], server="localhost"):
    assert isinstance(send_to, (list, tuple, set))
    assert isinstance(files, (list, tuple, set))

    msg = MIMEMultipart()

    # headers
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = Header(subject, 'utf-8')

    # body
    txt = MIMEText(text, 'plain', 'utf-8')
    msg.attach(txt)

    for f in files:
        part = MIMEBase('application', "octet-stream")
        with open(f, 'rb') as fd:
            part.set_payload(fd.read())
        Encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()
