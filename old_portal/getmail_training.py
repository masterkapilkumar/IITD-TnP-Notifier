sender_server_name = "smtp.gmail.com"
port = 587
sender_username = ""
sender_password = ""
toaddrs  = ['masterkapilkumar@gmail.com']

from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
import smtplib
import time
import sys

while True:
    url = "http://tnp.iitd.ac.in/notices/training/notify.php"

    old_data = ""
    try:
        history = open("history_training", 'r')
        old_data = history.read()
        history.close()
    except IOError:
        print("No history found...")

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

        response = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        new_data = ""
        for i in range(1,7):
            notifications = soup.find_all("div", {"id": str(i)})[0]
            for row in notifications.find_all("tr"):
                for data in row.find_all("td"):
                    if(data.b):
                        new_data+=(str(data.b.contents[0].encode())+"\n")
                    if(data.a):
                        new_data+=(str(data.a['href'].encode())+"\n")
                new_data+="\n"

        if(old_data==new_data):
            print("No new notification")
        else:
            print("New notifications!")
            print("Sending...")

            fromaddr = ''
            
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "T&P Training Notification"
            msg['From'] = fromaddr
            msg['To'] = str(toaddrs)
            print('to: '+msg['To'])
            
            soup.find("div", {"id": "header"}).decompose()
            soup.find("div", {"id": "menu"}).decompose()
            soup.find("div", {"id": "page"}).decompose()
            
            msg.attach(MIMEText(str(soup), 'html'))
            

            server = smtplib.SMTP(sender_server_name, port)
            server.ehlo()
            server.starttls()
            server.login(sender_username, sender_password)
            server.sendmail(fromaddr, toaddrs, msg.as_string())
            server.quit()
            print("Sent!\n")
            history = open("history_training", 'w+')
            history.write(new_data)
            history.close()
        time.sleep(300)
    except KeyboardInterrupt:
        sys.exit(1)
    except:
        print('Error: '+str(sys.exc_info()))
        print("\n")
        time.sleep(300)
