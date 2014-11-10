import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

msg = MIMEMultipart()
sender = 'user@example.com' #will be changed
subject = "[ LAB ]tempctrl finished"
body = "tempchamber program finished on [machinename] at [finished time].\n"
body +="outputs are [outputfilename] and [logfilename]"

msg['From'] = sender
msg['To'] = sender
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))
text=msg.as_string()
#print text
# Send the message via our SMTP server
s = smtplib.SMTP('smtp.server.com') #will be changed
s.sendmail(sender,sender, text)
s.quit()

