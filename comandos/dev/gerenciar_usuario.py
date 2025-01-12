import discord 
import sqlite3
import datetime
import requests
import json
import os 
from discord import app_commands
from discord.ext import commands
from dotenv import dotenv_values
from time import sleep
from utils import embed, logs_admin

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Database', 'database.db') #caminho da db

config = dotenv_values('.env')
icon_padrao =  'https://media.discordapp.net/attachments/1237961121714016349/1237961507099119696/image_2.png?ex=663d8cff&is=663c3b7f&hm=0a53fc41dce47a0ceb8d8b0dc9c6afd5d7551f904c32d6c47596bee7d8988878&=&format=webp&quality=lossless&width=373&height=350'
webhook_url = 'https://discord.com/api/webhooks/1238988821085945950/9ErhVuA_Sx4GXd_eE8y9p4OOcuD07j1LFdjS45BvQ4XiFmHm1RVwCJnMnVGdaGzKlAZE'

class gerenciamento_usuarios(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(description='Comando reservado a equipe de gerenciamento da bbl.')
    @app_commands.describe(user='Informe o id do usuario na qual deseja gerenciar.')
    async def gerenciar_usuario(self, interact: discord.Interaction, user: discord.User):
        author = interact.user
        # Verifica se o usuário é desenvolvedor
        if str(author.id) != config['DONO']:
            await interact.response.send_message(content=f'> **`❌` - Você deve fazer parte da nossa equipe para executar esse comando.**', ephemeral=True)
            return
        
        #conexao com banco de dados
        con = sqlite3.connect(db_path)
        cur = con.cursor()            
        cur.execute("SELECT * FROM usuarios WHERE id=?", (user.id,))
        user_db = cur.fetchall()


        if not user_db:
            await interact.response.send_message(content="> **`❌` - Usuário não encontrado na base de dados.**", ephemeral=True)
            return

      #funçao criadora da embed
        async def gerar_embed():
            embed_info_user = discord.Embed(title=f'Gerenciamento de usuário')
            embed_info_user.set_thumbnail(url=user.display_avatar)
            embed_info_user.add_field(name="- **`🆔` ID:**", value=f"> `{user.id}`", inline=False)
            embed_info_user.add_field(name="- **`📧` - E-mail:**", value=f"> ||{str(user_db[0][1])}||", inline=False)
            embed_info_user.add_field(name='- **`🔗` - Ip:**', value=f'> ||{str(user_db[0][6])}||', inline=False)
            embed_info_user.add_field(name="- ** `💬` - Comandos Executados:**", value=f"> `{user_db[0][4]}`", inline=False)
            embed_info_user.add_field(name="- **`👮‍♂️` - Blacklist**", value="> `✅`" if user_db[0][5] == 1 else "> `❌`", inline=False)
            embed_info_user.set_footer(text=f'{config['URL']} | Ajuda • {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}', icon_url=icon_padrao)
            embed_info_user.color = discord.Color(int(config['COR'].lstrip('#'), 16))
            return embed_info_user



        #criando botoes basicos
        class botoes_gerenciadores(discord.ui.View):
            def __init__(self, message):
                super().__init__(timeout=160)
                self.foo = None
                self.message = message
            
            async def desativar_botoes(self):
                for item in self.children:
                    item.disabled = True
                await self.message.edit_original_response(view=self, allowed_mentions=None)

            async def on_timeout(self):
                await self.desativar_botoes()
                await self.message.edit_original_response(content='> `❌` - Tempo inspirado, voce demorou demais para responder.', view=None, embed=None)
                con.close()

            class header_blacklist_bnt(discord.ui.Modal):
                def __init__(self, message):
                    self.message = message
                    super().__init__(title='Blacklist - BBL System:')
                    
                    self.motivo_blacklist = discord.ui.TextInput(label='Motivo: ', placeholder='Digite aqui o motivo.')
                    self.add_item(self.motivo_blacklist)

                async def send_logs_blacklist(self, author:discord.User, user:discord.User, motivo=None):
                        motivo = motivo if motivo else '...'
                        
                        data = {
                                'embeds': [
                                    {
                                        "title": "Mensagem de Log - Blacklist",
                                        "description": f"- **`👤` - Usuário: `{user.name}`(||{user.id}||)**\n- **`👮‍♂️` - Author da puniçao: `{author.name}`(||{author.id}||)**\n> Motivo: `{motivo}`\n",
                                        "color": int(config['COR'].lstrip('#'), 16), 
                                        "thumbnail": {"url": str(user.display_avatar)},
                                        "footer": {
                                            "text": f"{config['URL']} | Ajuda • {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}",
                                            "icon_url": icon_padrao
                                        },

                                    }
                                ]
                            }

                        headers = {'Content-Type': 'application/json'}

                        response = requests.post(webhook_url, headers=headers, data=json.dumps(data))


                async def on_submit(self, interaction: discord.Interaction):
                    motivo = self.motivo_blacklist.value
                    cur.execute('UPDATE usuarios SET blacklist = 1 WHERE id = ?',(user.id,))
                    con.commit()
                    con.close()
                    embed_info_user = await gerar_embed()
                    await self.message.edit_original_response(embed=embed_info_user)
                    await interaction.response.defer()

                    suporte_bnt = discord.ui.Button(label='Suporte', style=discord.ButtonStyle.url, url='https://discord.gg/VNdrdy4haS')
                    view = discord.ui.View()
                    view.add_item(suporte_bnt)

                    message_motivo = (
                    f"> **`🧨` - Lamentamos informar que suas ações recentes violaram nossas regras, resultando na sua adição à nossa blacklist.**\n"
                    f" - **Motivo:** `{motivo}`\n\n"
                    "Se você acredita que houve um equívoco ou precisa de mais esclarecimentos, por favor, não hesite em entrar em contato com nossa equipe de suporte. Estamos aqui para ajudar."
                    )

                    await user.send(content=message_motivo, view=view)
                    await self.send_logs_blacklist(interaction.user, user, str(motivo))


            @discord.ui.button(label='👮‍♂️', style=discord.ButtonStyle.blurple)
            async def blacklist_bnt(self, interaction: discord.Interaction, Button: discord.ui.Button):
                    if interaction.user.id != self.message.user.id:
                        await interaction.response.send_message(content=f'> **`❌` - Somente quem realizou o comando deve reagir aos botões.**', ephemeral=True)
                        return


                    if int(user_db[0][5]) == 1:
                        cur.execute('UPDATE usuarios SET blacklist = 0 WHERE id = ?',(user.id,))
                        con.commit()
                        con.close()
                        embed_info_user = await gerar_embed()
                        await self.message.edit_original_response(embed=embed_info_user)
                        await interaction.response.defer()
                        await self.desativar_botoes()
                        motivo = '...'
                        await self.header_blacklist_bnt.send_logs_blacklist(self, interact.user, user)

                        message = ( "> **`✅` - Excelentes notícias! Você foi removido com sucesso da nossa blacklist. Estamos ansiosos para vê-lo contribuindo positivamente para a nossa comunidade novamente.**\n - Seja bem-vindo de volta!")
                        await user.send(content=message)
                        return
                    else:
                        await interaction.response.send_modal(self.header_blacklist_bnt(self.message))
                        return


        # Criação da embed com as informações do usuário
        embed_info_user = await gerar_embed()
        await interact.response.send_message(embed=embed_info_user, view=botoes_gerenciadores(interact))

async def setup(bot):
    await bot.add_cog(gerenciamento_usuarios(bot))