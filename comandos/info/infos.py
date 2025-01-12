import discord
from discord import app_commands
from discord.ext import commands
from utils import embed

class infos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command()
    async def ping(self, interact:discord.Interaction):
        latencia = self.bot.latency * 1000
        await interact.response.send_message(f'> :ping_pong: - Pong\n- {latencia:.2f}ms', ephemeral=True)
async def setup(bot):
    await bot.add_cog(infos(bot))