import json
mystring = '{"a":1,"b":2,"c":3,"d":4,"e":5}'
data2 = json.loads(mystring)
data = json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}])
print (data)
print(data2)
