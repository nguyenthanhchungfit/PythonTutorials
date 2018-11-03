import xlsxwriter
import paramiko
import re

MD5_VAL = 'c3afbc59b1318552bab9a4b570656de7'

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


# extract list scribe is running
#root      3496     1  0 Sep23 ?        00:04:45 /zserver/scribe/zcribe -c /zserver/scribe/scribe_1460.conf
#root      3513     1  0 Sep23 ?        00:05:43 /zserver/scribe/zcribe -c /zserver/scribe/scribe_1464.conf
#root      3529     1  0 Sep23 ?        00:00:08 /zserver/scribe/zcribe -c /zserver/scribe/scribe_1465.conf
#root      3541     1  0 Sep23 ?        00:00:07 /zserver/scribe/zcribe -c /zserver/scribe/scribe_1466.conf
#root      3568     1  0 Sep23 ?        00:00:07 /zserver/scribe/zcribe -c /zserver/scribe/scribe_1467.conf
#root      3615     1  0 Sep23 ?        00:04:19 /zserver/scribe/zcribe -c /zserver/scribe/scribe_1473.conf
#root      3668     1  0 Sep23 ?        00:02:05 /zserver/scribe/zcribe -c /zserver/scribe/scribe_1573.conf
#root      3783     1  0 Sep23 ?        00:00:07 /zserver/scribe/zcribe -c /zserver/scribe/scribe_1563.conf
#root      4016     1  0 Sep23 ?        00:00:07 /zserver/scribe/zcribe -c /zserver/scribe/scribe_1470.conf
#zdeploy  61588 61587  0 08:02 ?        00:00:00 bash -c ps -ef|grep /zserver/scribe/
#zdeploy  61608 61588  0 08:02 ?        00:00:00 grep /zserver/scribe/
#
def extractListRunningScribe(inputStream):
    list_scribe = []
    if(inputStream != ""):
        arrEle = inputStream.split("\n")
        for ele in arrEle:
            while("  " in ele):
                ele = ele.replace("  ", " ")
            arrParams = ele.split(" ")
            if(len(arrParams) == 10):
                if(arrParams[9].endswith('.conf')):
                    list_scribe.append(arrParams[9])
    return list_scribe


def extractMd5(inputStream):
    if(inputStream != ""):
        return inputStream.split(' ')[0]
    return ''

def extractTotalScribe(inputStream):
    list_scribe = []
    if(inputStream != ""):
        arrEle = inputStream.split('\n')
        for ele in arrEle:
            while '  ' in ele:
                ele = ele.replace("  ", " ")
            arrParam = ele.split(" ")
            if(len(arrParam) == 9):
                if(arrParam[8].endswith('.conf')):
                    hasPort = re.search('_(\d+)\.', arrParam[8])
                    if(hasPort):
                        list_scribe.append(arrParam[8])
    return list_scribe

def parseDataToDictionary(inputStream):
    dataMap = {}
    if(inputStream != ""):
        arrEle = inputStream.split('\n')
        for ele in arrEle:
            if(ele != ""):
                arrParam = ele.split('=')  
                if(len(arrParam) == 2): 
                    dataMap[arrParam[0]] = arrParam[1]
    return dataMap

def extractInfoScribe(inputStream):
    mapPrimary = {}
    if(inputStream != ''):
        strBegin = "<primary>"
        strEnd = "</primary>"
        posBegin = inputStream.find(strBegin)
        posEnd = inputStream.find(strEnd)
        if(posBegin >= 0 and posEnd > (posBegin + len(strBegin))):
            dataPrimary = inputStream[posBegin + len(strBegin) : posEnd]
            mapPrimary = parseDataToDictionary(dataPrimary)
    listKeys = mapPrimary.keys()
    res_remote_host = ''
    res_remote_port = '0'
    res_log_bin = 'old'
    res_write_type = 'syn'
    if('remote_host' in listKeys):
        res_remote_host = mapPrimary['remote_host']
        if('remote_port' in listKeys):
            res_remote_port = mapPrimary['remote_port']
        if('log_bin_format' in listKeys):
            res_log_bin = mapPrimary['log_bin_format']
        if('write_type' in listKeys):
            res_write_type = mapPrimary['write_type']
    else:
        res_remote_port = res_log_bin = res_write_type = ''
    return res_remote_host, res_remote_port, res_log_bin, res_write_type

# get List Result
def getListServerRes(listIp):
    listServerRes = []
    for ip in listIp:
        if(ip != ''):
            serverRes = {}
            serverRes['ip'] = ip
            sshClient = getConnection(ip)
            if(sshClient):
                ## get md5 code
                md5Stream = getOutputStreamFromServer(sshClient, 'md5sum /zserver/scribe/zcribe')
                md5Code = extractMd5(md5Stream)
                if(md5Code == MD5_VAL):
                    serverRes['version'] = 'latest'
                else:
                    serverRes['version'] = 'old'

                ## get list all scribe
                listRunningScribeStream = getOutputStreamFromServer(sshClient, 'ps -ef|grep /zserver/scribe/') 
                listRunningScribe = extractListRunningScribe(listRunningScribeStream)
                ## get list all scribe
                listAllScribeStream = getOutputStreamFromServer(sshClient, 'ls -l /zserver/scribe/')
                listAllScribe = extractTotalScribe(listAllScribeStream)

                listScribe = []
                for scribe in listAllScribe:
                    dicScribe = {}
                    print('   >>> current scribe: ' + scribe)
                    fullScribe = '/zserver/scribe/' + scribe
                    infoScribeStream = getOutputStreamFromServer(sshClient, 'cat ' + fullScribe)
                    remote_host, remote_port, log_bin, write_type = extractInfoScribe(infoScribeStream)
                    dicScribe['remote_host'] = remote_host
                    dicScribe['remote_port'] = remote_port
                    dicScribe['log_bin'] = log_bin
                    dicScribe['write_type'] = write_type
                    port = '0'
                    status = 'stopped'
                    hasPort = re.search('_(\d+)\.', scribe)
                    if(hasPort):
                        port = hasPort.group(1)
                    if(fullScribe in listRunningScribe):
                        status = 'running'
                
                    dicScribe['scribe_agent'] = port + ',' + status

                    listScribe.append(dicScribe)
                serverRes['list_scribe'] = listScribe
                sshClient.close()
            listServerRes.append(serverRes)
    return listServerRes

def exportDataToExcel(path_file_name, listServerRes):
    total = 0
    workbook = xlsxwriter.Workbook(path_file_name)
    worksheet = workbook.add_worksheet()

    # write header
    worksheet.write_string('A1', 'IP')
    worksheet.write_string('B1', 'Version')
    worksheet.write_string('C1', 'Scribe Agent')
    worksheet.write_string('D1', 'Remote host')
    worksheet.write_string('E1', 'Remote port')
    worksheet.write_string('F1', 'Log bin')
    worksheet.write_string('G1', 'Write type')

    worksheet.set_column(0, 3, 20)
    worksheet.set_column(1, 1, 10)
    worksheet.set_column(4, 6, 10)
    # Create a format to use in the merged range.
    merge_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter'
        })

    row = 1
    col = 2
    for serverRes in listServerRes:
        total = total + 1
        old_row = row
        ip = serverRes['ip']
        version = ''
        if('version' in serverRes.keys()):
            version = serverRes['version']
        if('list_scribe' in serverRes.keys()):
            listScribe = serverRes['list_scribe']
            for scribe in listScribe:
                worksheet.write_string(row, col, scribe['scribe_agent'])
                worksheet.write_string(row, col + 1, scribe['remote_host'])
                worksheet.write_string(row, col + 2, scribe['remote_port'])
                worksheet.write_string(row, col + 3, scribe['log_bin'])
                worksheet.write_string(row, col + 4, scribe['write_type'])
                row = row+1
        if(old_row == row):
            row = row + 1
        rangeTopA = 'A' + str(old_row + 1)
        rangeBottomA = 'A' + str(row)
        rangeA = rangeTopA + ':' + rangeBottomA
        rangeTopB = 'B' + str(old_row + 1)
        rangeBottomB = 'B' + str(row)
        rangeB = rangeTopB + ':' + rangeBottomB
        worksheet.merge_range(rangeA, ip, merge_format)
        worksheet.merge_range(rangeB, version, merge_format)

    workbook.close()
    return total

# obj   
#[{
# 'ip' : ''.
# 'version' : ''
# 'list_scribe' : [
    #   {
        #    'scribe agent' : '1460, running',
        #    'remote_host' : '',
        #    'remote_port' : ,
        #    'log_bin' : '',
        #    'write_type' : ''
    #   }
# ]
# }]

# main
listIp = getListIp('list_ip_test')
listServerRes = getListServerRes(listIp)
total = exportDataToExcel('data_export.xlsx', listServerRes)
print('\n\n************ Done!! Total: ' + str(total) + "****************\n\n")


