import pymysql

print("MySQL test")

connection = pymysql.connect(
    host="localhost",
    db="dkim",
    user="root",
    password="1234",
    charset="utf8",
    cursorclass=pymysql.cursors.DictCursor
)

sql = "SELECT * FROM tb1"
cursor = connection.cursor()
cursor.execute(sql)
players = cursor.fetchall()

cursor.close()
connection.close()

for i in players:
    print(i["name"])