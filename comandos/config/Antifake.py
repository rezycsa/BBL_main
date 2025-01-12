# -*- coding: utf-8 -*-
import discord
import traceback
import sqlite3
import os 
from discord.ext import commands
from discord import app_commands
from utils import logs_admin
from dotenv import dotenv_values
from datetime import datetime, timedelta

db_path =  os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Database', 'database.db') #define o caminho da db

config = dotenv_values('.env')

class Antifake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description='Comando para configurar o sistema contra contas fakes.')
    @app_commands.guild_only()
    async def config_antifake(self, interaction: discord.Interaction):
        try:
            #verifica permiçoes do usuario
            perms = interaction.user.guild_permissions
            if not perms.kick_members:
                await interaction.response.send_message('> **`❌` Você deve ter a permissão de `Kicar Membros` para executar esse comando.**', ephemeral=True)
                return
            if not perms.manage_roles:
                await interaction.response.send_message('> **`❌` Você deve ter a permissão de `Gerenciar Cargos` para executar esse comando.**', ephemeral=True)
                return
            if not perms.manage_channels:
                await interaction.response.send_message('> **`❌` Você deve ter a permissão de `Gerenciar Canais` para executar esse comando.**', ephemeral=True)
                return
 
            server_id = int(interaction.guild.id)
            if interaction.guild.icon is None:
                server_icon = 'https://i.postimg.cc/J4NTqfpC/png-clipart-discord-computer-servers-teamspeak-discord-icon-video-game-smiley-thumbnail.png'
            else:
                server_icon = interaction.guild.icon
            #funçao resposavel por carregar a embed
            async def embed():
                con_embed = sqlite3.connect(db_path)
                cur_embed = con_embed.cursor()
                cur_embed.execute("SELECT * FROM AntiFakeSystem WHERE server_id=?", (server_id,))
                server_db_embed = cur_embed.fetchall()
                con_embed.close()

                if server_db_embed:
                    if server_db_embed[0][1] == 0:
                        status = '> `Desativado`'
                    else:
                        status = '> `Ativado`'

                    if server_db_embed[0][2] is None:
                        dias_minimos = '> `Não configurado.`'
                    else:
                        dias_minimos = f'> `{server_db_embed[0][2]} Dias.`'

                    if server_db_embed[0][5] is None:
                        canal_logs = '> `Não configurado.`'
                    else:
                        canal_logs = f'> <#{server_db_embed[0][5]}>, (||`{server_db_embed[0][5]}`||)'

                    if server_db_embed[0][6] is None:
                        tipo_punicao = '> `Não configurado.`'
                    elif int(server_db_embed[0][6]) == 0:
                        tipo_punicao = '> `Kick.`'
                    elif int(server_db_embed[0][6]) == 1:
                        tipo_punicao = f'> `AutoRole`, (<@&{server_db_embed[0][7]}>)'

                    embed_status = discord.Embed(title='Config - Sistema Anti-Fake.', description='> O Sistema Anti-Fake permite a punição automática de usuários com pouco tempo de criação de conta.')
                    embed_status.set_thumbnail(url=server_icon)
                    embed_status.add_field(name=f'`💫` - Status', value=status, inline=False)
                    embed_status.add_field(name=f'`⏱` - Dias Mínimos para Entrar no Servidor', value=dias_minimos, inline=False)
                    embed_status.add_field(name=f'`📝` - Logs:', value=canal_logs, inline=False)
                    embed_status.add_field(name=f'`🔨` - Tipo de Punição:', value=tipo_punicao, inline=False)
                    embed_status.color = discord.Color(int(config['COR'].lstrip('#'), 16))
                    return embed_status
            #classe resposavel por gerar os botoes atrave de uma view
            class ConfigsButton(discord.ui.View):
                def __init__(self, message):
                    self.message = message
                    super().__init__(timeout=160)

                async def on_timeout(self) -> None:
                    await self.message.edit_original_response(content='> **`❌` - O tempo máximo foi atingido. Para abrir o menu novamente, digite o comando mais uma vez.**', embed=None, view=None)

                class ButtonModal(discord.ui.Modal):
                    def __init__(self, message):
                        self.message = message
                        super().__init__(title='AntFake - Config')

                    dias_definidos = discord.ui.TextInput(label='Dias:', placeholder='Acima de 1 dia.')

                    async def on_submit(self, interaction: discord.Interaction):
                        try:
                            dias = int(self.dias_definidos.value)
                            if dias < 1:
                                await interaction.response.send_message('> **`❌` - Por favor, insira um número válido.**', ephemeral=True)
                            else:
                                con = sqlite3.connect(db_path)
                                cur = con.cursor()
                                servidor_id = int(interaction.guild.id)
                                cur.execute("UPDATE AntiFakeSystem SET dias_minimos = ? WHERE server_id = ?", (dias, servidor_id,))
                                con.commit()
                                con.close()

                                embed_status = await embed()
                                await self.message.edit_original_response(embed=embed_status)
                                await interaction.response.defer()
                        except ValueError:
                            await interaction.response.send_message('> **`❌` - Por favor, insira um número válido.**', ephemeral=True)

                @discord.ui.button(label='💫', style=discord.ButtonStyle.primary)
                async def Definir_Status(self, interact: discord.Interaction, Button: discord.Button):
                    if interact.user.id != self.message.user.id:
                        await interact.response.send_message(content=f'> `❌` - Somente quem realizou o comando deve reagir aos botões.', ephemeral=True)
                        return
                    
                    con = sqlite3.connect(db_path)
                    cur = con.cursor()
                    cur.execute("SELECT * FROM AntiFakeSystem WHERE server_id=?", (server_id,))
                    server_db = cur.fetchall()
                    con.close()


                    if server_db[0][1] == 0:
                        dias_minimos = server_db[0][2]
                        tipo_punicao = server_db[0][6]

                        if dias_minimos is not None and tipo_punicao is not None:
                            con = sqlite3.connect(db_path)
                            cur = con.cursor()
                            cur.execute("UPDATE AntiFakeSystem SET status=? WHERE server_id=?", (1, server_id))
                            con.commit()
                            con.close()

                            embed_status = await embed()
                            await self.message.edit_original_response(embed=embed_status)
                            await interact.response.defer()
                        else:
                            await interact.response.send_message(content='> **`❌` - Por favor, configure os dias mínimos e o tipo de punição antes de ativar o sistema.**', ephemeral=True)
                    else:
                            con = sqlite3.connect(db_path)
                            cur = con.cursor()
                            cur.execute("UPDATE AntiFakeSystem SET status=? WHERE server_id=?", (0, server_id))
                            con.commit()
                            con.close()

                            embed_status = await embed()
                            await self.message.edit_original_response(embed=embed_status)
                            await interact.response.defer()


                @discord.ui.button(label='⏱', style=discord.ButtonStyle.primary)
                async def Definir_DiasMinimos(self, interact: discord.Interaction, Button: discord.Button):
                    if interact.user.id != self.message.user.id:
                        await interact.response.send_message(content=f'> `❌` - Somente quem realizou o comando deve reagir aos botões.', ephemeral=True)
                        return
                    
                    await interact.response.send_modal(self.ButtonModal(self.message))

                @discord.ui.button(label='📝',style=discord.ButtonStyle.primary)
                async def Definir_CanalLogs(self, interact: discord.Interaction, Button: discord.Button):
                    if interact.user.id != self.message.user.id:
                        await interact.response.send_message(content=f'> `❌` - Somente quem realizou o comando deve reagir aos botões.', ephemeral=True)
                        return
                    
                    async def logs_select(interaction: discord.Interaction):
                        if interaction.user.id != self.message.user.id:
                            await interaction.response.send_message(content=f'> `❌` - Somente quem realizou o comando deve reagir aos botões.', ephemeral=True)
                            return
                        
                        canal_id = interaction.data['values'][0]
                        con = sqlite3.connect(db_path)
                        cur = con.cursor()
                        cur.execute("UPDATE AntiFakeSystem SET canal_logs = ? WHERE server_id = ?", (int(canal_id), server_id))
                        con.commit()
                        con.close()

                        embed_status = await embed()
                        await self.message.edit_original_response(embed=embed_status, view=ConfigsButton(self.message))
                        await interaction.response.defer()

                    canal_logs = discord.ui.ChannelSelect(channel_types=[discord.ChannelType.text])
                    canal_logs.callback = logs_select
                    view = discord.ui.View()
                    view.add_item(canal_logs)
                    await self.message.edit_original_response(embed=None, view=view)

                @discord.ui.button(label='🔨', style=discord.ButtonStyle.primary)
                async def Definir_TipoPunicao(self, interact: discord.Interaction, Button: discord.Button):
                    if interact.user.id != self.message.user.id:
                        await interact.response.send_message(content=f'> `❌` - Somente quem realizou o comando deve reagir aos botões.', ephemeral=True)
                        return
                    
                    async def resposta_selectmenu(interaction: discord.Interaction):
                        if interaction.user.id != self.message.user.id:
                             await interaction.response.send_message(content=f'> `❌` - Somente quem realizou o comando deve reagir aos botões.', ephemeral=True)
                             return
                        
                        tipo_punicao = interaction.data['values']
                        if tipo_punicao[0] == 'kick':
                            con = sqlite3.connect(db_path)
                            cur = con.cursor()
                            cur.execute("UPDATE AntiFakeSystem SET tipo_punicao = ? WHERE server_id = ?", (0, server_id))
                            con.commit()
                            con.close()

                            embed_status = await embed()
                            await self.message.edit_original_response(embed=embed_status, view=ConfigsButton(self.message))
                            await interaction.response.defer()
                        elif tipo_punicao[0] == 'cargo':

                            async def selecionar_cargo_fun(interact: discord.Interaction):
                                if interact.user.id != self.message.user.id:
                                         await interact.response.send_message(content=f'> `❌` - Somente quem realizou o comando deve reagir aos botões.', ephemeral=True)
                                         return
                                
                                cargo_id = interact.data['values'][0]
                                cargo = interact.guild.get_role(int(cargo_id))

                                if cargo.position >= interact.user.top_role.position:
                                    await interact.response.send_message("> **`❌` - Desculpe, você não pode selecionar este cargo porque ele está acima ou do mesmo nível do seu cargo atual. Por favor, selecione um cargo abaixo do seu.**", ephemeral=True)
                                    return

                                con = sqlite3.connect(db_path)
                                cur = con.cursor()
                                cur.execute("UPDATE AntiFakeSystem SET tipo_punicao = ?, cargo_autorole = ? WHERE server_id = ?", (1, int(cargo_id), server_id))
                                con.commit()
                                con.close()

                                embed_status = await embed()
                                await self.message.edit_original_response(embed=embed_status, view=ConfigsButton(self.message))
                                await interact.response.defer()

                            selecione_cargo = discord.ui.RoleSelect(max_values=1)
                            selecione_cargo.callback = selecionar_cargo_fun
                            view = discord.ui.View()
                            view.add_item(selecione_cargo)
                            await self.message.edit_original_response(view=view)

                    tipo_punicao = discord.ui.Select(placeholder='Qual tipo de punição?')
                    options = [
                        discord.SelectOption(label='Kick', value='kick'),
                        discord.SelectOption(label='Cargo', value='cargo')
                    ]

                    tipo_punicao.options = options
                    tipo_punicao.callback = resposta_selectmenu
                    view = discord.ui.View()
                    view.add_item(tipo_punicao)

                    await self.message.edit_original_response(view=view, embed=None)
                    await interact.response.defer()

            con = sqlite3.connect(db_path)
            cur = con.cursor()
            cur.execute("SELECT * FROM AntiFakeSystem WHERE server_id=?", (server_id,))
            server_db = cur.fetchall()
            con.close()

            if not server_db:
                con = sqlite3.connect(db_path)
                cur = con.cursor()
                cur.execute("INSERT INTO AntiFakeSystem (server_id) VALUES (?)", (server_id,))
                con.commit()
                con.close()
                await interaction.response.send_message(f'- Servidor registrado na db com sucesso, execute o comando novamente.', ephemeral=True)
                return

            embed_status = await embed()
            await interaction.response.send_message(embed=embed_status, view=ConfigsButton(
                
            ))
        except Exception as error:
            print(traceback.format_exc())
            logs = logs_admin.logs(f'> **Novo erro - `Config_antifake`**\n- ```{error}```')
            logs.enviar_logs()

async def setup(bot):
    await bot.add_cog(Antifake(bot))
