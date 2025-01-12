import discord
import os 
import sqlite3
import traceback
from utils.embed import embed_padrao
from discord.ext import commands
from utils import logs_admin

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Database', 'database.db')

class BioCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        try:
            servidor_id = int(after.guild.id)
            
            #conecta na db
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            cur.execute("SELECT DISTINCT * FROM StatusRoleSystem WHERE server_id=?", (servidor_id,))
            server_db = cur.fetchone()
            con.close()

            #verfica o status do membros
            status_antigo_custum = next((activity for activity in before.activities if isinstance(activity, discord.CustomActivity)), None)
            status_novo_custum = next((activity for activity in after.activities if isinstance(activity, discord.CustomActivity)), None)
            #defini as vars do stt
            status_antigo = status_antigo_custum.state if status_antigo_custum else "Nenhum"
            status_novo = status_novo_custum.state if status_novo_custum else "Nenhum"

            #verfica se o server tem o sistema ativo
            if server_db is None:
                return
            
            if server_db[1] == 1:
                if str(status_novo) == str(server_db[3]):
                   role_list = server_db[2].split(',')

                   for role in role_list:
                       cargo = discord.utils.get(after.guild.roles, id=int(role))
                       await after.add_roles(cargo)

                   #envia as logs
                   if server_db[4] is not None:
                    try:
                        canal = discord.utils.get(after.guild.channels, id=int(server_db[4]))

                        cargos_add = '> '
                        for cargo in role_list:
                            if role != role_list[-1]:
                                cargos_add += f'<@&{cargo}>, '
                            else:
                                cargos_add += f'<@&{cargo}>'
                            

                        embed = discord.Embed(title=f'Sistema de Logs - Cargo por Status')
                        embed = await embed_padrao(embed, after.guild)
                        embed.add_field(name='`👤` - Usuario: ', value=f'> **<@{after.id}>, (||{after.id}||)**', inline=False)
                        embed.add_field(name='`🔑` - Cargos adicionado: ', value=cargos_add, inline=False)
                        embed.add_field(name='`💫` - Status antigo/novo: ', value=f'> **`{status_antigo}` --> `{status_novo}`**', inline=False)
                        
                        await canal.send(embed=embed)
                    except discord.Forbidden:
                        pass

                else:
                    if status_antigo == server_db[3]:
                        role_list = server_db[2].split(',')
                        
                        for role in role_list:
                            cargo = discord.utils.get(after.guild.roles, id=int(role))
                            await after.remove_roles(cargo)
                        #envia as logs
                        if server_db[4] is not None:
                            try:
                                canal = discord.utils.get(after.guild.channels, id=int(server_db[4]))
                        
                                cargos_remove = '> '

                                for cargo in role_list:
                                    if role != role_list[-1]:
                                        cargos_remove += f'<@&{cargo}>, '
                                    else:
                                        cargos_remove += f'<@&{cargo}>'

                                embed = discord.Embed(title=f'Sistema de Logs - Cargo por Status')
                                embed = await embed_padrao(embed, after.guild)
                                embed.add_field(name='`👤` - Usuario: ', value=f'> **<@{after.id}>, (||{after.id}||)**', inline=False)
                                embed.add_field(name='`🔑` - Cargos removido: ', value=cargos_remove, inline=False)
                                embed.add_field(name='`💫` - Status antigo/novo: ', value=f'> **`{status_antigo}` --> `{status_novo}`**', inline=False)
                                
                                await canal.send(embed=embed)
                            except discord.Forbidden:
                                pass                
                                 
        except Exception as error:
           if error == discord.MissingPermissions:
               pass
           else:
               print(traceback.format_exc())
               logs = logs_admin.logs(f'> **Novo erro - `cargo_por_status`**\n- ```{error}```')
               logs.enviar_logs()

        
            


async def setup(bot):
    await bot.add_cog(BioCheck(bot))