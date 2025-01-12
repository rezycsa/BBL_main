import discord
import os
import sqlite3 
import traceback
from discord.ext import commands
from discord import app_commands
from utils import logs_admin
from utils.embed import embed_padrao

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Database', 'database.db')

class RoleStt(commands.Cog):
    def __init__(self, bot):
     self.bot = bot 

    @app_commands.command(description='Configure o sistema de cargo por status.')
    async def biocheck(self, interact: discord.Interaction):
        try:
            #verifica permicao do membro
            if not interact.user.guild_permissions.manage_roles:
                await interact.response.send_message(content=f'> **`❌` - Você deve ter a permissão de `Gerenciar cargos` para executar esse comando.**', ephemeral=True)
                return 

            #verifica o icon do sever
            server_id = int(interact.guild.id)
   

   	      #funcao de consultar db
            async def db_conecte():
               con = sqlite3.connect(db_path)
               cur = con.cursor()
               cur.execute("SELECT * FROM StatusRoleSystem WHERE server_id=?", (server_id,))
               server_db = cur.fetchone()
            
               if not server_db: #verifica se o sevidor esta registrado na db
                cur.execute("INSERT INTO StatusRoleSystem (server_id) VALUES (?)", (server_id,))
                con.commit()
                cur.execute("SELECT * FROM StatusRoleSystem WHERE server_id=?", (server_id,))
                server_db = cur.fetchone()               
               con.close()
               return server_db
            
         #cria funcao de embed
            async def embed():
               server_db = await db_conecte()

               if server_db[1] == 0:
                  status = '> `Desativado`'
               else:
                  status = '> `ativo`'

               if server_db[2] is None:
                  cargos_msg = '> `Nao configurado`'
               else:
                  #caso tenha cargos configurados
                  role_lista = server_db[2].split(',')
                  cargos_msg = "> "
                  for role in role_lista:
                     if role == role_lista[-1]:  # Se for o último cargo da lista
                           cargos_msg += f'<@&{role}>'
                     else:
                           cargos_msg += f'<@&{role}>,'

               if server_db[3] is None:
                  mensagem_Stt = '> `Nao configurado`'
               else:
                  mensagem_Stt = str(f'> `{server_db[3]}`')
               
               if server_db[4] is None:
                  canal_logs = '> `Nao configurado`'
               else:
                  canal_logs = str(f'> <#{server_db[4]}>')
                  

               embed = discord.Embed(title='Config - Sistema de cargo por status.', description='> Sistema destinado a colocar automaticamente cargos em membros com status personalizados.')
               embed = await embed_padrao(embed, interact.guild)
               embed.add_field(name=f'`💫` - Status', value=status, inline=False)
               embed.add_field(name=f'`🔑` - Cargos:', value=cargos_msg, inline=False)
               embed.add_field(name=f'`🎫` - Mensagem: ', value=mensagem_Stt, inline=False)
               embed.add_field(name=f'`📝` - Logs:', value=canal_logs, inline=False)
               return embed


                        #funcao de criar select de mensagem
           
            class MsgModal(discord.ui.Modal):
               def __init__(self, message):
                  self.message = message
                  super().__init__(title='Defina a mensagem de status')

                  #cria o campo de texto
                  self.mensagem_definida = discord.ui.TextInput(
                        label='Mensagem definida', style=discord.TextStyle.short,
                        placeholder='Digite a mensagem aqui...',
                        max_length=124, required=True)
                  self.add_item(self.mensagem_definida)

               #funcao qunado e enviado 
               async def on_submit(self, interaction: discord.Interaction):
                     mensagem = str(self.mensagem_definida.value)

                     con = sqlite3.connect(db_path)   
                     cur = con.cursor()
                     cur.execute("UPDATE StatusRoleSystem SET msg=? WHERE server_id=?", (mensagem, server_id))
                     con.commit()
                     con.close()
                     #envia embed
                     embed_status = await embed()
                     await self.message.edit_original_response(embed=embed_status, view=ConfigButton(interaction), content=None)
                     await interaction.response.defer()

   	   #cria funcao de viwer, para os botoes e menus etc...
            class ConfigButton(discord.ui.View):
               def __init__(self, message):
                  self.message = message 
                  super().__init__(timeout=160)
               
               #define a funcao de timeout, quando o tempo maximo for atingido, o menu será fechado 
               async def on_timeout(self) -> None:
                  await self.message.edit_original_response(
                     content=f'> **`❌` - O tempo máximo foi atingido. Para abrir o menu novamente, digite o comando mais uma vez.**',
                     embed=None, view=None)
                     
               #cria a funcao do botao de status
               @discord.ui.button(label='💫', style=discord.ButtonStyle.primary)
               async def status(self, interact: discord.Interaction, button: discord.ui.Button):
                  if interact.user.id != self.message.user.id:
                     await interact.response.send_message(content=f'> `❌` - Somente quem realizou o comando deve reagir aos botões.',
                     ephemeral=True)
                     return 
                  
                  server_db = await db_conecte()

                  if server_db[1] == 0:
                     if server_db[2] is None: #verifica se o cargo foi corfigurado
                        await interact.response.send_message(content=f'> **`❌` - Voce deve definir o cargo antes de ativar o sistema.**', ephemeral=True)
                        return
                     
                     if server_db[3] is None: #verifica se a mensagem foi configurada
                        await interact.response.send_message(content=f'> **`❌` - Voce deve definir a mensagem antes de ativar o sistema.**', ephemeral=True)	
                        return

                     con = sqlite3.connect(db_path)
                     cur = con.cursor()
                     cur.execute("UPDATE StatusRoleSystem SET status=1 WHERE server_id=?", (server_id,))
                     con.commit()
                     con.close()

                     embed_status = await embed()
                     await self.message.edit_original_response(embed=embed_status)
                     await interact.response.defer()
                  else: 
                     con = sqlite3.connect(db_path)
                     cur = con.cursor()
                     cur.execute("UPDATE StatusRoleSystem SET status=0 WHERE server_id=?", (server_id,))
                     con.commit()
                     con.close()
                     embed_status = await embed()
                     await self.message.edit_original_response(embed=embed_status)
                     await interact.response.defer()

               #cria a funcao do botao de cargo
               @discord.ui.button(label='🔑', style=discord.ButtonStyle.secondary )
               async def cargo(self, interact: discord.Interaction, button: discord.ui.Button):
                  if interact.user.id != self.message.user.id:
                        await interact.response.send_message(content=f'> `❌` - Somente quem realizou o comando deve reagir aos botões.',
                        ephemeral=True)
                        return
                 
                 #funcao de criar select de role
                  async def role_select(interaction: discord.Interaction):

                     if interaction.user.id != self.message.user.id: 
                      await interaction.response.send_message(content=f'> **`❌` - Somente quem realizou o comando deve reagir aos botões.**', ephemeral=True)
                      return

                     roles_lista = interaction.data['values']

                     #verifica em loop todos os cargos
                     for role in roles_lista:
                        cargo = interaction.guild.get_role(int(role))
                        if cargo.position >= interaction.user.top_role.position:
                           await interaction.response.send_message(
                                 content=f'> **`❌` - Você não pode definir um cargo com permissão maior ou igual ao o seu.**', 
                                 ephemeral=True
                           )
                         
                           return

                     #salva na db
                     roles_lista_db = ','.join(map(str, roles_lista))
                     con = sqlite3.connect(db_path)
                     cur = con.cursor()
                     cur.execute("UPDATE StatusRoleSystem SET cargos=? WHERE server_id=?", (roles_lista_db, server_id))
                     con.commit()
                     con.close()

                     embed_status = await embed()
                     await self.message.edit_original_response(embed=embed_status, view=ConfigButton(interaction), content=None)
                     await interaction.response.defer()

                  #funcao de voltar 
                  async def voltar_role_select(interaction: discord.Interaction):
                     if interaction.user.id != self.message.user.id:
                        await interaction.response.send_message(content=f'> **`❌` - Somente quem realizou o comando deve reagir aos botões.**', ephemeral=True)
                        return

                     embed_status = await embed()
                     await self.message.edit_original_response(embed=embed_status, view=ConfigButton(interaction), content=None)
                     await interaction.response.defer()
                        

                  #envia o select roles e emebd
                  cargo_select = discord.ui.RoleSelect(placeholder='Selecione o cargo', min_values=1, max_values=5)
                  voltar = discord.ui.Button(label='❌', style=discord.ButtonStyle.danger)

                  voltar.callback = voltar_role_select
                  cargo_select.callback = role_select

                  view = discord.ui.View()

                  view.add_item(cargo_select)
                  view.add_item(voltar)
                  await self.message.edit_original_response(content=f'> **`🔑` - Selecione de 1 a 5 cargos abaixo:** ', view=view, embed=None)

             #cria a funcao do botao de mensagem
               @discord.ui.button(label='🎫', style=discord.ButtonStyle.secondary)
               async def mensagem(self, interact: discord.Interaction, button: discord.ui.Button):
                  #verfica padrao
                  if interact.user.id != self.message.user.id:
                           await interact.response.send_message(content=f'> `❌` - Somente quem realizou o comando deve reagir aos botões.',
                           ephemeral=True)
                           return
                  #envia o modal
                  await interact.response.send_modal(MsgModal(self.message))         

               @discord.ui.button(label='📝', style=discord.ButtonStyle.secondary)
               async def logs(self, interact: discord.Interaction, button: discord.ui.Button):
                  if interact.user.id != self.message.user.id:
                        await interact.response.send_message(content=f'> `❌` - Somente quem realizou o comando deve reagir aos botões.',
                        ephemeral=True)
                        return
                  #funcao de seletor de canal de logs
                  async def logs_select(interaction: discord.Interaction):
                     #verifica se o usuario e o mesmo que criou o comando
                     if interaction.user.id != self.message.user.id:
                        await interaction.response.send_message(content=f'> **`❌` - Somente quem realizou o comando deve reagir aos botões.**', ephemeral=True)
                        return

                     canal_id = interaction.data['values'][0]

                     con = sqlite3.connect(db_path)
                     cur = con.cursor()
                     cur.execute("UPDATE StatusRoleSystem SET canal_logs=? WHERE server_id=?", (canal_id, server_id))
                     con.commit()
                     con.close()

                     embed_status = await embed()
                     await self.message.edit_original_response(embed=embed_status, view=ConfigButton(interaction), content=None)
                     await interaction.response.defer()

                  #funcao de voltar 
                  async def voltar_logs_select(interaction: discord.Interaction):
                     if interaction.user.id != self.message.user.id:
                        await interaction.response.send_message(content=f'> **`❌` - Somente quem realizou o comando deve reagir aos botões.**', ephemeral=True)
                        return

                     #retira o canal de logs
                     con = sqlite3.connect(db_path)
                     cur = con.cursor()
                     cur.execute("UPDATE StatusRoleSystem SET canal_logs=? WHERE server_id=?", (None, server_id))
                     con.commit()
                     con.close()


                     embed_status = await embed()
                     await self.message.edit_original_response(embed=embed_status, view=ConfigButton(interaction), content=None)
                     await interaction.response.defer()
                  
                  #envia o select roles e edita a embed
                  canal_select = discord.ui.ChannelSelect(placeholder='Selecione o canal de logs', channel_types=[discord.ChannelType.text], max_values=1, min_values=1)
                  voltar = discord.ui.Button(label='❌', style=discord.ButtonStyle.danger)
                  
                  voltar.callback = voltar_logs_select 
                  canal_select.callback = logs_select

                  view = discord.ui.View()
                  view.add_item(canal_select)
                  view.add_item(voltar)

                  await self.message.edit_original_response(content=f'> **`📝` - Selecione o canal de logs abaixo:** ', view=view, embed=None)
                  
               @discord.ui.button(label='❌', style=discord.ButtonStyle.danger)
               async def delete(self, interact: discord.Interaction, button: discord.ui.Button):
                  #verifica se o usuario e o mesmo que criou o comando
                  if interact.user.id != self.message.user.id:
                     await interact.response.send_message(content=f'> **`❌` - Somente quem realizou o comando deve reagir aos botões.**', ephemeral=True)
                     return
                  
                  original_msg = await self.message.original_response()
                  await original_msg.delete()
               

          #envia embed
            embed_status = await embed()
            await interact.response.send_message(embed=embed_status, view=ConfigButton(interact))

        except Exception as error: #caso tenha erro no codigo
           print(traceback.format_exc()) 
           logs = logs_admin.logs(f'> **Novo erro - `cargo_por_status`**\n- ```{error}```')
           logs.enviar_logs()


async def setup(bot):
   await bot.add_cog(RoleStt(bot))