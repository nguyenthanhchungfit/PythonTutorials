from urllib.request import urlopen
import json
httpobj = urlopen('https://api.github.com/users/voduytuan/repos')
data = json.loads(httpobj.read())
print(data)


# import wget
# fs = wget.download(url='https://api.github.com/users/voduytuan/repos')
# with open(fs, 'r') as f:
#     content = f.read()
# print(content)