# pip install BeautifulSoup
# pip install lxml
from bs4 import BeautifulSoup as Soup
websitehtml = '''
<html>
<head>
</head>
<body>
<p>Go go</p>
<p>Don't move</p>
</body>
</html>
'''
soup = Soup(websitehtml, 'lxml')
pList = soup.find_all('p')
for pEle in pList:
    print(pEle.string)

