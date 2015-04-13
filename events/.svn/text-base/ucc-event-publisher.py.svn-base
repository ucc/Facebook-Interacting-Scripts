from optparse import OptionParser
import string
import readline
from dateutil.parser import *
import datetime

from datetime import timedelta
import sys, tempfile, os
from subprocess import call
from UccFacebookPoster import *
import smtplib
from email.mime.text import MIMEText
import re


def get_text_input_from_editor(instructions=""):
    """Stolen from http://stackoverflow.com/questions/6309587/call-up-an-editor-vim-from-a-python-script"""

    EDITOR = os.environ.get('EDITOR','vim') 
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tmpfile:
        tmpfile.write(instructions)
        tmpfile.flush()
        call([EDITOR, tmpfile.name])
        with open(tmpfile.name,'rb') as f:
            text = f.read()
            text = text.replace(instructions, "", 1)
            return text.strip()

def parse_timedelta(deltastring):
    """Stolen from http://blog.posativ.org/2011/parsing-human-readable-timedeltas-in-python/"""
    keys = ["weeks", "days", "hours", "minutes"]
    regex = "".join(["((?P<%s>\d+)%s ?)?" % (k, k[0]) for k in keys])
    kwargs = {}
    for k,v in re.match(regex, deltastring).groupdict(default="0").items():
        kwargs[k] = int(v)
    return timedelta(**kwargs)


class EventDetails:

    def __str__(self):
        return '''Event Details:
         Name: %(name)s
         Start Time: %(start)s
         End Time: %(end)s
         Location: %(loc)s 
         Description:
         %(desc)s
         ''' % {'name':self.name, 
                           'start':str(self.startdatetime),
                           'end': str(self.enddatetime),
                           'desc': self.description,
                           'loc': self.location
                           }


    def timing_details(self):
        startdate = self.startdatetime.date()
        enddate = self.enddatetime.date()
        def format_time(time):
            return time.strftime("%-I:%M%p")
        def format_date(date):
            return date.strftime("%A, %-d/%m/%Y")

        if (startdate==enddate):
            starttime = self.startdatetime.time()
            endtime = self.enddatetime.time()
            return "Date: %(date)s\nTime: %(start)s-%(end)s" % \
                        {'date': format_date(startdate),
                         'start': format_time(starttime),
                         'end': format_time(endtime)}
        else:
            def formatdatetime(dt):
                return "%(date)s - %(time)s" % \
                     {'date' : format_date(dt.date()),
                      'time' : format_time(dt.time())}

            return "Start: %(start)s\nEnd: %(end)s" % \
                      {'start' : formatdatetime(self.startdatetime),
                       'end' : formatdatetime(self.enddatetime)}

    def details_for_email(self): 
        return self.timing_details() + '\nLocation: ' + self.location


def get_parsed_input(question, parse):
    readinput = raw_input(question)
    try:
        return parse(readinput)
    except (ValueError, re.error)  as e:
        print("Error: %s" % str(e))
        return get_parsed_input(question, parse)

def print_header():
    print("Welcome to the UCC Event Publishing System,\n made by [*OX] in 2012")
    print("-"*71)
    print("Note: The parser for datetimes is python-dateutil, and is really smart,")
    print("      so don't over think it.")
    print("-"*71)

def get_event_details():
    event_details = EventDetails()
    event_details.name= raw_input("Event Name? ")
    event_details.startdatetime = get_parsed_input(
        "Please enter start datetime, day first: \n",
        lambda imp: parse(imp, dayfirst=True))

    def parse_end_time(endTimeInput):
        if (endTimeInput==""): return None
        try:
            delta = parse_timedelta (endTimeInput)
            enddatetime = event_details.startdatetime + delta    
    
        except ValueError, re.error: 
            enddatetime = parse(endTimeInput,
                                dayfirst=True, 
                                default=event_details.startdatetime)
        return enddatetime

    event_details.enddatetime = get_parsed_input(
'''Please enter end time(/datetime), missing datetime fields default to those
from start or duration (eg "1d 2h 3m " for 1 day 2 hours and 3 minutes),
or You many leave it blank to not specify.\n''',
        parse_end_time)
    event_details.location = raw_input("Location: ")
    event_details.description = get_text_input_from_editor("#Enter the event's description, and save and exit, this line will be deleted")
    return event_details

def post_to_facebook(event_details):
    Poster().CreateEvent( name = event_details.name,
                 description = event_details.description,
                 startdatetime = event_details.startdatetime,
                 enddatetime = event_details.enddatetime,
                 location = event_details.location )


def send_email(event_details):
    """Stolen from http://www.yak.net/fqa/84.html"""
    SENDMAIL = "/usr/sbin/sendmail" # sendmail location
    p=os.popen("%s -t" % SENDMAIL, "w")
    p.write("To: %s\n" % 'oxinabox@ucc.asn.au')
    p.write("Subject: %s" % event_details.name)
    p.write("\n")
    p.write("Hi all,\n UCC has an event comming up: " + event_details.name)
    p.write("\n\n")
    p.write(event_details.details_for_email())
    p.write("\n\n" + event_details.description)
    p.write("\n\n Hope to see you there \n\n")
    p.write("(This email was sent using the UCC event publication system)")
    exitStatus = p.close()
    if (exitStatus):
        print("Email failed: Sendmail exit code %s" % exitStatus)
    else:
        print("email sent") 
       


print_header()
event_details = get_event_details()
print(str(event_details))
try:
    post_to_facebook(event_details)
except Exception, e:
    "Post to facebook failed"
    print >> sys.stderr, e
try:
    send_email(event_details)
except Exception, e:
    "Send email failed"
    print >> sys.stderr, e


 
