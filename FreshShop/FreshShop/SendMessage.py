import requests

url = "http://106.ihuyi.com/webservice/sms.php?method=Submit"

account = "C01565544"
password = "7dac869f6d0e9c8c1a7bc3093bd3ff65"
mobile = "18617802669"
content = "您的验证码是：888888。请不要把验证码泄露给其他人。"

headers = {
    "Content-tpe": "application/x-www-form-urlencoded",
    "Accept": "text/plain"
}

data = {
    "account": account,
    "password": password,
    "mobile": mobile,
    "content": content,
}

response = requests.post(url, headers=headers, data=data)
print(response.content.decode())

