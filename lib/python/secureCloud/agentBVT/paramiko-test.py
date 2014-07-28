import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='172.18.0.10', port=22, username='root', password='P@ssw0rd')
stdin, stdout, stderr = ssh.exec_command('uptime')
print stdout.readlines()
