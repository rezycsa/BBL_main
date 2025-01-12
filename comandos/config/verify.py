import discord
import sqlite3
from discord.ext import commands
from discord import app_commands, Button, ButtonStyle
class verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(description='Configure o sistema de verificaçao atraves do auth')
    async def config_auth(self, interaction: discord.Interaction):
            #incia db
            con = sqlite3.connect('database.db')
            cur = con.cursor()        
            cur.execute("SELECT * FROM usuarios WHERE id=?", (interaction.user.id,))
            user_db = cur.fetchall()

            if user_db[0][2] == None:
                view = discord.ui.View()
                url_dash = discord.ui.Button(label='🔗', url='https://google.com')
                view.add_item(url_dash)

                await interaction.response.send_message(
                    content='> **`❌` - Para utilizar esse sistema voce deve ter seu registro completo, voce pode fazer isso clicando abaixo.**',
                    ephemeral=True,
                    view=view)

async def setup(bot):
     await bot.add_cog(verify(bot))