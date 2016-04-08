import requests

url = 'http://127.0.0.1:5000/upload'
files = {'file': open('/Users/lkhamsurenl/Downloads/icon.png', 'rb')}

r = requests.post(url, files=files)

print(r.text)