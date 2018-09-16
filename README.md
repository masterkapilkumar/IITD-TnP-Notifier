# IITD-TnP-Notifier
Sends real time email notifications for TnP notifications.

***getmail_placement.py*** - Placement notifications for new TnP Portal.

***old_portal/getmail_training.py*** - Training notifications for old TnP Portal.

***old_portal/companies_sync.py*** - Notifications for Companies on campus on old TnP Portal.

***old_portal/companies_sync.py*** - Notifications for Companies on campus on old TnP Portal.


## How to run
    python getmail_placement.py timeout_interval
    
You can change various parameters such as email server details, recipent list, proxy on/off in the main function of the script.

### Dependencies
- Python 3.x
- Python libraries - requests, smtplib, socket, socks
