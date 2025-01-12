import discord
import sqlite3
import os 
from discord.ext import commands
from utils import logs_admin
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Database', 'database.db') #caminho da db

class intecao_feita(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        try:
            con = sqlite3.connect(db_path)
            cur = con.cursor()        
            cur.execute("SELECT * FROM usuarios WHERE id=?", (interaction.user.id,))
            user_db = cur.fetchall()

            if not user_db:
                cur.execute("INSERT INTO usuarios (id) VALUES (?)", (interaction.user.id,))
                con.commit()
                con.close()

            elif user_db[0][5] == 1:
                await interaction.response.send_message(content='> **`❌` - Você foi impedido de utilizar o bot devido à sua inclusão em nossa `BLACKLIST`**.\n- *Se desejar contestar essa decisão, por favor, abra um `ticket em nosso servidor` de suporte.*', ephemeral=True)
                con.close()
                return
            
        except Exception as er:
                logs = logs_admin.logs(f'**Novo erro - Cogs_Eventos**\n ```{er}```')
                await logs.enviar_logs()
                con.close()

async def setup(bot):
    await bot.add_cog(intecao_feita(bot))