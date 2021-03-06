from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from matplotlib import pyplot as plt
from bs4 import BeautifulSoup
from cairosvg import svg2png
from datetime import datetime
from weasyprint import HTML
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
import os

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
    
    def __init__(self, outgoing_server, outgoing_port, sender_email, sender_password, recipient_email_list, check_interval, login_url, captcha_url, companies_url, company_history_file, proxy_url=None, proxy_port=None, tnp_username='abc', tnp_password='123', owner_name="Kapil", owner_email="masterkapilkumar@gmail.com"):
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
        self.department_mapping = {'BB1': 'B.Tech in Biochemical Engineering & Biotechnology', 'CE1': 'B.Tech in Civil Engineering', 'CH1': 'B.Tech in Chemical Engineering', 'CS1': 'B.Tech in Computer Science & Engineering', 'EE1': 'B.Tech in Electrical Engineering', 'EE3': 'B.Tech in Electrical Engineering (Power and Automation)', 'ME1': 'B.Tech in Mechanical Engineering', 'ME2': 'B.Tech in Production & Industrial Engineering', 'MT1': 'B.Tech in Mathematics & Computing', 'PH1': 'B.Tech in Engineering Physics', 'TT1': 'B.Tech in Textile Engineering', 'BB5': 'B.Tech and M.Tech in Biochemical Engg & Biotechnology', 'CH7': 'B.Tech and M.Tech in Chemical Engineering', 'CS5': 'B.Tech and M.Tech in Computer Science & Engineering', 'MT6': 'B.Tech and M.Tech in Mathematics & Computing', 'MEB': 'B.Tech in Production & Industrial Engineering and M.Tech in Production Engineering', 'MEC': 'B.Tech in Mechanical Engineering and M.Tech in Mechanical Design', 'MEF': 'B.Tech in Mechanical Engineering and M.Tech in Applied Mechanics', 'MED': 'B.Tech in Production & Industrial Engineering and M.Tech in Mechanical Design', 'CSA': 'B.Tech in Textile Engineering and M.Tech in Computer Science & Engineering', 'CSE': 'B.Tech in Chemical Engineering and M.Tech in Computer Science & Engineering', 'CSF': 'B.Tech in Production & Industrial Engineering and M.Tech in Computer Science & Engineering', 'CEC': 'B.Tech in Civil Engineering and M.Tech in Structural Engineering', 'CED': 'B.Tech in Civil Engineering and M.Tech in Construction Engineering & Management', 'CSB': 'B.Tech in Engineering Physics and M.Tech in Computer Science & Engineering', 'MEA': 'B.Tech in Mechanical Engineering and M.Tech in Thermal Engineering', 'CSG': 'B.Tech in Mechanical Engineering and M.Tech in Computer Science & Engineering', 'CHE': 'M.Tech in Chemical Engineering', 'CYM': 'M.Tech in Molecular Engineering: Chemical Synthesis & Analysis', 'CEG': 'M.Tech in Geotechnical and Geoenvironmental Engineering', 'CEU': 'M.Tech in Rock Engineering & Underground Structures', 'CES': 'M.Tech in Structure Engineering', 'CEW': 'M.Tech in Water Resources Engineering', 'CET': 'M.Tech in Construction Engineering & Management', 'CEV': 'M.Tech in Environmental Engineering & Management', 'CEP': 'M.Tech in Transportation Engineering', 'MCS': 'M.Tech in Computer Science & Engineering', 'PHA': 'M.Tech in Applied Optics', 'PHM': 'M.Tech in Solid State Materials', 'TTF': 'M.Tech in Fibre Science & Technology', 'TTE': 'M.Tech in Textile Engineering', 'TTC': 'M.Tech in Textile Chemical Processing', 'AST': 'M.Tech in Atmospheric-Oceanic Science and Technology', 'BMT': 'M.Tech in Biomedical Engineering', 'JDS': 'Master of Design in Industrial Design', 'EEE': 'M.Tech in Communications Engineering', 'EET': 'M.Tech in Computer Technology', 'EEA': 'M.Tech in Control & Automation', 'EEN': 'M.Tech in Integrated Electronics & Circuits', 'EEP': 'M.Tech in Power Electronics, Electrical Machines & Drives', 'EES': 'M.Tech in Power Systems', 'CRF': 'M.Tech in Radio Frequency Design & Technology', 'MEM': 'M.Tech in Mechanical Design', 'MEE': 'M.Tech in Industrial Engineering', 'MEP': 'M.Tech in Production Engineering', 'MET': 'M.Tech in Thermal Engineering', 'AMA': 'M.Tech in Engineering Analysis & Design', 'JIT': 'M.Tech in Industrial Tribology & Maintenance Engineering', 'JES': 'M.Tech in Energy Studies', 'JID': 'M.Tech in Instrument Technology', 'JOP': 'M.Tech in Optoelectronics & Optical Communication', 'JPT': 'M.Tech in Polymer Science & Technology', 'JTM': 'M.Tech in Telecommunication Technology & Management', 'JVL': 'M.Tech in VLSI Design Tools & Technology', 'BEY': 'M.S.(R) in Biochemical Engineering and Biotechnology', 'CHY': 'M.S.(R) in Chemical Engineering', 'CEY': 'M.S.(R) in Civil Engineering', 'CSY': 'M.S.(R) in Computer Science & Engineering', 'BSY': 'M.S.(R) in Telecommunication Technology and Management', 'SIY': 'M.S.(R) in Information Technology', 'BLY': 'M.S.(R) in Biological Sciences', 'AMY': 'M.S.(R) in Applied Mechanics', 'MEY': 'M.S.(R) in Mechanical Engineering', 'EEY': 'M.S.(R) in Electrical Engineering', 'CYS': 'M.Sc in Chemistry', 'MAS': 'M.Sc in Mathematics', 'PHS': 'M.Sc in Physics', 'PHD': 'Doctor of Philosophy'}
        self.proxy_url = proxy_url
        self.proxy_port = proxy_port
        self.owner_name = owner_name
        self.owner_email = owner_email
        self._socket = socket.socket

    def get_json_response(self, url, headers=None, verify=False, type='GET'):
        time.sleep(1)
        if(not headers):
            headers = self.headers
        if(type=='GET'):
            num_tries = 2
            data=None
            for _ in range(num_tries):
                response = requests.get(url, headers=headers, verify=verify)
                try:
                    data = response.json()
                    return data, response.status_code
                except json.decoder.JSONDecodeError as e:
                    print(f"ERROR: {e}\nRetrying...")
                    time.sleep(1)
            if data is None:
                raise Exception(f"Unable to fetch json response: {url}\nError: {response.content}")
            return data, response.status_code
    
    def find_json_object(self, data, it, ignore_attrs=[], shortlist=False):
        if(shortlist):
            for item in data:
                if it['profile_code']==item['profile_code']:
                    if 'status' in it and 'status' in item and 'shortlist' in it['status'].lower() and 'shortlist' not in item['status'].lower():
                        return False
                    elif 'shortlist_frozen' in it and 'shortlist_frozen' in item and it['shortlist_frozen'] and not item['shortlist_frozen']:
                        return False
                    else:
                        return True
            if 'status' in it and 'shortlist' in it['status'].lower():
                return False
            if 'shortlist_frozen' in it and it['shortlist_frozen']:
                return False
            return True
        for item in data:
            flag = True
            for attr in self.contents["companies"]:
                if (attr not in item and attr not in it) or attr in ignore_attrs:
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
    
    
    def json_diff(self, new_data, old_data, shortlist):
        diff = []
        for item in new_data:
            if not shortlist:
                flag = self.find_json_object(old_data, item, ignore_attrs = ["ppt_applied"])
            else:
                flag = self.find_json_object(old_data, item, shortlist=shortlist)
            if not flag:
                diff.append(item)
            
        return diff
        
    def check_new_notifications(self, old_file, shortlist=False):
        self.headers["Authorization"] = "Bearer " + self.user.token
        if shortlist:
            data, _ = self.get_json_response("https://tnp.iitd.ac.in/api/student/companies", headers=self.headers)
        else:
            data, _ = self.get_json_response(self.companies_url, headers=self.headers)
        
        try:
            fin = open(old_file, 'r')
            old_data = json.loads(fin.read())
            fin.close()
        except IOError as e:
            print("No history found...")
            old_data = []
        
        diff = self.json_diff(data, old_data, shortlist)
        
        if(diff == []):
            return (data, None)
        
        return (data, diff)
        
    def get_pretty_date(self, datestr, format):
        if(datestr.strip()==""):
            return ""
        d = datetime.strptime(datestr,format)
        return d.strftime("%a, %b %d, %I:%M %p")
    
    def html_to_pdf(self, html):
        html = HTML(string=html)
        pdf = html.write_pdf()
        return pdf
    
    def build_jnf_html(self, data):
        def bool_to_str(val):
            if(val==True):
                return "Yes"
            if(val==False):
                return "No"
            return str(val).replace("\n","<br>")
        data = {k: bool_to_str(v) for k, v in data.items()}     #convert true/false to Yes/No 

        if data.get('eligible_depts'):
            data['eligible_depts'] = ', '.join(map(lambda x: self.department_mapping.get(x,"Unknown Deptt."), eval(data['eligible_depts'])))
        else:
            data['eligible_depts'] = "None"
        
        table = '''<table style="margin:auto;width:95%%;white-space:pre-line;font-size:9pt;border-spacing:10px", class="myclass">
            <colgroup><col style="width: 20%%;" span="1"><col style="width: 85%%;" span="1"></colgroup>
            <tbody>
            %s
            </tbody>
        </table>
        '''
        
        company_overview_fields = {"Name": "name", "Website":"website", "Company Type":"company_type", "Startup":"startup", "Year of Incorporation":"incorp_year", "Description":"description"}
        job_details_fields = {"Designation": "profile", "Type":"type", "Place of Posting":"location", "Job Details":"project_details", "Joining By":"join_by"}
        salary_details_fields = {"CTC": "ctc", "Gross":"gross", "CTC Breakup":"ctc_breakup", "Perks / Bonus":"perks"}
        selection_process_fields = {"Resume Shortlist": "resume", "Written Test":"written_test", "Online Test":"online_test", "Group Discussion":"group_discussion", "Medical Test":"medical_test", "Personal Interview":"interview", "No. of Rounds":"rounds", "No. of Offers":"offers", "Minimum CGPA":"min_cgpa"}
        eligibility_fields = {"Recruiting PHDs": "phd", "Eligible Departments":"eligible_depts"}
        company_overview=job_details=salary_details=selection_process=eligibility=""
        
        for field, key in company_overview_fields.items():
            if field in ['ctc','gross']:
                company_overview += '''<tr><td style="vertical-align: top;"><b>%s:</b></td><td style="vertical-align: top;">%s</td></tr>'''%(field, data.get(key,"NA") + data.get('currency',""))
            company_overview += '''<tr><td style="vertical-align: top;"><b>%s:</b></td><td style="vertical-align: top;">%s</td></tr>'''%(field, data.get(key,"NA"))
        for field, key in job_details_fields.items():
            job_details += '''<tr><td style="vertical-align: top;"><b>%s:</b></td><td style="vertical-align: top;">%s</td></tr>'''%(field, data.get(key,"NA"))
        for field, key in salary_details_fields.items():
            salary_details += '''<tr><td style="vertical-align: top;"><b>%s:</b></td><td style="vertical-align: top;">%s</td></tr>'''%(field, data.get(key,"NA"))
        for field, key in selection_process_fields.items():
            selection_process += '''<tr><td style="vertical-align: top;"><b>%s:</b></td><td style="vertical-align: top;">%s</td></tr>'''%(field, data.get(key,"NA"))
        for field, key in eligibility_fields.items():
            eligibility += '''<tr><td style="vertical-align: top;"><b>%s:</b></td><td style="vertical-align: top;">%s</td></tr>'''%(field, data.get(key,"NA"))
        
        
        table_body = '''
            <div style="font-size:18px;margin-bottom:10px;margin-top:16px">Company Overview</div>%s
            <div style="font-size:18px;margin-bottom:10px;margin-top:16px">Job Details</div>%s
            <div style="font-size:18px;margin-bottom:10px;margin-top:16px">Salary Details</div>%s
            <div style="font-size:18px;margin-bottom:10px;margin-top:16px">Selection Process</div>%s
            <div style="font-size:18px;margin-bottom:10px;margin-top:16px">Eligibility</div>%s
        </div>
        '''%(table%company_overview, table%job_details, table%salary_details, table%selection_process, table%eligibility)
        
        html = '''<html><body>
            <h2 style="text-align: center">Job Notification Form, IIT Delhi</h2>
            %s
        </body></html>'''%table_body
        
        return html
        
        # open("test.pdf", 'wb').write(pdf)

    def saveJNFs(self, pdfs):
        if not os.path.exists("./JNFs/"):
            os.makedirs("./JNFs/")
        for pdf in pdfs:
            open("./JNFs/"+pdf['filename'].replace('/',''), 'wb').write(pdf['data'])
        print("Saved all JNFs")
    
    def build_attachments(self, data):
        attachments = []
        print(f"Downloading {len(data)} JNFs")
        for item in data:
            link = "https://tnp.iitd.ac.in/api/placement/company?code="+item['profile_code']
            jnf, _ = self.get_json_response(link, headers=self.headers)
            html = self.build_jnf_html(jnf)
            pdf = self.html_to_pdf(html)
            attachments.append({"filename":"%s (%s).pdf"%(item['name'],item['profile']),"data":pdf})
            print(f"Downloaded {item['name']} ({item['profile']}).pdf")
        return attachments
    
    def build_email_body(self, data, shortlist=False):
        
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
            if(shortlist):
                if(item['shortlist_frozen'] and 'status' in item and 'shortlist' in item['status'].lower()):
                    companies += item_body.format('<font color="red">'+"Shortlist Uploaded! <br> Shortlist Frozen!"+"</font>")
                elif(item['shortlist_frozen']):
                    companies += item_body.format('<font color="red">'+"Shortlist Frozen!"+"</font>")
                else:
                    companies += item_body.format('<font color="red">'+"Shortlist Uploaded!"+"</font>")
            else:
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
    
    def send_email(self, to_addrs, email_body, subject="", bcc=None, attachments=[]):
        
        print("Sending email...")
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = 'whomsoever-it-may-concern'
        
        body = MIMEMultipart('alternative')
        body.attach(MIMEText(email_body, 'html'))
        msg.attach(body)
        
        for attachment in attachments:
            attachFile = MIMEBase('application', attachment['filename'].split(".")[-1])
            attachFile.set_payload(attachment['data'])
            encoders.encode_base64(attachFile)
            attachFile.add_header('Content-Disposition', 'attachment', filename=attachment['filename'])
            msg.attach(attachFile)

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
        
        self.user = User(r['entry_number'], r['full_name'], r['eligible'], r['blocked'], r['selected'], r['department'], r['course'], r['accepted'], r['cv_verified'], r['application_limit'], r.get('contact'), r['token'])
        
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
            attachments = self.build_attachments(diff)
            self.saveJNFs(attachments)
            self.send_email([self.owner_email], message, "Companies On Campus Placement Notification", bcc=self.recipient_email_list, attachments=attachments)
            self.dump_json(data, self.company_history_file)
        else:
            print("No new notifications")
        
        (data, diff) = self.check_new_notifications("shortlist-"+self.company_history_file, shortlist=True)
        if(diff):
            print("New shortlists uploaded")
            message = self.build_email_body(diff, shortlist=True)
            attachments = self.build_attachments(diff)
            self.saveJNFs(attachments)
            self.send_email([self.owner_email], message, "Shortlist Notification", bcc=self.recipient_email_list, attachments=attachments)
            self.dump_json(data, "shortlist-"+self.company_history_file)
        else:
            print("No new shortlists")
        

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
#TODO - check whether all the email ids in the list are valid or not
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
        owner_name = config_data.get("owner_name", "Kapil")
        owner_email = config_data.get("owner_email", "masterkapilkumar@gmail.com")
        check_interval = args.time
    except KeyError:
        print("Missing configuration data:\n")
        traceback.print_exc()
        sys.exit(1)
    
    tnp_notifier = TnP_Company_Notifier(outgoing_server, outgoing_port, sender_email, sender_password, recipient_email_list, check_interval, login_url, captcha_url, companies_url, history_file, proxy_url, proxy_port, tnp_username, tnp_password, owner_name, owner_email)
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
