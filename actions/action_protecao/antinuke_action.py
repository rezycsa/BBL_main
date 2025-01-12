import discord
import traceback
from utils import logs_admin, conectdb
from utils.embed import embed_padrao

class AntiNuke:
    def __init__(self, bot):
        self.bot = bot

    async def verificar_perms(self, interaction):
        """Função auxiliar para verificar se o usuário é o dono do servidor."""
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message(content=f'> **`❌` - Você deve ser o dono do servidor para executar esse comando.**', ephemeral=True)
            return False
        return True

    async def gerar_embed(self, interaction):
        """Gera o embed com as informações de proteção do servidor."""
        consulta_db_AntNuke = await conectdb.consultar('AntNukeSystem', interaction.guild.id).consultar_server()
        status = 'Desativado' if consulta_db_AntNuke[1] == 0 else 'Ativado'
        ant_ban = 'Desativado' if consulta_db_AntNuke[2] is None else 'Ativado'
        ant_kick = 'Desativado' if consulta_db_AntNuke[3] is None else 'Ativado'
        ant_chanell = 'Desativado' if consulta_db_AntNuke[4] is None else 'Ativado'
        ant_role = 'Desativado' if consulta_db_AntNuke[5] is None else 'Ativado'

        embed = discord.Embed(title=f'Ant Nuke - {self.bot.user.name}', description='O melhor ant nuke que vai encontrar.')
        embed = await embed_padrao(embed, interaction.guild)
        embed.add_field(name=f'`💫` - Status: (`{status}`)', value=f'> O sistema ant nuke adiciona uma protecao contra nuke dentro do servidor.', inline=False)
        embed.add_field(name=f'`🔨` - Banir: (`{ant_ban}`)', value=f'> O sistema ant nuke banir usuarios que tentarem nukear o servidor.', inline=False)
        embed.add_field(name=f'`🚪  ` - Kickar: (`{ant_kick}`)', value=f'> O sistema ant nuke kickar usuarios que tentarem nukear o servidor.', inline=False)
        embed.add_field(name=f'`🏷️` - Canais: (`{ant_chanell}`)', value=f'> O sistema ant nuke remover canais que tentarem nukear o servidor.', inline=False)
        embed.add_field(name=f'`🎫` - Roles: (`{ant_role}`)', value=f'> O sistema ant nuke remover roles que tentarem nukear o servidor.', inline=False)

        return embed

    class ProtecaoButton(discord.ui.View):
            def __init__(self, interaction, bot, main):
                super().__init__(timeout=160)
                self.interaction = interaction
                self.bot = bot
                self.main = main

            async def on_timeout(self):
                try:
                    await self.interaction.edit_original_response(
                        content=f'> **`❌` - O tempo máximo foi atingido. Para abrir o menu novamente, digite o comando mais uma vez.**',
                        view=None, embed=None
                    )
                except Exception as err:
                    pass

            @discord.ui.button(label=':dizzy:', style=discord.ButtonStyle.secondary)
            async def status_btn(self, interaction: discord.Interaction):
                if not await self.bot.verificar_perms(interaction):
                    return

            @discord.ui.button(label=':hammer:', style=discord.ButtonStyle.secondary)
            async def ban_btn(self, interaction: discord.Interaction):
                if not await self.bot.verificar_perms(interaction):
                    return

            @discord.ui.button(label=':door:', style=discord.ButtonStyle.secondary)
            async def kick_btn(self, interaction: discord.Interaction):
                if not await self.bot.verificar_perms(interaction):
                    return

            @discord.ui.button(label=':label:', style=discord.ButtonStyle.secondary)
            async def chanell_btn(self, interaction: discord.Interaction):
                if not await self.bot.verificar_perms(interaction):
                    return

            @discord.ui.button(label=':ticket:', style=discord.ButtonStyle.secondary)
            async def role_btn(self, interaction: discord.Interaction):
                if not await self.bot.verificar_perms(interaction):
                    return

            @discord.ui.button(label=':x:', style=discord.ButtonStyle.green)
            async def reload_btn(self, interaction: discord.Interaction):
                if not await self.bot.verificar_perms(interaction):
                    return

    async def main(self, interaction: discord.Interaction, mensagem: discord.Message):
        """Função principal que chama a proteção anti-nuke."""
        try:
            # Gera o embed com os detalhes de proteção
            embed = await self.gerar_embed(interaction)

            # Atualiza a resposta original com o embed e os botões de interação
            await mensagem.edit_original_response(embed=embed, view=self.ProtecaoButton(interaction, self))

        except Exception as er:
            print(traceback.format_exc())
            logs = logs_admin.logs(f'**Novo erro - antinuke**\n ```{er}```')
            logs.enviar_logs()

        return True
