import paramiko
# 
#username='chungnt', password='NTTthao231011335', timeout=5
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('127.0.0.1', port=22, password='thanhCHUNG')
stdin, stdout, stderr = ssh.exec_command("lsb_release -a", timeout=2)
print ("ssh succuessful. Closing connection")
print(stdout.read())
stdout=stdout.readlines()
ssh.close()
print ("Connection closed")
output=""
print(stdout)
for line in stdout:
    output=output+line
if output!="":
    print (output)
else:
    print ("There was no output for this command")
#, 