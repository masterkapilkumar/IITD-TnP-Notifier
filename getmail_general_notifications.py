from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import traceback
import argparse
import requests
import smtplib
import json
import time
import sys
# import socks
import socket

class TnP_Notifier:
    
    def __init__(self, outgoing_server, outgoing_port, sender_email, sender_password, recipient_email_list, check_interval, notifications_url, notifications_history_file, proxy_url=None, proxy_port=None, owner_name="Kapil", owner_email="masterkapilkumar@gmail.com", notifications_type="Placement"):
        self.outgoing_server = outgoing_server
        self.outgoing_port = outgoing_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email_list  = recipient_email_list
        if(recipient_email_list==['']):
            self.recipient_email_list  = None
        self.check_interval = check_interval
        self.notifications_url = notifications_url
        self.notifications_history_file = notifications_history_file
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        self.contents = {"general": ["info"],
                        "visit": ["name", "time", "venue", "info"],
                        "shortlist": ["link", "name", "info"],
                        "file": ["link", "name", "info"]}
        self.proxy_url = proxy_url
        self.proxy_port = proxy_port
        self.owner_name = owner_name
        self.owner_email = owner_email
        self.notifications_type = notifications_type.capitalize()
        self._socket = socket.socket

    def find_json_object(self, data, it):
        for item in data:
            if(item["category"] == it["category"]):
                flag = True
                for attr in self.contents[it["category"]]:
                    if(item[attr] != it[attr]):
                        flag = False
                        break
                if(flag):
                    return True
        return False
        
    def json_diff(self, data1, data2):
        diff = []
        for item in data1:
            flag = self.find_json_object(data2, item)
            if not flag:
                diff.append(item)
            
        return diff
        
    def check_new_notifications(self, old_file):
        response = requests.get(self.notifications_url, headers=self.headers, verify=False)
        data = response.json()
        
        try:
            fin = open(old_file, 'r')
            old_data = json.loads(fin.read())
            fin.close()
        except IOError:
            print("No history found...")
            old_data = []
        
        diff = self.json_diff(data, old_data)
        
        if(diff == []):
            return (data, None)
        else:
            return (data, diff)
        
    
    def build_email_body(self, data):
        body = '<center><table width="770"><tr><td><br>'
        general = ""
        visit = ""
        shortlist = ""
        file = ""
        general += '<div align="center"><h2>General Notifications</h2><br>'
        general += '<table align="center" border="2" cellpadding="2" cellspacing="2" width="100%"><tr><th><font face="Arial, Helvetica, sans-serif">Subject</font></th></tr>'
        visit += '<div align="center"><h2>Company Visit Schedule</h2><br>'
        visit += '<table align="center" border="2" cellpadding="2" cellspacing="2" width="100%"><tr> \
                  <th><font face="Arial, Helvetica, sans-serif">Company Name</font></th> \
                  <th><font face="Arial, Helvetica, sans-serif">Date and Time</font></th> \
                  <th><font face="Arial, Helvetica, sans-serif">Venue</font></th> \
                  <th><font face="Arial, Helvetica, sans-serif">Info</font></th> \
                  </tr>'
        shortlist += '<div align="center"><h2>Short List</h2><br>'
        shortlist += '<table align="center" border="2" cellpadding="2" cellspacing="2" width="100%"><tr> \
                  <th><font face="Arial, Helvetica, sans-serif">Link</font></th> \
                  <th><font face="Arial, Helvetica, sans-serif">Company Name</font></th> \
                  <th><font face="Arial, Helvetica, sans-serif">Info</font></th> \
                  </tr>'
        file += '<div align="center"><h2>Downloads</h2><br>'
        file += '<table align="center" border="2" cellpadding="2" cellspacing="2" width="100%"><tr> \
                  <th><font face="Arial, Helvetica, sans-serif">Link</font></th> \
                  <th><font face="Arial, Helvetica, sans-serif">Name</font></th> \
                  <th><font face="Arial, Helvetica, sans-serif">Info</font></th> \
                  </tr>'
        
        item_body = '<td><center><font face="Arial, Helvetica, sans-serif"> <b>{}</b></font> </center></td>'
        for item in data:
            if(item['category'] == "general"):
                general += '<tr>'
                general += item_body.format('<br />'.join(item['info'].split('\n')))
                general += '</tr>'
            elif(item['category'] == "visit"):
                visit += '<tr>'
                visit += item_body.format(item['name'])
                visit += item_body.format(item['time'])
                visit += item_body.format(item['venue'])
                visit += item_body.format('<br />'.join(item['info'].split('\n')))
                visit += '</tr>'
            elif(item['category'] == "shortlist"):
                shortlist += '<tr>'
                shortlist += item_body.format(item['link'])
                shortlist += item_body.format(item['name'])
                shortlist += item_body.format('<br />'.join(item['info'].split('\n')))
                shortlist += '</tr>'
            elif(item['category'] == "file"):
                file += '<tr>'
                file += item_body.format(item['link'])
                file += item_body.format(item['name'])
                file += item_body.format('<br />'.join(item['info'].split('\n')))
                file += '</tr>'
        
        general += '</table><br/><br/><br/><br/><br/></div>'
        visit += '</table><br/><br/><br/><br/><br/></div>'
        shortlist += '</table><br/><br/><br/><br/><br/></div>'
        file += '</table><br/><br/><br/><br/><br/></div>'
        
        if(general.count('<tr>') > 1):
            body += general
        if(visit.count('<tr>') > 1):
            body += visit
        if(shortlist.count('<tr>') > 1):
            body += shortlist
        if(file.count('<tr>') > 1):
            body += file
        body += '</td></tr></table></center>'
        
        return body
    
    def dump_json(self, data, file_name):
        str_data =  json.dumps(data, indent=4)
        open(file_name ,'w').write(str_data)
    
    def send_email(self, to_addrs, email_body, subject="", bcc=None):
        
        print("Sending new notifications...")
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = 'whomsoever-it-may-concern'

        msg.attach(MIMEText(email_body, 'html'))

        if(self.proxy_url and self.proxy_port):
            socks.setdefaultproxy(socks.HTTP, proxy_url, proxy_port)
            socks.wrapmodule(smtplib)

        server = smtplib.SMTP(self.outgoing_server, self.outgoing_port)
        server.ehlo()
        server.starttls()
        server.login(self.sender_email, self.sender_password)
        if(bcc!=None and len(bcc)>0 and '' not in bcc):
            server.sendmail(self.sender_email, bcc, msg.as_string())

        #send mail to owner
        if(bcc!=None and len(bcc)>0 and '' not in bcc):
            msg['To'] = ','.join(bcc)
        server.sendmail(self.sender_email, to_addrs, msg.as_string())

        server.quit()
        print("Email sent successfully! Hurray!\n\n")

        if(self.proxy_url and self.proxy_port):
            socket.socket = self._socket
    
    def run(self):
        
        (data, diff) = self.check_new_notifications(self.notifications_history_file)
        if(diff):
            print("New notifications")
            message = self.build_email_body(diff)
            self.send_email([self.owner_email], message, "T&P %s Notification" %(self.notifications_type), bcc=self.recipient_email_list)
            self.dump_json(data, self.notifications_history_file)
            
        else:
            print("No new notifications")

if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="path of JSON file having configuration data")
    parser.add_argument('-t', '--time', help="Time (in seconds) gap for checking new notifications", default="1000", type=int)
    parser.add_argument('-T', '--type', help="Notifications type - Training/Placement", choices=["placement", "training"], default="placement")
    
    args = parser.parse_args()
    
    notifications_type = args.type.lower()
    
    try:
        fin = open(args.config_file, 'r')
        config_data = json.loads(fin.read().strip())
        fin.close()
    except Exception:
        print("Error reading configuration data:\n")
        traceback.print_exc()
        sys.exit(1)
    
    try:
        outgoing_server = config_data["outgoing_server"]
        outgoing_port = config_data["outgoing_port"]
        sender_email = config_data["sender_email"]
        sender_password = config_data["sender_password"]
#TODO - check whether all the email ids in the list are valid or not
        recipient_email_list = config_data["recipient_email_list"]
        recipient_email_list = list(map(lambda s: s.strip(), recipient_email_list.split(",")))
        notifications_url = "https://tnp.iitd.ac.in/api/notify?type="+notifications_type
        history_file = config_data["history_file"]
        proxy_url = config_data.get("proxy_url", None)
        proxy_port = config_data.get("proxy_port", None)
        owner_name = config_data.get("owner_name", "Kapil")
        owner_email = config_data.get("owner_email", "masterkapilkumar@gmail.com")
        check_interval = args.time
    except KeyError:
        print("Missing configuration data:\n")
        traceback.print_exc()
        sys.exit(1)
    
    tnp_notifier = TnP_Notifier(outgoing_server, outgoing_port, sender_email, sender_password, recipient_email_list, check_interval, notifications_url, history_file, proxy_url, proxy_port, owner_name, owner_email, notifications_type)
    time_since_last_sent_error = 0
    while(True):
        try:
            tnp_notifier.run()
            time_since_last_sent_error = 0
        except Exception:
            #handle any exception
            traceback.print_exc()
            print("\n")
            
            #Send email to owner in case of any error in interval of 3 hours
            if(time_since_last_sent_error > 10800):
                time_since_last_sent_error = 0
            if(time_since_last_sent_error == 0):
                print("Informing %s..." %(owner_name))
                error_msg = "<b>TnpNotifier encountered an error, please debug it ASAP:</b><br><br><i>%s</i>" %(str(sys.exc_info()))
                tnp_notifier.send_email([owner_email], error_msg, subject="TnP Notifier is down...")
                print("Email sent to %s..." %owner_name)
            time_since_last_sent_error += check_interval
        print("Pausing execution for %s seconds\n" %check_interval)
        time.sleep(check_interval)