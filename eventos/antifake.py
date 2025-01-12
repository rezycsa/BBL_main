import discord
from discord.ext import commands
import sqlite3
import traceback
import os 
from datetime import datetime, timezone
from utils import embed
from dotenv import dotenv_values
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Database', 'database.db') #caminho da db

config = dotenv_values('.env')
icon_padrao =  'https://media.discordapp.net/attachments/1237961121714016349/1237961507099119696/image_2.png?ex=663d8cff&is=663c3b7f&hm=0a53fc41dce47a0ceb8d8b0dc9c6afd5d7551f904c32d6c47596bee7d8988878&=&format=webp&quality=lossless&width=373&height=350'

class AntiFake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            servidor_id = member.guild.id
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            cur.execute("SELECT * FROM AntiFakeSystem WHERE server_id=?", (servidor_id,))
            server_config = cur.fetchone()
            con.close()

            if not server_config:
                return

            if server_config[1] == 0:
                return

            created_at_utc = member.created_at.replace(tzinfo=timezone.utc)
            dias_desde_criacao = (datetime.utcnow().replace(tzinfo=timezone.utc) - created_at_utc).days

            if dias_desde_criacao < int(server_config[2]):

                if server_config[5] is not None:
                    canal_logs = member.guild.get_channel(int(server_config[5]))

                    if int(server_config[6]) == 0:
                        tipo_punicao = '> `Kick.`'
                    elif int(server_config[6]) == 1:
                        tipo_punicao = f'> `AutoRole`, (<@&{server_config[7]}>)'

                    if canal_logs:
                        embed_logs = discord.Embed(
                            title="Logs - AntiFake",
                        )
                        embed_logs.add_field(name='`👤` - Usuario: ', value=f'> **<@{member.id}>, (||{member.id}||)**', inline=False)
                        embed_logs.add_field(name='`📆` - Data de criaçao: ', value=f'> <t:{int(member.created_at.timestamp())}:F>', inline=False)
                        embed_logs.add_field(name='`🔨` - Puniçao: ', value=tipo_punicao, inline=False)
                        embed_logs.color = discord.Color(int(config['COR'].lstrip('#'), 16))
                        embed_logs.set_footer(text=f"{config['URL']} | Ajuda • {datetime.now().strftime('%d/%m/%Y %H:%M')}", icon_url=icon_padrao)
                        embed_logs.set_thumbnail(url=member.display_avatar)
                        await canal_logs.send(embed=embed_logs)

                if int(server_config[6]) == 0:                    
                    try:
                        embed_dm = discord.Embed(
                            title="Puniçao - AntiFake",
                            color=discord.Color(int(config['COR'].lstrip('#'), 16))
                        )
                        embed_dm.add_field(name='`🔗` - Servidor:', value=f'> **{member.guild.name}(||{member.guild.id}||)**', inline=False)
                        embed_dm.add_field(name='`📋` - Motivo:',    value=f'> **Sua conta é muito nova.**\n - **Ela deve ter pelo menos `{int(server_config[2])}` dias de criação.**', inline=False)
                        embed_dm.set_footer(text=f"{config['URL']} | Ajuda • {datetime.now().strftime('%d/%m/%Y %H:%M')}", icon_url=icon_padrao)
                        embed_dm.set_thumbnail(url=member.display_avatar)
                        await member.send(embed=embed_dm)
                    except discord.Forbidden:
                        None
                    await member.kick(reason="Proteçao - AntiFake")



                elif int(server_config[6]) == 1:
                    # AutoRole
                    cargo_autorole_id = server_config[7]
                    cargo_autorole = member.guild.get_role(int(cargo_autorole_id))
                    if cargo_autorole:
                        await member.add_roles(cargo_autorole, reason="Proteçao - AntiFake")
                    else:
                        return

        except Exception as e:
            print(traceback.format_exc())
            # Log de erro, se necessário

async def setup(bot):
    await bot.add_cog(AntiFake(bot))
