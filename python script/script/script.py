import xlsxwriter
import math
import paramiko

# connect to server and get outputstream
def getOutputStreamFromServer(ip, cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('127.0.0.1', password='thanhCHUNG')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=2)
    res = stdout.read()
    ssh.close()
    #print ("ssh succuessful. Closing connection")
    return res.decode('utf-8')
    

# get Ip from text file
def getListIp(pathFile):
    f1 = open(pathFile, 'r', encoding='utf-8')
    data = f1.read()
    arr = data.split('\n')
    return arr


# parseOutputStream to useful data
# parse ram : #b'MemTotal:       16367992 kB\n'
def extractMemInfo(inputStream):
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

# parse cpu : #b'cpu cores\t: 4\n'
def extractCpuInfo(inputStream):
    lenStr= len(inputStream)
    strContent = inputStream[0: lenStr - 1]
    while("  " in strContent):
        strContent = strContent.replace("  ", " ")
    strContent = strContent.replace('\t', '')
    cpu = 0
    params = strContent.split(':')
    cpu = int(params[1])
    return cpu

# parse jdk.version
# b'lrwxrwxrwx 1 root root 30 Th05 14 14:42 /zserver/java/jdk -> /zserver/java/jdk1.8.0_162-x64\n'
def extractJdkVersion(inputStream):
    ind = inputStream.rfind("->")
    res = ""
    if(ind >= 0):
        strLib = inputStream[ind + 3 : len(inputStream) - 1]
        indJdk = strLib.find('jdk')
        if(indJdk >= 0):
            res = strLib[indJdk + 3 : ]
    return res
    
    
# parse jzcommon
#b'libjemalloc-4.2.0.so\n
# libjffi-1.2.so\n
# libJZCommonX-1.2.0.2.so\n
# libJZCommonX-1.2.0.3.so\n
# libJZCommonX-1.2.0.4.so\n
# libJZCommonX-1.2.0.5.so\n
# libJZCommonX-1.2.0.6.so\n
# libJZCommonX-1.2.0.7.so\n
# libJZCommonX-1.2.0.8.so\n
# libJZCommonX-1.2.0.9.so\n
# libJZCommonX-1.2.1.0.so\n
# libJZCommonX-1.2.1.1.so\n
# libJZCommonX-1.2.1.2.so\n
# libJZCommonX-1.2.1.3.so\n
# libJZCommonX-1.2.1.4.so\n
# libKcdbX-1.0.0.0.so\n
# libZCommonX-1.2.0.3.so\n
# libZCommonX-1.2.0.4.so\n
# libZCommonX-1.2.0.5.so\n
# libZCommonX-1.2.0.6.so\n
# libZCommonX-1.2.0.7.so\n
# libZCommonX-1.2.0.8.so\n
# libZCommonX-1.2.0.9.so\n
# libZCommonX-1.2.1.0.so\n
# libZCommonX-1.2.1.1.so\n
# libZCommonX-1.2.1.2.so\n
# libZCommonX-1.2.1.3.so\n
# libZCommonX-1.2.1.4.so\n
# libZiCacheX-1.2.0.3.so\n
# libZiCacheX-1.2.0.4.so\n
# libZiCacheX-1.2.0.5.so\n
# libZiCacheX-1.2.0.6.so\n
# libZiCacheX-1.2.0.7.so\n
# libZiCacheX-1.2.0.8.so\n'
def extractJzcommon(inputStream):
    arrLib = inputStream.split('\n')
    arrLibJz = []
    for item in arrLib:
        if("libJZCommonX" in item):
            item = item.replace("libJZCommonX", "")
            item = item.replace("-", "")
            item = item.replace(".so", "")
            arrLibJz.append(item)
    return max(arrLibJz)
    #print(arrLib)
# parse memcache
# 
# 
# parse resize
# 
# parse os
# b'DISTRIB_ID=Ubuntu\n
# DISTRIB_RELEASE=16.04\n
# DISTRIB_CODENAME=xenial\n
# DISTRIB_DESCRIPTION="Ubuntu 16.04.5 LTS"\n
# NAME="Ubuntu"\n
# VERSION="16.04.5 LTS (Xenial Xerus)"\n
# ID=ubuntu\n
# ID_LIKE=debian\n
# PRETTY_NAME="Ubuntu 16.04.5 LTS"\n
# VERSION_ID="16.04"\n
# HOME_URL="http://www.ubuntu.com/"\n
# SUPPORT_URL="http://help.ubuntu.com/"\n
# BUG_REPORT_URL="http://bugs.launchpad.net/ubuntu/"\n
# VERSION_CODENAME=xenial\n
# UBUNTU_CODENAME=xenial\n'
def extractOsname(inputStream):
    arrEle = inputStream[2: len(inputStream) - 1].split('\n')
    for ele in arrEle:
        print(ele)
# 

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
    # for ip in listIp:
    #     print(ip)
    
    server = {}
    server['ip'] = '127.0.0.1'
    ip = ''
    # get os name
    # osStream = getOutputStreamFromServer(ip, '')
    server['os'] = 1

    # get cpu
    cpuStream = getOutputStreamFromServer(ip, "grep -m 1 'cpu cores' /proc/cpuinfo")
    server['cpu'] = extractCpuInfo(cpuStream)

    # get ram
    ramStream = getOutputStreamFromServer(ip, "grep -m 1 'MemTotal' /proc/meminfo")
    server['ram'] = extractMemInfo(ramStream)

    # get jdk.version
    jdkStream = getOutputStreamFromServer(ip, "ls -l /zserver/java/jdk")
    server['jdk'] = extractJdkVersion(jdkStream)

    # get jzcommon
    jzcommonStream = getOutputStreamFromServer(ip, "ls  /zserver/lib/zx")
    server['jzcommon'] = extractJzcommon(jzcommonStream)

    # get memcache
    server['memcache'] = 1
    # get resize
    server['resize'] = ''

    server['description'] = ''
    listServer.append(server)
    print(listServer)
# arrIp = getListIp('list_ip')
# print(len(arrIp))
# print(arrIp)



objData = [
    {'ip' :  '12.19.44.12', 'memcache' : 'ready', 'resize' : 'not ready', 'cpu' : 32, 'ram' : 64, 'os' : 'centos 7', 'jdk' : '1.2.1.2', 'jzcommon' : '1.3.1.2', 'description' : ''},
    {'ip' :  '12.19.44.20', 'memcache' : 'not ready', 'resize' : 'not ready', 'cpu' : 64, 'ram' : 128, 'os' : 'centos 7', 'jdk' : '1.2.1.2', 'jzcommon' : '1.3.1.2', 'description' : ''}
]
#exportDataToExcel('server_data.xlsx', objData)


# extractCpuInfo('b\'cpu cores\t: 4\n\'')

# extractJdkVersion("b'lrwxrwxrwx 1 root root 30 Th05 14 14:42 /zserver/java/jdk -> /zserver/java/jdk1.8.0_162-x64\n'")

# extractJzcommon("b'libjemalloc-4.2.0.so\nlibjffi-1.2.so\nlibJZCommonX-1.2.0.2.so\nlibJZCommonX-1.2.0.3.so\nlibJZCommonX-1.2.0.4.so\nlibJZCommonX-1.2.0.5.so\nlibJZCommonX-1.2.0.6.so\nlibJZCommonX-1.2.0.7.so\nlibJZCommonX-1.2.0.8.so\nlibJZCommonX-1.2.0.9.so\nlibJZCommonX-1.2.1.0.so\nlibJZCommonX-1.2.1.1.so\nlibJZCommonX-1.2.1.2.so\nlibJZCommonX-1.2.1.3.so\nlibJZCommonX-1.2.1.4.so\nlibKcdbX-1.0.0.0.so\nlibZCommonX-1.2.0.3.so\nlibZCommonX-1.2.0.4.so\nlibZCommonX-1.2.0.5.so\nlibZCommonX-1.2.0.6.so\nlibZCommonX-1.2.0.7.so\nlibZCommonX-1.2.0.8.so\nlibZCommonX-1.2.0.9.so\nlibZCommonX-1.2.1.0.so\nlibZCommonX-1.2.1.1.so\nlibZCommonX-1.2.1.2.so\nlibZCommonX-1.2.1.3.so\nlibZCommonX-1.2.1.4.so\nlibZiCacheX-1.2.0.3.so\nlibZiCacheX-1.2.0.4.so\nlibZiCacheX-1.2.0.5.so\nlibZiCacheX-1.2.0.6.so\nlibZiCacheX-1.2.0.7.so\nlibZiCacheX-1.2.0.8.so\n'")

# extractOsname("b'DISTRIB_ID=Ubuntu\nDISTRIB_RELEASE=16.04\nDISTRIB_CODENAME=xenial\nDISTRIB_DESCRIPTION=\"Ubuntu 16.04.5 LTS\"\nNAME=\"Ubuntu\"\nVERSION=\"16.04.5 LTS (Xenial Xerus)\"\nID=ubuntu\nID_LIKE=debian\nPRETTY_NAME=\"Ubuntu 16.04.5 LTS\"\nVERSION_ID=\"16.04\"\nHOME_URL=\"http://www.ubuntu.com/\"\nSUPPORT_URL=\"http://help.ubuntu.com/\"\nBUG_REPORT_URL=\"http://bugs.launchpad.net/ubuntu/\"\nVERSION_CODENAME=xenial\nUBUNTU_CODENAME=xenial\n'")


# main
listIp = getListIp('list_ip')
getListServerInfo(listIp)