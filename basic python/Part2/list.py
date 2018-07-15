numbers = [3,2,1,4,5]

names = ['Marry', 'jetty', 'Tom']

print(numbers[2])
print(names[1])
print(len(names))

try:
    names[4]
except IndexError:
    print("Out of range")

print('jetty' in names)
print(numbers[-2:])
del numbers[2]
print(numbers)
del numbers[1:2]
print(numbers)

a = [1, 2]
b = [3, 4]
print(a+b+names)
names.append('Chung')
print(names)
names.pop()
print(names)
#print(names.index('Chung'))
print(names.index('jetty'))
names.reverse()
print(names)
names.sort()
print(names)
