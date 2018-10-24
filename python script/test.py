import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('10.30.65.21', 10077))
    print ("Port 22 reachable")
except socket.error as e:
    print ("Error on connect: %s" % e)
s.close()