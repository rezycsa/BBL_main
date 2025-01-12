import discord
import json
from discord import app_commands
from discord.ext import commands
from dotenv import dotenv_values

config = dotenv_values('.env')

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
    
    @commands.command()
    async def load_slash(self, ctx:commands.Context):
        if ctx.author.id == int(config['DONO']):
            comandos = await self.bot.tree.sync()
            await ctx.reply(f'> `✔` - Comandos carregados com sucesso.\n - Totais de comandos: `{len(comandos)}`')
        else: 
            await ctx.reply(f'> ❌ - Voce deve ser um dev para executar esse comando.')

async def setup(bot):
    await bot.add_cog(Admin(bot))


    