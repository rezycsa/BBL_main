import discord 
import traceback

from discord.ext import commands
from discord import app_commands, ButtonStyle, Button
from utils.embed import embed_padrao
from utils import logs_admin
from utils.conectdb import consultar
from actions.action_protecao.antinuke_action import AntiNuke

class protecao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(description='Configure o sistema de segurança')
    async def protecao(self, interaction: discord.Interaction):
        try:
            #verifica se o usuario e o posse do server
            if interaction.user.id != interaction.guild.owner_id:
                await interaction.response.send_message(content=f'> **`❌` - Você deve ser o dono do servidor para executar esse comando.**', ephemeral=True)
                return
            
            async def embed():
                #consulta na db todos os sistemas
                consulta_db_AntNuke = await consultar('AntNukeSystem', interaction.guild.id).consultar_server()
                consulta_db_AntBots = await consultar('AntBotsSystem', interaction.guild.id).consultar_server()
                consulta_db_AntFake = await consultar('AntFakeSystem', interaction.guild.id).consultar_server()
                consulta_db_PermsSystem = await consultar('PermsSystem', interaction.guild.id).consultar_server()

                #cria as variaveis
                antnuke_stt = 'Desativado' if consulta_db_AntNuke[1] == 0 else 'Ativado'
                antfake_stt = 'Desativado' if consulta_db_AntFake[1] == 0 else 'Ativado'
                antbots_stt = 'Desativado' if consulta_db_AntBots[1] == 0 else 'Ativado'
                permssystem = 'Desativado' if consulta_db_PermsSystem[1] == 0 else 'Ativado'
                

                #cria embed principal
                embed = discord.Embed(title=f'Protecao - {self.bot.user.name}', description='Sistema de protecao focado na simplicidade e eficacia')
                embed = await embed_padrao(embed, interaction.guild)
                embed.add_field(name=f'`🚨` - AntiNuke (`{antnuke_stt}`)', value=f'> O sistema ant nuke adiciona uma protecao contra nuke dentro do servidor.', inline=False)
                embed.add_field(name=f'`🛎️` - AntiBots (`{antbots_stt}`)', value=f'> O sistema ant bots adiciona uma protecao contra bots maliciosos dentro do servidor.', inline=False)
                embed.add_field(name=f'`👮` - AntiFake (`{antfake_stt}`)', value=f'> O sistema ant fake adiciona uma protecao contra contas fake dentro do servidor.', inline=False)
                embed.add_field(name=f'`🎫` - Permicoes: (`{permssystem}`)', value=f'> O sistema de permicoes avancado permitido a usuarios terem somente permicao dentro do bot.', inline=False)
                return embed
            #cria funcao view

            class ProtecaoButton(discord.ui.View):
                def __init__(self, message, bot):
                    self.message = message
                    self.antinuke_action = AntiNuke(bot)
                    super().__init__(timeout=160)

                async def on_timeout(self) -> None:
                    try:
                        await self.message.edit_original_response(
                            content=f'> **`❌` - O tempo máximo foi atingido. Para abrir o menu novamente, digite o comando mais uma vez.**',
                            embed=None, view=None)
                    except:
                        pass

                # Botão do antinuke
                @discord.ui.button(label='🚨', style=discord.ButtonStyle.secondary)
                async def antinuke_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id != interaction.guild.owner_id:
                        await interaction.response.send_message(content=f'> **`❌` - Você deve ser o dono do servidor para executar esse comando.**', ephemeral=True)
                        return
                    # Chama a função main da classe AntiNuke, que irá gerar o embed e atualizar a resposta
                    await self.antinuke_action.main(interaction, self.message)
                        
                @discord.ui.button(label='🛎️', style=discord.ButtonStyle.secondary)
                async def antbots_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id != interaction.guild.owner_id:
                        await interaction.response.send_message(content=f'> **`❌` - Você deve ser o dono do servidor para executar esse comando.**', ephemeral=True)
                        return
                    return

                @discord.ui.button(label='👮', style=discord.ButtonStyle.secondary)
                async def antfake_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id != interaction.guild.owner_id:
                        await interaction.response.send_message(content=f'> **`❌` - Você deve ser o dono do servidor para executar esse comando.**', ephemeral=True)
                        return
                    return
                
                @discord.ui.button(label='🎫', style=discord.ButtonStyle.secondary)
                async def permssystem_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id != interaction.guild.owner_id:
                        await interaction.response.send_message(content=f'> **`❌` - Você deve ser o dono do servidor para executar esse comando.**', ephemeral=True)
                        return
                    return
                
                @discord.ui.button(label='❌', style=discord.ButtonStyle.danger)
                async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id != interaction.guild.owner_id:
                        await interaction.response.send_message(content=f'> **`❌` - Você deve ser o dono do servidor para executar esse comando.**', ephemeral=True)
                        return
                    original_msg = await self.message.original_response()
                    await original_msg.delete()
            
            embed_principal = await embed()
            await interaction.response.send_message(embed=embed_principal, view=ProtecaoButton(interaction, self.bot))
            
        except Exception as error:
           print(traceback.format_exc()) 
           logs = logs_admin.logs(f'> **Novo erro - `protecao`**\n- ```{error}```')
           logs.enviar_logs()
            

async def setup(bot):
    await bot.add_cog(protecao(bot))

        
