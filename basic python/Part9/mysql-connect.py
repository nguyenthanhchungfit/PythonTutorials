# pip install MYSQL-python
# pip install pymysql
import pymysql
dbcon = None
try:
    dbcon = pymysql.connect(host='localhost', user='root', passwd='', db='thegioididong', charset='utf8')

except pymysql.Error as e:
    print("Error %d: %s" % (e.args[0],e.args[1]))
    SystemExit(1)
    #sys.exit(1)
if dbcon:
    cur = dbcon.cursor()
    cur.execute("SELECT VERSION()")
    ver = cur.fetchone()
    print("Database version : %s " %ver)





