import mysql.connector
config = {
  'user':"avnadmin",
  'host':"mysql-aarogyam-aarogyam-001.k.aivencloud.com",
  'password':"AVNS_FqqBlZreUbayKVxj31T",
  'port': "13073",
  'database': "Aarogyam"
}
def connection():
  try:
    conn_obj = mysql.connector.connect(**config)
    print("Connected to the database successfully!")
    return conn_obj
  
  except mysql.connector.Error as err:
    print(f"ERROR : {err}")


# conn = connection()
# cursor = conn.cursor()
# cursor.execute("""SELECT name,plan from person""")
# results = cursor.fetchall()
# for row in results:
#   print(f"Name : {row[0]} , Plan : {row[1]}")
# cursor.close()
# conn.close()