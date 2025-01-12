import discord
from dotenv import dotenv_values
from datetime import datetime

config = dotenv_values('.env')
icon_padrao =  'https://i.postimg.cc/J4NTqfpC/png-clipart-discord-computer-servers-teamspeak-discord-icon-video-game-smiley-thumbnail.png'

async def embed_padrao(embed: discord.Embed, guild: discord.Guild):
    server_icon = icon_padrao
    
    if guild.icon != None:
        server_icon = guild.icon
        
    embed.set_thumbnail(url=server_icon)
    embed.color = discord.Color(int(config['COR'].lstrip('#'), 16))
    embed.set_footer(text=f'{config['URL']} | Ajuda • {datetime.now().strftime('%d/%m/%Y %H:%M')}', icon_url=icon_padrao)
    
    return embed