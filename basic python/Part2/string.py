str1 = "Hello"
str2 = 'world'

print(str1[0])

paragraph = """This is line 1
This is line 2
This is line 3"""

print(paragraph)

print(str1 + " " + str2)
print(str1[0:4])
print(str1[0:-2])
print(str1[:3])
print(str1[1:])

print(len(str1))

print(paragraph.replace('line', 'row'))

print(str1.find('l'))
print(str1.rfind('l'))

print(paragraph.split('\n'))
print(paragraph.splitlines())

print(' Hello World  '.strip())
print(' Hello World  '.lstrip())
print(' Hello World  '.rstrip())

print('12345'.isnumeric())
print(str1.lower())
print(str1.upper())