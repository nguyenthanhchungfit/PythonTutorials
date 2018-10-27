import paramiko
# 
#username='chungnt', password='NTTthao231011335', timeout=5
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('127.0.0.1', password='thanhCHUNG')
stdin, stdout, stderr = ssh.exec_command("cat /etc/*-release", timeout=2)
print ("ssh succuessful. Closing connection")
res = stdout.read()
print(res)
ssh.close()
