#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on Dec 8, 2016

@author: xiaopan
'''
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib

from utils.log import Log


class Mail(object):
    '''
    classdocs
    '''


    def __init__(self, from_addr, to_addrs):
        self.logger = Log().getLogger("Mail")
        self.from_addr = from_addr
        self.to_addrs = to_addrs
        
    def set_from_addr(self, from_addr):
        self.from_addr = from_addr
        
    def set_to_addrs(self, to_addrs):
        self.to_addrs = to_addrs
        
    def init_smtp(self, from_addr, to_addrs):
        self.smtp = smtplib.SMTP('mail.emea.nsn-intra.net')
        self.message = MIMEMultipart()
        self.message['From'] = from_addr
        self.message['To'] = to_addrs
        
    def close_smtp(self):
        self.smtp.close()
        
    def create(self, subject, content, attachment=None, subtype='plain'):
        self.init_smtp(self.from_addr, self.to_addrs)
        self.add_mail_subject(subject)
        if content:
            self.add_mail_content(content, subtype)
        if attachment:
            self.add_mail_attach(attachment)
        
    def send(self):
        self.logger.debug('From: ' + self.from_addr + ' To:' + self.to_addrs + ' Message:' + self.message.as_string())
        self.smtp.sendmail(self.from_addr, self.to_addrs, self.message.as_string())
        self.close_smtp()
            
    def add_mail_subject(self, subject):
        self.message['Subject'] = subject 
        
    def add_mail_content(self, content_str, subtype):
        mail_msg = MIMEText(content_str, subtype)
        self.message.attach(mail_msg)
        
    def add_mail_attach(self, attach_list):
        for filename in attach_list:
            source_file = open(filename, 'rb')
            attachment = MIMEApplication(source_file.read())
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filename))
            self.message.attach(attachment)
            self.logger.info('add %s as attachment' % filename)
        
        
