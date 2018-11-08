import xlsxwriter
import math
import sys
import paramiko
import re

# connect to server and get outputstream
def getConnection(ip, username='zdeploy'):
    if(ip != ''):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname = ip, username=username)
            print('*** Connected to:' + ip + ' with username=' + username)
            return ssh
        except IOError as error:
            print('!!! Error connect to ' + ip + ' with username=' +username)
            print(error)
            return None
    return None

def getOutputStreamFromServer(sshClient, cmd):
    if(sshClient is not None):
        try:
            stdin, stdout, stderr = sshClient.exec_command(cmd, timeout=2)
            res = stdout.read()
            return res.decode('utf-8')
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException, 
            paramiko.SSHException) as e:
            print('Error when execute command ' + cmd)
            print(e)
            return ''
        return ''
    return ''
   
# get Ip from text file
def getListIp(pathFile):
    f1 = open(pathFile, 'r')
    data = f1.read()
    arr = data.split('\n')
    return arr

# parseOutputStream to useful data
# parse ram : #b'MemTotal:       16367992 kB\n'
def extractMemInfo(inputStream):
    if(inputStream != ''):
        lenStr= len(inputStream)
        strContent = inputStream[0: lenStr - 1]
        while("  " in strContent):
            strContent = strContent.replace("  ", " ")
        params = strContent.split(' ')
        ram = 0
        if(params[2] == 'B'):
            ram = math.ceil(float(params[1])/(1024*1024*1024))
        elif(params[2] == 'kB'):
            ram = math.ceil(float(params[1])/(1024*1024))
        elif(params[2] == 'mB'):
            ram = math.ceil(float(params[1])/(1024))
        return ram
    return 0

# parse cpu : #b'cpu cores\t: 4\n'
def extractCpuInfo(inputStream):
    if(inputStream != ''):
        lenStr= len(inputStream)
        strContent = inputStream[0: lenStr - 1]
        while("  " in strContent):
            strContent = strContent.replace("  ", " ")
        strContent = strContent.replace('\t', '')
        cpu = 0
        params = strContent.split(':')
        cpu = int(params[1])
        return cpu
    return 0

# parse jdk.version
# b'lrwxrwxrwx 1 root root 30 Th05 14 14:42 /zserver/java/jdk -> /zserver/java/jdk1.8.0_162-x64\n'
# total 335388
# drwxrwxrwx  9 root    root         4096 Mar  2  2011 apache-activemq-5.4.2
# drwxrwxrwx  6 root    root         4096 Dec 20  2010 apache-ant-1.8.2
# drwxrwxrwx 10 root    root         4096 Dec 12  2011 apache-tomcat-7.0.8
# drwxrwxrwx  9 root    root         4096 Mar  2  2011 axis2-1.5.4
# lrwxrwxrwx  1 root    root           11 Nov 17  2015 jdk -> jdk1.6.0_31
# lrwxrwxrwx  1 root    root           11 Nov 17  2015 jdk1.6.0 -> jdk1.6.0_31
# drwxrwxrwx  9 zdeploy es_user      4096 Nov 17  2015 jdk1.6.0_31
# drwxrwxrwx 10 zdeploy es_user      4096 Jun 27  2011 jdk1.7.0
# drwxrwxrwx  8 zdeploy es_user      4096 Oct  8  2013 jdk1.7.0_45-x64
# drwxrwxrwx  8 zdeploy es_user      4096 Dec 19  2013 jdk1.7.0_51-x64
# drwxr-xr-x  8 uucp        143      4096 Apr 11  2015 jdk1.7.0_80
# -rw-rw-r--  1    1000    1000 153530841 Feb 10  2018 jdk1.7.0_80-x64.tar.gz
# -rw-rw-r--  1    1000    1000 189815615 Mar  5  2018 jdk1.8.0_1062-x64.tar.gz
# drwxrwxrwx  8 uucp        143      4096 Jun 17  2014 jdk1.8.0_11-x64
# drwxr-xr-x  8 uucp        143      4096 Mar 15  2017 jdk1.8.0_131
# drwxrwxrwx 17 root    root        12288 Jan 19  2018 lib
# -rwxrwxrwx  1 root    root          199 Jun  7  2012 link
# -rwxrwxrwx  1 root    root          234 Jun  7  2012 set_env
# -rwxrwxrwx  1 zdeploy es_user       440 Feb 25  2014 set_env.cmd
# -rwxrwxrwx  1 zdeploy es_user       369 Feb 25  2014 set_env_jdk7.cmd
# drwxrwxrwx 10 root    root         4096 Dec 12  2011 zookeeper-3.3.2
def extractJdkVersion(inputStream):
    if(inputStream != ''):
        ind = inputStream.rfind("->")
        res = ""
        if(ind >= 0):
            strLib = inputStream[ind + 3 : len(inputStream) - 1]
            indJdk = strLib.find('jdk')
            if(indJdk >= 0):
                res = strLib[indJdk + 3 : ]
        return res
    return ''

def extractJdkVersionV2(inputStream):
    if(inputStream != ''):
        while('  ' in inputStream):
            inputStream = inputStream.replace('  ', ' ')
        arrEle = inputStream.split('\n')
        listJdk = []
        for ele in arrEle:
            arrParams = ele.split(' ')
            if(len(arrParams) == 9):
                strJdk = arrParams[8]
                if('jdk' in strJdk and '-x64' in strJdk):
                    strJdk = strJdk.replace('jdk', '')
                    strJdk = strJdk.replace('.tar.gz', '')
                    listJdk.append(strJdk)
        verF = 0
        jdkRes = ''
        for jdk in listJdk:
            ver = re.search('_(.+?)-', jdk)
            if ver:
                verNumber = int(ver.group(1))
                if(verNumber > verF):
                    verF = verNumber
                    jdkRes = jdk
        return jdkRes
    return ''

# parse jzcommon
def extractJzcommon(inputStream):
    if(inputStream != ''):
        arrLib = inputStream.split('\n')
        arrLibJz = []
        for item in arrLib:
            if("libJZCommonX" in item):
                item = item.replace("libJZCommonX", "")
                item = item.replace("-", "")
                item = item.replace(".so", "")
                arrLibJz.append(item)
        return max(arrLibJz)
    return ''

    #print(arrLib)

# parse memcache
def extractMemcache(inputStream):
    if(inputStream != ''):
        return 'Ready'
    return 'Not ready'

# parse resize
def extractResize(inputStream):
    if(inputStream != ''):
        return 'Ready'
    return 'Not ready'
# parse os
def extractOsname(inputStream):
    osname = ''
    osversion = 0
    if(inputStream != ''):
        arrEle = inputStream.split('\n')
        for ele in arrEle:
            arrParams = ele.split(':\t')
            if(arrParams[0] == 'Distributor ID'):
                osname =arrParams[1].lower()
            elif(arrParams[0] == 'Release'):
                osversion = arrParams[1].split('.')[0]
        return osname + ' ' + osversion
    return ''

# parse os v2
def extractOsnameV2(inputStream):
    osname = ''
    osversion = '0'
    if(inputStream != ''):
        osfirst = extractOsnameV2Os6(inputStream)
        if(osfirst != ''):
            return osfirst
        arrEle = inputStream.split('\n')
        for ele in arrEle:
            arrParams = ele.split('=')
            if(arrParams[0].lower() == 'id'):
                osname = arrParams[1]
                while('"' in osname):
                    osname = osname.replace('"', '')
            elif(arrParams[0].lower() == 'version_id'):
                osStrVersion = arrParams[1]
                while('"' in osStrVersion):
                    osStrVersion = osStrVersion.replace('"', '')
                osversion = osStrVersion
        return osname + ' ' + osversion
    return ''

# parse os V2 cent6
# CentOS release 6.10 (Final)
# LSB_VERSION=base-4.0-amd64:base-4.0-noarch:core-4.0-amd64:core-4.0-noarch:graphics-4.0-amd64:graphics-4.0-noarch:printing-4.0-amd64:printing-4.0-noarch
# CentOS release 6.10 (Final)
# CentOS release 6.10 (Final)
def extractOsnameV2Os6(inputStream):
    if(inputStream != ""):
        centos = re.search('CentOS release (.+?)\(Final\)', inputStream)
        if centos:
            version = centos.group(1).split('.')[0]
            return 'centos ' + version
    return ''


# export object excel file (list cac dictionary)
# object {'ip', 'memcache: ', 'resize: ', 'cpu: ', 'ram : ', 'os : ', 'jdk.version : ', 'jzcommonx.version : ', 'description : '}
def exportDataToExcel(pathFileExcel, objData):
    workbook = xlsxwriter.Workbook(pathFileExcel)
    worksheet = workbook.add_worksheet()

    # write header
    worksheet.write_string('A1', 'IP')
    worksheet.write_string('B1', 'Memcache')
    worksheet.write_string('C1', 'Resize')
    worksheet.write_string('D1', 'CPU')
    worksheet.write_string('E1', 'RAM')
    worksheet.write_string('F1', 'OS')
    worksheet.write_string('G1', 'jdk.version')
    worksheet.write_string('H1', 'jzcommonx.version')
    worksheet.write_string('I1', 'Description')

    # write_data
    row = 1
    col = 0
    for server in objData :
        worksheet.write_string(row, col, server['ip'])
        worksheet.write_string(row, col + 1, server['memcache'])
        worksheet.write_string(row, col + 2, server['resize'])
        worksheet.write_number(row, col + 3, server['cpu'])
        worksheet.write_number(row, col + 4, server['ram'])
        worksheet.write_string(row, col + 5, server['os'])
        worksheet.write_string(row, col + 6, server['jdk'])
        worksheet.write_string(row, col + 7, server['jzcommon'])
        worksheet.write_string(row, col + 8, server['description'])
        row += 1
    workbook.close()


# get data list server
def getListServerInfo(listIp):
    listServer = []
    for ip in listIp:
        server = {}
        server['ip'] = ip

        sshClient = getConnection(ip)

        if(sshClient is not None):
            # get os name
            osStream = getOutputStreamFromServer(sshClient, 'lsb_release -a')
            server['os'] = extractOsname(osStream)
            if(server['os'] == ''):
                osStream = getOutputStreamFromServer(sshClient, 'cat /etc/*-release')
                server['os'] = extractOsnameV2(osStream)

            # get cpu
            cpuStream = getOutputStreamFromServer(sshClient, "grep -m 1 'cpu cores' /proc/cpuinfo")
            server['cpu'] = extractCpuInfo(cpuStream)

            # get ram
            ramStream = getOutputStreamFromServer(sshClient, "grep -m 1 'MemTotal' /proc/meminfo")
            server['ram'] = extractMemInfo(ramStream)

            # get jdk.version
            jdkStream = getOutputStreamFromServer(sshClient, "ls -l /zserver/java")
            server['jdk'] = extractJdkVersionV2(jdkStream)

            # get jzcommon
            jzcommonStream = getOutputStreamFromServer(sshClient, "ls  /zserver/lib/zx")
            server['jzcommon'] = extractJzcommon(jzcommonStream)

            # get memcache
            memcacheStream = getOutputStreamFromServer(sshClient, "ls -l /zserver/memcached")
            server['memcache'] = extractMemcache(memcacheStream)
            # get resize
            resizeStream = getOutputStreamFromServer(sshClient, "ls -l /zserver/lib/libJMagick.so")
            server['resize'] = extractResize(resizeStream)

            server['description'] = ''
            listServer.append(server)
            sshClient.close()
    return listServer


# extractCpuInfo('b\'cpu cores\t: 4\n\'')

# extractJdkVersion("b'lrwxrwxrwx 1 root root 30 Th05 14 14:42 /zserver/java/jdk -> /zserver/java/jdk1.8.0_162-x64\n'")

# extractJzcommon("b'libjemalloc-4.2.0.so\nlibjffi-1.2.so\nlibJZCommonX-1.2.0.2.so\nlibJZCommonX-1.2.0.3.so\nlibJZCommonX-1.2.0.4.so\nlibJZCommonX-1.2.0.5.so\nlibJZCommonX-1.2.0.6.so\nlibJZCommonX-1.2.0.7.so\nlibJZCommonX-1.2.0.8.so\nlibJZCommonX-1.2.0.9.so\nlibJZCommonX-1.2.1.0.so\nlibJZCommonX-1.2.1.1.so\nlibJZCommonX-1.2.1.2.so\nlibJZCommonX-1.2.1.3.so\nlibJZCommonX-1.2.1.4.so\nlibKcdbX-1.0.0.0.so\nlibZCommonX-1.2.0.3.so\nlibZCommonX-1.2.0.4.so\nlibZCommonX-1.2.0.5.so\nlibZCommonX-1.2.0.6.so\nlibZCommonX-1.2.0.7.so\nlibZCommonX-1.2.0.8.so\nlibZCommonX-1.2.0.9.so\nlibZCommonX-1.2.1.0.so\nlibZCommonX-1.2.1.1.so\nlibZCommonX-1.2.1.2.so\nlibZCommonX-1.2.1.3.so\nlibZCommonX-1.2.1.4.so\nlibZiCacheX-1.2.0.3.so\nlibZiCacheX-1.2.0.4.so\nlibZiCacheX-1.2.0.5.so\nlibZiCacheX-1.2.0.6.so\nlibZiCacheX-1.2.0.7.so\nlibZiCacheX-1.2.0.8.so\n'")

# extractOsname("b'DISTRIB_ID=Ubuntu\nDISTRIB_RELEASE=16.04\nDISTRIB_CODENAME=xenial\nDISTRIB_DESCRIPTION=\"Ubuntu 16.04.5 LTS\"\nNAME=\"Ubuntu\"\nVERSION=\"16.04.5 LTS (Xenial Xerus)\"\nID=ubuntu\nID_LIKE=debian\nPRETTY_NAME=\"Ubuntu 16.04.5 LTS\"\nVERSION_ID=\"16.04\"\nHOME_URL=\"http://www.ubuntu.com/\"\nSUPPORT_URL=\"http://help.ubuntu.com/\"\nBUG_REPORT_URL=\"http://bugs.launchpad.net/ubuntu/\"\nVERSION_CODENAME=xenial\nUBUNTU_CODENAME=xenial\n'")

# osstream = '''
# CentOS Linux release 7.4.1708 (Core) 
# NAME="CentOS Linux"
# VERSION="7 (Core)"
# ID="centos"
# ID_LIKE="rhel fedora"
# VERSION_ID="7"
# PRETTY_NAME="CentOS Linux 7 (Core)"
# ANSI_COLOR="0;31"
# CPE_NAME="cpe:/o:centos:centos:7"
# HOME_URL="https://www.centos.org/"
# BUG_REPORT_URL="https://bugs.centos.org/"

# CENTOS_MANTISBT_PROJECT="CentOS-7"
# CENTOS_MANTISBT_PROJECT_VERSION="7"
# REDHAT_SUPPORT_PRODUCT="centos"
# REDHAT_SUPPORT_PRODUCT_VERSION="7"

# CentOS Linux release 7.4.1708 (Core) 
# CentOS Linux release 7.4.1708 (Core)
# '''
# osstream = '''
# CentOS release 6.10 (Final)
# LSB_VERSION=base-4.0-amd64:base-4.0-noarch:core-4.0-amd64:core-4.0-noarch:graphics-4.0-amd64:graphics-4.0-noarch:printing-4.0-amd64:printing-4.0-noarch
# CentOS release 6.10 (Final)
# CentOS release 6.10 (Final)
# '''

#print(extractOsnameV2(osstring))

# jdkstring = '''
# total 335388
# drwxrwxrwx  9 root    root         4096 Mar  2  2011 apache-activemq-5.4.2
# drwxrwxrwx  6 root    root         4096 Dec 20  2010 apache-ant-1.8.2
# drwxrwxrwx 10 root    root         4096 Dec 12  2011 apache-tomcat-7.0.8
# drwxrwxrwx  9 root    root         4096 Mar  2  2011 axis2-1.5.4
# lrwxrwxrwx  1 root    root           11 Nov 17  2015 jdk -> jdk1.6.0_31
# lrwxrwxrwx  1 root    root           11 Nov 17  2015 jdk1.6.0 -> jdk1.6.0_31
# drwxrwxrwx  9 zdeploy es_user      4096 Nov 17  2015 jdk1.6.0_31
# drwxrwxrwx 10 zdeploy es_user      4096 Jun 27  2011 jdk1.7.0
# drwxrwxrwx  8 zdeploy es_user      4096 Oct  8  2013 jdk1.7.0_45-x64
# drwxrwxrwx  8 zdeploy es_user      4096 Dec 19  2013 jdk1.7.0_51-x64
# drwxr-xr-x  8 uucp        143      4096 Apr 11  2015 jdk1.7.0_80
# -rw-rw-r--  1    1000    1000 153530841 Feb 10  2018 jdk1.7.0_80-x64.tar.gz
# -rw-rw-r--  1    1000    1000 189815615 Mar  5  2018 jdk1.8.0_1062-x64.tar.gz
# drwxrwxrwx  8 uucp        143      4096 Jun 17  2014 jdk1.8.0_11-x64
# drwxr-xr-x  8 uucp        143      4096 Mar 15  2017 jdk1.8.0_131
# drwxrwxrwx 17 root    root        12288 Jan 19  2018 lib
# -rwxrwxrwx  1 root    root          199 Jun  7  2012 link
# -rwxrwxrwx  1 root    root          234 Jun  7  2012 set_env
# -rwxrwxrwx  1 zdeploy es_user       440 Feb 25  2014 set_env.cmd
# -rwxrwxrwx  1 zdeploy es_user       369 Feb 25  2014 set_env_jdk7.cmd
# drwxrwxrwx 10 root    root         4096 Dec 12  2011 zookeeper-3.3.2
# '''

# main:
listIp = getListIp('list_ip_test')
listServer = getListServerInfo(listIp)
for server in listServer:
    print(server)
exportDataToExcel('server_data.xlsx', listServer)
