# -*- coding: utf-8 -*-

import os
import grok
import zope.sendmail
import grok
import zope.component
import smtplib
import zope.sendmail
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
from email.header import Header
from zope.sendmail.mailer import SMTPMailer

queue_path = "/Users/ck/work/bghw/fernlehrgang/var/mq"

mailer_object = SMTPMailer('localhost', 25, force_tls=False)


def mailer():
    return mailer_object


def delivery():
    return zope.sendmail.delivery.QueuedMailDelivery(queue_path)


def start_processor_thread():
    from zope.sendmail.queue import QueueProcessorThread
    thread = QueueProcessorThread()
    thread.setMailer(mailer_object)
    thread.setQueuePath(queue_path)
    thread.start()




def send_mail(send_from, send_to, subject, text, files=[], server="mail.bghw.de"):
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

    mailer = zope.component.getUtility(
        zope.sendmail.interfaces.IMailDelivery,
        name=u'flg.maildelivery'
        )
    mailer.send(send_from, send_to, msg.as_string())


grok.global_utility(
    mailer,
    provides=zope.sendmail.interfaces.IMailer,
    name='flg.smtpmailer')
grok.global_utility(
    delivery,
    zope.sendmail.interfaces.IMailDelivery,
    name='flg.maildelivery')
#start_processor_thread()
