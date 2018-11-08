# IITD-TnP-Notifier
Sends real time email notifications for TnP notices.

***getmail_general_notifications.py*** - General placement/training notifications for new TnP Portal.

***companies_on_campus/get_company_details.py*** - Notifications for Companies on campus on new TnP Portal.

***old_portal/getmail_training.py*** - General training notifications for old TnP Portal.

***old_portal/companies_sync.py*** - Notifications for Companies on campus on old TnP Portal.


## How to use
    usage: getmail_general_notifications.py [-h] [-t TIME] [-T {placement,training}] config_file

    positional arguments:
        config_file           path of JSON file having configuration data

    optional arguments:
        -h, --help            show this help message and exit
        -t TIME, --time TIME  Time (in seconds) gap for checking new notifications
        -T {placement,training}, --type {placement,training} Notifications type - Training/Placement
    
The JSON configuration file should have the following data:
 - **outgoing_server**: Name of the outgoing server for sending emails
 - **outgoing_port**: Port of the outgoing server
 - **sender_email**: Sender email address
 - **sender_password**: password of sender email id
 - **recipient_email_list**: comma separated list of recipent users.
 - **tnp_username**: Tnp portal username
 - **tnp_password**: TnP portal password
 - **history_file**: File name for storing history
 - **owner_name**: Name of the owner (not-required)
 - **owner_email**: Email of the owner, to send faliure emails (not-required)
 - **proxy_url**: Proxy url (not-required)
 - **proxy_port**: Proxy port (not-required)

### Dependencies
- Python 3.x
- Python libraries
    * requests
    * smtplib
    * PySocks
    * BeautifulSoup
    * cairosvg
