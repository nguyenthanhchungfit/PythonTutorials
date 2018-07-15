f1 = open("data.txt", 'r', encoding='utf-8')
#f2 = fopen("data.txt", a)

data = f1.read()
#data = f1.read(1024) #doc 1024 bytes
print(data)

f2 = open('data2.txt', 'w', encoding='utf-8')
f2.write(data)

f1.close()
f2.close()

import os
#os.rename('data2.txt', 'copydata.txt')
os.remove('data2.txt')