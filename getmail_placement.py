from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
import jsondiff
import smtplib
import json
import time
import sys

class TnP_Notifier:
    
    def __init__(self, outgoing_server, outgoing_port, sender_email, sender_password, recipient_email_list, check_interval, notifications_url, notifications_history_file):
        self.outgoing_server = outgoing_server
        self.outgoing_port = outgoing_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email_list  = recipient_email_list
        self.check_interval = check_interval
        self.notifications_url = notifications_url
        self.notifications_history_file = notifications_history_file
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        self.contents = {"general": ["info"],
                        "visit": ["name", "time", "venue", "info"],
                        "shortlist": ["link", "name", "info"],
                        "file": ["link", "name", "info"]}
    
    
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
            if(item["category"] == "file"):
                flag = self.find_json_object(data2, item)
                if not flag:
                    diff.append(item)
        return diff
        
    def check_new_notifications(self, old_file):
        response = requests.get(self.notifications_url, headers=self.headers, verify=False)
        data = json.loads(response.content)
        
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
        
    #TODO
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
                general += item_body.format(item['info'])
                general += '</tr>'
            elif(item['category'] == "visit"):
                visit += '<tr>'
                visit += item_body.format(item['name'])
                visit += item_body.format(item['time'])
                visit += item_body.format(item['venue'])
                visit += item_body.format(item['info'])
                visit += '</tr>'
            elif(item['category'] == "shortlist"):
                shortlist += '<tr>'
                shortlist += item_body.format(item['link'])
                shortlist += item_body.format(item['name'])
                shortlist += item_body.format(item['info'])
                shortlist += '</tr>'
            elif(item['category'] == "file"):
                file += '<tr>'
                file += item_body.format(item['link'])
                file += item_body.format(item['name'])
                file += item_body.format(item['info'])
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
    
    def send_email(self, to_addrs, email_body, subject):
        
        print("Sending new notifications...")
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = ','.join(to_addrs)
        
        msg.attach(MIMEText(email_body, 'html'))
        
        server = smtplib.SMTP(self.outgoing_server, self.outgoing_port)
        server.ehlo()
        server.starttls()
        server.login(self.sender_email, self.sender_password)
        server.sendmail(self.sender_email, ','.join(to_addrs), msg.as_string())
        server.quit()
        print("Email sent successfully! Hurray!\n\n")
    
    def run(self):
        
        (data, diff) = self.check_new_notifications(self.notifications_history_file)
        if(diff):
            print("New notifications")
            message = self.build_email_body(diff)
            self.send_email(self.recipient_email_list, message, "T&P Placement Notification")
            self.dump_json(data, self.notifications_history_file)
            
        else:
            print("No new notifications")

if __name__=='__main__':

    outgoing_server = "smtp.googlemail.com"
    outgoing_port = 587
    sender_email = "tnpnotifier@gmail.com"
    sender_password = "tnpnotify.exe"
    recipient_email_list  = ['masterkapilkumar@gmail.com']
    check_interval = 300    #in seconds
    notifications_url = "https://tnp.iitd.ac.in/api/notify?type=placement"
    notifications_history_file = "notifications_history.json"
    
    tnp_notifier = TnP_Notifier(outgoing_server, outgoing_port, sender_email, sender_password, recipient_email_list, check_interval, notifications_url, notifications_history_file)
    time_since_last_sent_error = 0
    while(True):
        try:
            tnp_notifier.run()
            time_since_last_sent_error = 0
        except KeyboardInterrupt:
            sys.exit(1)
        except:
            #handle any exception
            print("Error: " + str(sys.exc_info()))
            print("\n")
            #Send email to owner in case of any error in interval of 6 hours
            if(time_since_last_sent_error > 21600):
                time_since_last_sent_error = 0
            if(time_since_last_sent_error == 0):
                print("Informing Kapil...")
                error_msg = "<b>TnpNotifier encountered an error, please correct it ASAP:</b><br><br>"
                error_msg += "<i>"+str(sys.exc_info())+"</i>"
                tnp_notifier.send_email(["masterkapilkumar@gmail.com"], error_msg, "TnP Notifier is down...")
                print("Email sent to Kapil...")
            time_since_last_sent_error += check_interval
        print("Pausing execution for %s seconds\n" %check_interval)
        time.sleep(check_interval)