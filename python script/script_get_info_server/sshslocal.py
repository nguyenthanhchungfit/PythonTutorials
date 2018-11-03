import paramiko
# 
#username='chungnt', password='NTTthao231011335', timeout=5
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect('10.30.80.79', username='zdeploy', timeout=2)
    try:
        stdin, stdout, stderr = ssh.exec_command("cat /etc/*-release", timeout=2)
        print ("ssh succuessful. Closing connection")
        res = stdout.read()
        print(res.decode('utf-8'))
        ssh.close()
    except (paramiko.BadHostKeyException, paramiko.AuthenticationException, 
        paramiko.SSHException) as e:
        print('1234567890')
except IOError as error:
    print('Exception: Bad connection')
    print(error)
finally:
    if ssh:
        ssh.close()

# ssh.connect('10.30.80.14', username='zdeploy')
# stdin, stdout, stderr = ssh.exec_command("lsb_release -a", timeout=2)
# print ("ssh succuessful. Closing connection")
# res = stdout.read()
# print(res)
# ssh.close()