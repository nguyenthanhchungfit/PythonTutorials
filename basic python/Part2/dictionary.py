point = {'x' : 1, 'y':2}
print (point)
print (point['x'])
point['z'] = 5
point['x'] = -1
print (point)
copy = point.copy()
point.clear()
print(point)
print(copy)

seq = ('x', 'z')
print(copy.fromkeys(seq, 10))
print(copy.keys())
print(copy.values())
#print(copy.has_key('y'))

