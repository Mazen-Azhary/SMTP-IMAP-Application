import imaplib
from email.parser import Parser
import html2text
from dotenv import load_dotenv
import os
from plyer import notification
load_dotenv()



"""
this script uses IMAP : internet message access protocol to get emails from my email's inbox
by first fetching their id's , then using those id's we get from 0 to 10 full emails with their
bodies , subject , and sender 

I used an enviroment file to hide my credentials for security

Since most emails today use HTML to send emails in fancy formats , we use html2text to remove html tags
"""



class imap_server:
    def __init__(self):
        #env vars
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        self.username = os.getenv("EMAIL_USERNAME")
        self.password = os.getenv("EMAIL_PASSWORD")
        
    def send_notification(self, title, message):
        #Send Windows desktop notification
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="elbatta elsha2eya",
                timeout=10  # notification stays for 10 seconds
            )
        except Exception as e:
            print(f"Error sending notification: {e}")
    
    def extract_email_body(self, email_message):
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.get_payload():
                part_type = part.get_content_type()
                
                if part_type == "text/html":
                    html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    # Convert HTML to plain text using html2text
                    h = html2text.HTML2Text()
                    h.ignore_links = True  # Ignore links
                    h.ignore_images = True  # Ignore images
                    h.ignore_emphasis = False  # Keep bold/italic
                    return h.handle(html_body).strip()
                
                elif part_type == "text/plain" and not body:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        return body.strip()
    
    def connect(self):
        #create imap connection
        try:
            server = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            server.login(self.username, self.password)
            return server
        except Exception as e:
            print(f"Error connecting to IMAP: {e}")
            return None
    
    def fetch_emails(self, limit=10, mailbox="INBOX"):
        #Fetch latest emails from specified mailbox
        emails = []
        
        try:
            server = self.connect()
            if not server:
                print("Connection failed")
                return emails
            
            # Select mailbox
            status, messages = server.select(mailbox)
            
            # Get all email IDs
            status, email_ids = server.search(None, "ALL")
            email_id_list = email_ids[0].split()
            
            if not email_id_list:
                print("No emails found")
                server.close()
                server.logout()
                return emails
            
            # Get only the latest N emails
            size = min(limit, len(email_id_list))
            latest_email_ids = email_id_list[-size:]
            
            # Parse each email
            parser = Parser()
            for email_id in latest_email_ids:
                status, msg_data = server.fetch(email_id, "(RFC822)")
                email_message = parser.parsestr(msg_data[0][1].decode())
                
                email_dict = {
                    'from': email_message['From'],
                    'subject': email_message['Subject'],
                    'date': email_message['Date'],
                    'content_type': email_message.get_content_type(),
                    'body': self.extract_email_body(email_message),
                    'id': email_id.decode()
                }
                emails.append(email_dict)
                sender_name = email_message['From'].split('<')[0].strip()
                self.send_notification(
                    title="New Email",
                    message=f"From: {sender_name}\nSubject: {email_dict['subject'][:50]}"
                )
            server.close()
            server.logout()
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
        
        return emails
    
    def display_email(self, email):
        print(f"\n{'='*60}")
        print(f"From: {email['from']}")
        print(f"Subject: {email['subject']}")
        print(f"Date: {email['date']}")
        print(f"{'-'*60}")
        print(f"Body:\n{email['body'][:]}...")  
        print(f"{'='*60}\n")


if __name__ == "__main__":
    mailer = imap_server()    
    # Fetch latest 10 emails
    emails = mailer.fetch_emails(limit=10)
    
    #print all emails
    for email in emails:
        mailer.display_email(email)
 
    # if emails:
    #     first_email = emails[0]
    #     print(f"First email subject: {first_email['subject']}")
    #     print(f"From: {first_email['from']}")