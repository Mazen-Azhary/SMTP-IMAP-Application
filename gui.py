from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QMessageBox, QDialog, QLabel, QTextEdit
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
from imap_server import imap_server
from smtp_server import smtp_server
import sys

#PyQt5 GUI integrating with IMAP and SMTP email classes
#using ui.ui file created in Qt Designer

class EmailDetailDialog(QDialog):
    #display full email details from qtable in view emails page
    def __init__(self, email, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Email Details")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        # Create title with sender and subject
        title = QLabel(f"From: {email['from']}\nSubject: {email['subject']}\nDate: {email['date']}")
        title.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        body_display = QTextEdit()
        body_display.setText(email['body'])
        body_display.setReadOnly(True)
        layout.addWidget(body_display)
        
        self.setLayout(layout)

class GUII(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("ui.ui", self)  
        # Set window title and favicon
        self.setWindowTitle("Email Client App")
        self.setWindowIcon(QIcon("images/mail.png"))
        # Initialize email classes
        self.imap = imap_server()
        self.smtp = smtp_server()
        self.setFixedSize(1173, 863)
        # Connect buttons
        self.sendEmailButton.clicked.connect(self.go_to_send_page)
        self.viewMailboxButton.clicked.connect(self.go_to_viewmail_page)
        self.exitButton.clicked.connect(self.close)        
        self.sendMailConfirmButton.clicked.connect(self.send_email)
        self.backtoMenuButton1.clicked.connect(self.go_to_main_menu)
        self.backtoMenuButton2.clicked.connect(self.go_to_main_menu)
        
        # Email list storage
        self.emails = []
    
    def go_to_send_page(self):
        self.stackedWidget.setCurrentIndex(2)
        # Clear input fields
        self.recieverEmailText.clear()
        self.subjectText.clear()
        self.bodyText.clear()
    
    def go_to_viewmail_page(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Loading")
        msg.setText("Fetching emails... Please wait")
        msg.show()
        QApplication.processEvents()
        
        # Fetch emails
        self.emails = self.imap.fetch_emails(limit=10)
        msg.close()
        QApplication.processEvents()
        
        if not self.emails:
            QMessageBox.information(self, "No Emails", "No emails found in inbox")
            return
        
        # Show popup with email count
        QMessageBox.information(self, "Success", f"Fetched {len(self.emails)} emails")
        
        self.show_emails_list()
    
    def show_emails_list(self):
        # Switch to email view page
        self.stackedWidget.setCurrentIndex(0)
        
        # Set column count
        self.mailTable.setColumnCount(4)
        # Set column headers
        self.mailTable.setHorizontalHeaderLabels(["From", "Subject", "Date", "Body"])
        # Clear previous data
        self.mailTable.setRowCount(0)
        # Set row count
        self.mailTable.setRowCount(len(self.emails))
        
        #fill table with emails
        for idx, email in enumerate(self.emails):
            #extract features from email
            sender = email['from'].split('<')[0].strip()
            subject = email['subject'][:60] if email['subject'] else "(No Subject)"
            date = email['date'][:20]
            body_preview = email['body'][:80]
            
            # Add items to table
            self.mailTable.setItem(idx, 0, QTableWidgetItem(sender))
            self.mailTable.setItem(idx, 1, QTableWidgetItem(subject))
            self.mailTable.setItem(idx, 2, QTableWidgetItem(date))
            self.mailTable.setItem(idx, 3, QTableWidgetItem(body_preview))
        
        # Resize columns to fit content
        self.mailTable.resizeColumnsToContents()
        
        self.mailTable.setColumnWidth(0, 150)  # From
        self.mailTable.setColumnWidth(1, 250)  # Subject
        self.mailTable.setColumnWidth(2, 100)  # Date
        self.mailTable.setColumnWidth(3, 500)  # Body
        
        # Allow last column(email body) to stretch
        self.mailTable.horizontalHeader().setStretchLastSection(True)
        
        # Connect row click signal to show email details
        self.mailTable.itemClicked.connect(self.on_email_row_clicked)
    
    def on_email_row_clicked(self, item):
        #slot for email row click signal, show full email details
        row = item.row()
        if row < len(self.emails):
            email = self.emails[row]
            # Create and show email detail dialog
            dialog = EmailDetailDialog(email, self)
            dialog.exec_()
            
    def send_email(self):
        #Send email from input fields
        receiver = self.recieverEmailText.toPlainText().strip()
        subject = self.subjectText.toPlainText().strip()
        body = self.bodyText.toPlainText().strip()
        
        # Validate inputs
        if not receiver or not subject or not body:
            QMessageBox.warning(self, "Missing Fields", "Please fill all fields")
            return
        
        success = self.smtp.send_email(receiver, subject, body)
        
        if success:
            QMessageBox.information(self, "Success", f"Email sent to {receiver}")
        else:
            QMessageBox.critical(self, "Error", "Failed to send email")
    
    def go_to_main_menu(self):
        self.stackedWidget.setCurrentIndex(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GUII()
    window.show()
    sys.exit(app.exec_())