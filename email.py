import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

msg = MIMEMultipart()
sender = 'user@example.com'
subject = "[ LAB ]tempctrl finished"
body = "tempchamber program finished on [machinename]\n"
body +="outputs are [outputfilename] and [logfilename]"

msg['From'] = sender
msg['To'] = sender
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))
text=msg.as_string()
#print text
# Send the message via our SMTP server
s = smtplib.SMTP('smtp.server.com')
s.sendmail(sender,address_book, text)
s.quit()

