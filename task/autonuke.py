import discord
import sqlite3
from discord.ext import tasks, commands
from utils import logs_admin


class autonuke_lops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cont = 0
        self.intervalor_uma_hora.start()
        self.intervalo_tres_horas.start()
        self.intervalo_seis_horas.start()
        self.intervalo_doze_horas.start()
        self.intervalo_vinte_horas.start()
        super().__init__()

    async def loops(self, intervalo):
                try:
                    for guild in self.bot.guilds:
                        con = sqlite3.connect('database.db')
                        cur = con.cursor()
                        cur.execute('''CREATE TABLE IF NOT EXISTS autonuke_config (
                                    servidor_id INTEGER PRIMARY KEY,
                                    intervalo INTEGER,
                                    status BOOLEAN DEFAULT 0,
                                    canais_id TEXT
                                    )''')
                    
                        cur.execute("SELECT * FROM autonuke_config WHERE servidor_id=?", (guild.id,))
                        server_db = cur.fetchall()

                        if not server_db:
                            cur.execute("INSERT INTO autonuke_config (servidor_id) VALUES (?)", (guild.id,))
                            con.commit()
                            con.close()
                        elif server_db[0][2] == 0:
                            None
                        else: 
                            if server_db[0][1] == intervalo:
                                canais = server_db[0][3].split(',')
                                canal_substituido = ''
                                cont = 0
                                for canal_id in canais:
                                    canal_original = self.bot.get_channel(int(canal_id))

                                    if canal_original:
                                        categoria = canal_original.category
                                        novo_canal = await canal_original.clone()
                                        nova_posicao = canal_original.position
                                        
                                        if len(canais) >= 1:
                                             cont += 1
                                             if cont - len(canais) + 1 == 0:
                                                  canal_substituido += str(novo_canal.id)
                                             else:
                                                  canal_substituido += ',' +  str(novo_canal.id)
                                        else:
                                             canal_substituido += str(novo_canal.id)
                                        await canal_original.delete()
                                        await novo_canal.edit(category=categoria, position=nova_posicao)
                                        await novo_canal.send('> `✔` - **Canal nukado pelo sistema de AutoNuke**')
                                    else: 
                                        cur.execute("UPDATE autonuke_config SET status = 0 WHERE servidor_id = ?", (guild.id,))
                                        cur.execute("SELECT canais_id FROM autonuke_config WHERE servidor_id = ?", (guild.id,))
                                        con.commit()
                                    
                                    cur.execute("UPDATE autonuke_config SET canais_id = ? WHERE servidor_id = ?", (canal_substituido,guild.id,))
                                    con.commit()
                        con.close()            
                    con.close()
                except Exception as er:
                     logs = logs_admin.logs(f'[Task] - Autonuke erro:\n> ```{er}```')
                     await logs.enviar_logs()

    @tasks.loop(hours=1)
    async def intervalor_uma_hora(self):
         if self.cont == 5:
            await self.loops(1)
         else:
              self.cont += 1

    @tasks.loop(hours=3)
    async def intervalo_tres_horas(self):
         if self.cont == 5:
            await self.loops(3)
         else:
              self.cont += 1

    @tasks.loop(hours=6)
    async def intervalo_seis_horas(self):
         if self.cont == 5:
            await self.loops(6)
         else:
            self.cont += 1

    @tasks.loop(hours=12)
    async def intervalo_doze_horas(self):
         if self.cont == 5:
            await self.loops(3)
         else:
            self.cont += 1

    @tasks.loop(hours=24)
    async def intervalo_vinte_horas(self):
         if self.cont == 5:
            await self.loops(3)
         else:
            self.cont += 1




async def setup(bot):
    await bot.add_cog(autonuke_lops(bot))
