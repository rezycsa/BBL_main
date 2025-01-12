import os
import sqlite3

db = os.path.join(os.path.dirname(__file__), 'Database', 'database.db' )

con = sqlite3.connect(db)
cur = con.cursor()
cur.execute("SELECT * FROM StatusRoleSystem WHERE server_id=?", ('1324297903707258880', ))
resultado = cur.fetchone()

if resultado is None:
 print('nao existe ')


con.close()

print(resultado)
