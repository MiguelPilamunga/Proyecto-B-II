import pymssql

server = 'localhost'
user = 'sa'
password = 'admin123'
database = 'master'
port = 1433

try:
    conn = pymssql.connect(server=server, user=user, password=password, database=database, port=port)
    cursor = conn.cursor()
    cursor.execute('SELECT @@version')
    row = cursor.fetchone()
    print(f"SQL Server Version: {row[0]}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
