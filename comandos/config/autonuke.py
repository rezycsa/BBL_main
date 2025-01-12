import discord
import sqlite3
import json
from discord.ext import commands
from discord import app_commands
from dotenv import dotenv_values
from utils import logs_admin
config = dotenv_values('.env')
open_emojis = dotenv_values('.env')


class autonuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description='Comando de configuraçao do sistema de AutoNuke.')
    async def config_autonuke(self, interact:discord.Interaction):
        try:
            servidor_id = int(interact.guild.id)
            if interact.guild.icon == None:
                server_icon = 'https://media.discordapp.net/attachments/1231298302020943882/1231739239775866950/communityIcon_1xjv62tivxy61.png?ex=66380d8f&is=6625988f&hm=d38c32959459a01cf4988cd97069f49fa5a8865faabbfc719e8f2c04d717fad9&=&format=webp&quality=lossless&width=350&height=350'
            else:
                server_icon = interact.guild.icon
            
            #sqlite
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS autonuke_config (
                        servidor_id INTEGER PRIMARY KEY,
                        intervalo INTEGER,
                        status BOOLEAN DEFAULT 0,
                        canais_id TEXT
                        )''')
            
            cur.execute("SELECT * FROM autonuke_config WHERE servidor_id=?", (servidor_id,))
            server_db = cur.fetchall()

            async def embed():
                if server_db[0][2] == 0:
                    Status = '> `Desativado`'
                else:
                    Status = '> `Ativado`'

                if server_db[0][1] == None:
                    intervalo = '> `Nao configurado.`'
                else:
                    intervalo = f'> `{server_db[0][1]} Horas.`'

                if server_db[0][3] ==  None or server_db[0][3] == '':
                    canais = '> `Nenhum canal definido.`'
                else: 
                    canais_cont = server_db[0][3].strip().split(',')
                    canais = ''
                    for cont in range(len(canais_cont)):
                        canais += f'> <#{canais_cont[cont]}>' + '\n'

                embed_status = discord.Embed(title='Config - Sistema de AutoNuke.', description='> O Sistema de Autonuke permite a exclusão automática de canais após um determinado período de tempo.')
                embed_status.set_thumbnail(url=server_icon)
                embed_status.add_field(name=f'`💫` - Status', value=Status)
                embed_status.add_field(name=f'`⏱` - Intervalor',value=intervalo)
                embed_status.add_field(name=f'`💭` - Canais:', value=canais, inline=False)
                embed_status.color = discord.Color(int(config['COR'].lstrip('#'), 16))
                return embed_status

            class botoes_config(discord.ui.View):
                def __init__(self, message):
                    super().__init__(timeout=160)
                    self.foo = None
                    self.message = message
                
                async def desativa_todos_botoes(self):
                    for item in self.children:
                        item.disabled = True
                    await self.message.edit_original_response(view=self, allowed_mentions=None)

                async def on_timeout(self):
                    await self.desativa_todos_botoes()
                    await self.message.edit_original_response(content=f'> `❌` - Tempo inspirado, voce demorou demais para responder.')
                    con.close()
                    
                class modal_canais(discord.ui.Modal):
                    def __init__(self, message):
                        self.message = message
                        super().__init__(title="Autonuke - Sistema de configuraçao")
                
                    canais_ids_modal = discord.ui.TextInput(label='Canais id:', placeholder='Use virgula pra separa os ids.')
                    async def on_submit(self, interaction:discord.Interaction):
                        canais_id_listados = str(self.canais_ids_modal).strip().replace(' ', '').split(',')
                        
                        if len(canais_id_listados) > 5:
                            await interaction.response.send_message(content=f'> `❌` - O maximo de canais permitido e 5.', ephemeral=True)
                        else:
                            try:
                                canais = ''
                                canais_msg = ''
                                for cont in range(0,len(canais_id_listados)):
                                    canais_list = interaction.guild.get_channel(int(canais_id_listados[cont]))
                                    if canais_list == None:
                                        await interaction.response.send_message(content=f'> `❌` - Um dos ids informado esta **Invalido.**', ephemeral=True)
                                        break
                                    if str(canais_list.type) == 'voice':
                                        await interaction.response.send_message(content=f'> `❌` - Um dos ids informado e uma **call.**', ephemeral=True)
                                        break
                                    if len(canais_id_listados) != len(set(canais_id_listados)):
                                        await interaction.response.send_message(content='> `❌` voce nao pode adicionar canais repetidos.', ephemeral=True)
                                        break


                                    if len(canais_id_listados) > 0:
                                        if cont + 1 - len(canais_id_listados) + 1 == 0:
                                            canais += canais_id_listados[cont] + ','
                                        else:
                                            canais += canais_id_listados[cont]
                                    else:
                                        canais = canais_id_listados[cont]

                                    canais_msg += f'- <#{canais_id_listados[cont]}>' + '\n'


                                cur.execute("UPDATE autonuke_config SET canais_id = ? WHERE servidor_id = ?", (canais,servidor_id,))
                                con.commit()
                                embed_status = await embed()
                                await self.message.edit_original_response(embed=embed_status)
                                print(self.message)
                                await interaction.response.send_message(content=f'> `✔` - canais definido com sucesso, os canais definido foram:\n {canais_msg}')

                            except ValueError:
                                await interaction.response.send_message(content=f'> `❌` - Voce deve digitar um id **valido.**\n - parece que voce incluiu algumas letra na sua resposta.', ephemeral=True)
                            
                @discord.ui.button(label='💫',style=discord.ButtonStyle.primary)
                async def status_bnt(self, interaction: discord.Interaction, button: discord.ui.Button):
                    cur.execute("SELECT * FROM autonuke_config WHERE servidor_id=?", (servidor_id,))
                    server_db = cur.fetchall()

                    if interaction.user.id != self.message.user.id:
                        await interaction.response.send_message(content=f'> `❌` - Somente quem realizou o comando deve reagir aos botoes.', ephemeral=True)
                    elif server_db[0][2] == 0:
                            if server_db[0][1] == None:
                                await interaction.response.send_message(content=f'> `❌` - Voce deve definir o intervalo antes de **`Ativar` o sistema.**', ephemeral=True)
                            elif server_db[0][3] == None:
                                await interaction.response.send_message(content=f'> `❌` - Voce deve definir os canais antes de **`Ativar` o sistema.**', ephemeral=True)
                            else:
                                cur.execute("UPDATE autonuke_config SET status = 1 WHERE servidor_id = ?", (servidor_id,))
                                con.commit()
                                await interaction.response.send_message(content=f'> `✔` - Sistema **`Ativado` com sucesso.**', ephemeral=True)
                                await self.desativa_todos_botoes()

                    else:
                            cur.execute("UPDATE autonuke_config SET status = 0 WHERE servidor_id = ?", (servidor_id,))
                            con.commit()
                            await interaction.response.send_message(content=f'> `✔` - Sistema **`Desativado` com sucesso.**', ephemeral=True)
                            await self.desativa_todos_botoes()

                @discord.ui.button(label='⏱', style=discord.ButtonStyle.secondary)
                async def intervalo_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id != self.message.user.id:
                        await interaction.response.send_message(content=f'> `❌` - Somente quem realizou o comando deve reagir aos botões.', ephemeral=True)
                    else:
                        async def resposta_menuconfig(interact: discord.Interaction):
                            escolha_config = interact.data['values']
                            cur.execute("UPDATE autonuke_config SET intervalo = ? WHERE servidor_id = ?", (escolha_config[0],servidor_id,))
                            con.commit()
                            embed_status = await embed()
                            await self.message.edit_original_response(embed=embed_status)
  
                        config_select = discord.ui.Select(placeholder='Selecione o intervalo de tempo:')
                        options =[
                                        discord.SelectOption(label='24 horas', value=24),
                                        discord.SelectOption(label='12 horas', value=12),
                                        discord.SelectOption(label='6 horas', value=6),
                                        discord.SelectOption(label='3 horas', value=3),
                                        discord.SelectOption(label='1 hora', value=1)
                                    ]
                        
                        config_select.options = options
                        config_select.callback = resposta_menuconfig
                        view = discord.ui.View()
                        view.add_item(config_select)
                        await interaction.response.send_message('Por favor, selecione o intervalo de tempo:', ephemeral=True, view=view)

                @discord.ui.button(label='💭', style=discord.ButtonStyle.secondary)
                async def canais_bnt(self, interaction: discord.Interaction, button: discord.ui.button):
                    """if interaction.user.id != self.message.user.id:
                        await interaction.response.send_message(content=f'> `❌` - Somente quem realizou o comando deve reagir aos botões.', ephemeral=True)
"""
                    await interaction.response.send_modal(self.modal_canais(self.message))


            if not server_db:
                cur.execute("INSERT INTO autonuke_config (servidor_id) VALUES (?)", (servidor_id,))
                await interact.response.send_message(f' - Servidor registrado na db com sucesso, execute o comando novamente.', ephemeral=True)
                con.commit()
                con.close()
            else:   
                embed_status = await embed()             
                await interact.response.send_message(embed=embed_status, view=botoes_config(interact))
                # embed de status / principal
        except Exception as er:
                logs = logs_admin.logs(f'[Comados] - Autonukero erro:\n ```{er}```')
                logs.enviar_logs()

  
            

async def setup(bot):
    await bot.add_cog(autonuke(bot))
