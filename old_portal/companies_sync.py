server_name = "smtp.iitd.ernet.in"
port = 25
sender_username = ""
sender_password = ""
tnp_username = ""
tnp_password = ""
toaddrs  = ['masterkapilkumar@gmail.com']

from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
import smtplib
import time

while True:
    
    old_data = ""
    try:
        history = open("history", 'r')
        old_data = history.read()
        history.close()
    except IOError:
        print("File does not exist!")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    payload = {'username': tnp_username, 'password': tnp_password, 'login': 'Submit'}
    
    url = "https://tnp.iitd.ac.in/tnp/training/student/_studentlogin.php"

    session = requests.Session()
    response = session.post(url, data=payload, verify=False)

    url = "https://tnp.iitd.ac.in/tnp/training/student/campus.php"
    response = session.get(url, verify=False)


    # response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    new_data = ""
    companies_table = soup.find_all("table")[0]
    for row in companies_table.find_all("tr"):
        for data in row.find_all("td"):
            if(data.b):
                new_data+=(str(data.b.contents[0].encode())+"\n")
            else:
                new_data+=(str(data.encode())+"\n")
        new_data+="\n"
    
    if(old_data==new_data):
        print("No new notification")
    else:
        print("New notifications!")
        print("Sending...")
        
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Tnp Notification"
        msg['From'] = sender_username
        msg['To'] = ','.join(toaddrs)
        
        msg.attach(MIMEText(str(soup), 'html'))
        

        server = smtplib.SMTP(server_name, port)
        server.ehlo()
        server.starttls()
        server.login(sender_username, sender_password)
        server.sendmail(fromaddr, toaddrs, msg.as_string())
        server.quit()
        print("Sent!")
        history = open("history", 'w+')
        history.write(new_data)
        history.close()
    time.sleep(30)

