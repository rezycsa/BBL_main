import discord 
from discord.ext import commands

class messagens(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_message(self, msg: discord.message):
        membro = msg.author
        if membro.bot:
            return
        message_str = str(msg.content)

        if message_str.find('<@906304800512151642>') >= 0:
            await msg.channel.send(content=f'> <@{msg.author.id}>, Sou totalmente feito em slashs para ver todos meu comandos.\n- **Digite: `/help`**')

async def setup(bot):
    await bot.add_cog(messagens(bot))