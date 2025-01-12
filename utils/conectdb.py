import os
import sqlite3

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Database', 'database.db')	

class consultar():
    def __init__(self, coluna, valor):
        self.coluna = coluna
        self.valor = valor
        
    async def consultar_server(self, salvar=True):
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute(f"SELECT * FROM {self.coluna} WHERE server_id=?", (self.valor, ))
        resultado_server = cur.fetchone()
        #verifica se o server ta registado na db caso nao esteja ele registra
        if not resultado_server and salvar == True:
            cur.execute(f"INSERT INTO {self.coluna} (server_id) VALUES (?)", (self.valor,))
            con.commit()
            cur.execute(f"SELECT * FROM {self.coluna} WHERE server_id=?", (self.valor,))
            resultado_server = cur.fetchone()
        con.close()
        

        return resultado_server
        
