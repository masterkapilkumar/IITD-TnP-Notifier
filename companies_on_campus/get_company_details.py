from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from matplotlib import pyplot as plt
from bs4 import BeautifulSoup
from cairosvg import svg2png
from datetime import datetime
import numpy as np

import traceback
import hashlib
import argparse
import requests
import smtplib
import json
import time
import sys
import socks
import socket

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

sys.path.append('./libsvm/python')
from svmutil import svm_load_model, svm_predict

class User:
    def __init__(self, entry_number="", full_name="", eligible=False, blocked=False, selected=0, department='', course='', accepted=False, cv_verified=False, application_limit=0, contact='', token=''):
        self.entry_number = entry_number
        self.full_name = full_name
        self.eligible = eligible
        self.blocked = blocked
        self.selected = selected
        self.department = department
        self.course = course
        self.accepted = accepted
        self.cv_verified = cv_verified
        self.application_limit = application_limit
        self.contact = contact
        self.token = token

class TnP_Company_Notifier:
    
    def __init__(self, outgoing_server, outgoing_port, sender_email, sender_password, recipient_email_list, check_interval, login_url, captcha_url, companies_url, company_history_file, proxy_url=None, proxy_port=None, tnp_username='abc', tnp_password='123'):
        self.outgoing_server = outgoing_server
        self.outgoing_port = outgoing_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email_list  = recipient_email_list
        self.check_interval = check_interval
        self.login_url = login_url
        self.captcha_url = captcha_url
        self.companies_url = companies_url
        self.tnp_username = tnp_username
        self.tnp_password = tnp_password
        self.company_history_file = company_history_file
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        self.contents = {"companies": ["profile", "profile_code", "type", "name", "application_deadline", "ppt_date", "ppt_applied"]}
        self.type_mapping = {"tech": "Core (Technical)", "finance": "Finance", "research":"Teaching & Research", "other":"Other", "it": "Information Technology", "consult":"Consulting", "analytics":"Analytics"}
        self.proxy_url = proxy_url
        self.proxy_port = proxy_port
        # self._socket = socket.socket

    def get_json_response(self, url, headers=None, verify=False, type='GET'):
        if(not headers):
            headers = self.headers
        if(type=='GET'):
            response = requests.get(url, headers=headers, verify=verify)
            data = response.json()
            return data, response.status_code
    
    def find_json_object(self, data, it):
        for item in data:
            flag = True
            for attr in self.contents["companies"]:
                if (attr not in item and attr not in it) or attr=="ppt_applied":
                    continue
                elif ((attr not in item) or (attr not in it)):
                    flag = False
                    break
                elif(item[attr] != it[attr]):
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
        self.headers["Authorization"] = "Bearer " + self.user.token
        data, _ = self.get_json_response(self.companies_url, headers=self.headers)
        # print(r)
        
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
        
    def get_pretty_date(self, datestr, format):
        d = datetime.strptime(datestr,format)
        return d.strftime("%a, %b %d, %I:%M %p")
    
    def build_email_body(self, data):
        
        body = '<center><table width="870"><tr><td><br>'
        companies = ""
        
        companies += '<div align="center"><h2>Companies on Campus</h2><br>'
        companies += '<table align="center" border="2" cellpadding="2" cellspacing="2" width="100%"><tr> \
                  <th><font face="Arial, Helvetica, sans-serif"><h3>Company Name</h3></font></th> \
                  <th><font face="Arial, Helvetica, sans-serif"><h3>Profile</font></h3></th> \
                  <th><font face="Arial, Helvetica, sans-serif"><h3>Type</font></h3></th> \
                  <th><font face="Arial, Helvetica, sans-serif"><h3>Deadlines</h3></font></th> \
                  </tr>'
        
        item_body = '<td><center><font face="Arial, Helvetica, sans-serif"> <b>{}</b></font> </center></td>'
        dateformat="%Y-%m-%dT%H:%M"
        for item in data:
            
            companies += '<tr>'
            companies += item_body.format('<a href="https://tnp.iitd.ac.in/portal/view-jnf?code='+item['profile_code']+'">'+item['name']+'</a>')
            companies += item_body.format(item['profile'])
            companies += item_body.format(self.type_mapping.get(item['type'], "Type not registered in TnpNotifier"))
            if('application_deadline' in item and 'ppt_date' in item):
                companies += item_body.format('<font color="red">'+"Apply: " + self.get_pretty_date(item['application_deadline'], dateformat) + "<br>" + "PPT: " + self.get_pretty_date(item['ppt_date'], dateformat)+ "</font>")
            elif('application_deadline' in item):
                companies += item_body.format('<font color="red">'+"Apply: " + self.get_pretty_date(item['application_deadline'], dateformat)+ "</font>")
            elif('ppt_date' in item):
                companies += item_body.format('<font color="red">'+"PPT: " + self.get_pretty_date(item['ppt_date'], dateformat)+ "</font>")
            else:
                companies += item_body.format('---')
                
            companies += '</tr>'
        
        companies += '</table><br/><br/><br/><br/><br/></div>'
        
        if(companies.count('<tr>') > 1):
            body += companies
        body += '</td></tr></table></center>'
        
        return body
    
    def dump_json(self, data, file_name):
        str_data =  json.dumps(data, indent=4)
        open(file_name ,'w').write(str_data)
    
    def send_email(self, to_addrs, email_body, subject, bcc=None):
        
        print("Sending email...")
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        # msg['To'] = ','.join(to_addrs)
        msg['To'] = 'whomsoever-it-may-concern'
        # if(bcc):
            # to_addrs += bcc

        msg.attach(MIMEText(email_body, 'html'))

        if(self.proxy_url and self.proxy_port):
            socks.setdefaultproxy(socks.HTTP, proxy_url, proxy_port)
            socks.wrapmodule(smtplib)

        server = smtplib.SMTP(self.outgoing_server, self.outgoing_port)
        server.ehlo()
        server.starttls()
        server.login(self.sender_email, self.sender_password)
        if(bcc!=None and len(bcc)>0):
            server.sendmail(self.sender_email, bcc, msg.as_string())

        #send mail to owner
        if(bcc!=None and len(bcc)>0):
            msg['To'] = ','.join(bcc)
        server.sendmail(self.sender_email, to_addrs, msg.as_string())

        server.quit()
        print("Email sent successfully! Hurray!\n\n")

        if(self.proxy_url and self.proxy_port):
            socket.socket = self._socket
    
    def split_chars(self,data):
        soup = BeautifulSoup(data, 'html.parser')
        paths=[]
        svgs=[]
        for i in range(6):
            a=soup.find('path').extract()
            if(not a.get('fill')=='none'):
                paths.append(a)
        for path in paths:
            outer_tag = BeautifulSoup(str(soup), 'html.parser').find('svg').extract()
            outer_tag.insert(1,path)
            svgs.append(str(outer_tag))
        svgs.sort(key=lambda s:float(s.split(" ")[4][4:]))
        return svgs
    
    def read_img(self, name):
        return plt.imread(name)
    
    def save_to_png(self, data, name):
        svg2png(bytestring=data,write_to=name)
    
    def process_captcha_data(self):
        captcha_json, _ = self.get_json_response(self.captcha_url)
        captcha = captcha_json['captcha']
        captcha_token = captcha_json['token']
        
        self.save_to_png(captcha, "temp1.png")
        image = self.read_img("temp1.png")
        self.save_image_as_grayscale(image, "temp1.png")
        
        svgs=self.split_chars(captcha)
        captcha_data = []
        for i in range(len(svgs)):
            data=svgs[i]
            self.save_to_png(data, "temp.png")
            
            image = self.read_img("temp.png")
            self.save_image_as_grayscale(image, "temp.png")
            image = self.read_img("temp.png")
            image[np.where(image[...,0]>0)]=1
            
            captcha_data.append(image[...,0].flatten())
        
        return (captcha_data, captcha_token)
    
    def save_image_as_grayscale(self, image, name):
        image[...,3]=1
        image[np.where(image[...,0]>0)]=1
        plt.imsave(name,image[...,0],cmap=plt.cm.gray)
    
    def solve_captcha(self, svgs):
        model = svm_load_model('captcha_model')
        
        ans = svm_predict([0,0,0,0],np.array(svgs).tolist(),model, "-q")
        
        chars=[]
        for c in ans[0]:
            c=int(c)
            if(c<=9):
                chars.append(str(c))
            else:
                chars.append(chr(c+87))
        
        return ''.join(chars)  
    
    def log_in(self, username, password):
        
        #get and solve captcha
        (captcha_data, captcha_token) = self.process_captcha_data()
        captcha = self.solve_captcha(captcha_data)
        payload = {"entry_number":self.tnp_username,"password":self.tnp_password,"captcha":captcha,"captchaToken":captcha_token,"type":"placement"}
        
        #log in
        self.session = requests.Session()
        response = self.session.post(self.login_url, data=payload, verify=False)
        if(response.status_code!=200):
            return str(response.json())
        r = response.json()
        
        self.user = User(r['entry_number'], r['full_name'], r['eligible'], r['blocked'], r['selected'], r['department'], r['course'], r['accepted'], r['cv_verified'], r['application_limit'], r['contact'], r['token'])
        
        return False
        
    def check_login(self):
        data, status_code = self.get_json_response(self.companies_url)
        if(status_code!=200):
            print(data)
            print("Trying to login now...")
            response = self.log_in(self.tnp_username, self.tnp_password)
            if(response==False):
                print("Successfully logged in.")
            else:
                raise Exception("Login failed with the following error: \n%s" %(response))
    
    def run(self):
        
        self.check_login()
        
        (data, diff) = self.check_new_notifications(self.company_history_file)
        if(diff):
            print("New notifications")
            message = self.build_email_body(diff)
            self.send_email(["masterkapilkumar@gmail.com"], message, "Companies On Campus Placement Notification", bcc=self.recipient_email_list)
            self.dump_json(data, self.company_history_file)
            
        else:
            print("No new notifications")

if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="path of JSON file having configuration data")
    parser.add_argument('-t', '--time', help="Time (in seconds) gap for checking new notifications", default="1000", type=int)
    
    args = parser.parse_args()
    
    try:
        fin = open(args.config_file, 'r')
        config_data = json.loads(fin.read().strip())
        fin.close()
    except:
        print("Error reading configuration data:\n")
        traceback.print_exc()
        sys.exit(1)
    
    try:
        outgoing_server = config_data["outgoing_server"]
        outgoing_port = config_data["outgoing_port"]
        sender_email = config_data["sender_email"]
        sender_password = config_data["sender_password"]
        recipient_email_list = config_data["recipient_email_list"]
        recipient_email_list = list(map(lambda s: s.strip(), recipient_email_list.split(",")))
        captcha_url = "https://tnp.iitd.ac.in/api/captcha"
        login_url = "https://tnp.iitd.ac.in/api/student/login"
        tnp_username = config_data["tnp_username"]
        tnp_password = config_data["tnp_password"]
        tnp_password = hashlib.md5(tnp_password.encode()).hexdigest()
        companies_url = "https://tnp.iitd.ac.in/api/student/all-companies"
        history_file = config_data["history_file"]
        proxy_url = config_data.get("proxy_url", None)
        proxy_port = config_data.get("proxy_port", None)
        check_interval = args.time
    except KeyError:
        print("Missing configuration data:\n")
        traceback.print_exc()
        sys.exit(1)
    
    tnp_notifier = TnP_Company_Notifier(outgoing_server, outgoing_port, sender_email, sender_password, recipient_email_list, check_interval, login_url, captcha_url, companies_url, history_file, proxy_url, proxy_port, tnp_username, tnp_password)
    time_since_last_sent_error = 0
    while(True):
        try:
            tnp_notifier.run()
            time_since_last_sent_error = 0
        except KeyboardInterrupt:
            sys.exit(1)
        except:
            #handle any exception
            
            traceback.print_exc()
            print("\n")
            #Send email to owner in case of any error in interval of 6 hours
            if(time_since_last_sent_error > 21600):
                time_since_last_sent_error = 0
            if(time_since_last_sent_error == 0):
                print("Informing Kapil...")
                error_msg = "<b>TnpNotifier encountered an error, please debug it ASAP:</b><br><br>"
                error_msg += "<i>"+str(sys.exc_info())+"</i>"
                tnp_notifier.send_email(["masterkapilkumar@gmail.com"], error_msg, "TnP Notifier is down...")
                print("Email sent to Kapil...")
            time_since_last_sent_error += check_interval
        print("Pausing execution for %s seconds\n" %check_interval)
        time.sleep(check_interval)