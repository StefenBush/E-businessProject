import smtplib
from email.mime.text import MIMEText


subject = "新版学习方案"
content = "每天抄五遍就好了"
sender = "2317708584@qq.com"
receiver = "793115964@qq.com,2317708584@qq.com"

password = "nbzajrgfctxfdjeg"
message = MIMEText(content, "plain", "utf-8")
message["Subject"] = subject
message["To"] = receiver
message["From"] = sender

smtp = smtplib.SMTP_SSL("smtp.qq.com", 465)
smtp.login(sender,password)
smtp.sendmail(sender,receiver.split(","), message.as_string())
smtp.close()







