import discord
from discord.ext import commands
import os
import subprocess
from dotenv import dotenv_values
from colored import Style, Fore
from utils import logs_admin

config = dotenv_values('.env')

perms = discord.Intents.default()
perms.message_content = True
perms.members = True
perms.presences = True
bot = commands.Bot(command_prefix=config['PREFIX'], intents=perms)

async def Cogs():
    #Carregando eventos
    for arquivos in os.listdir('eventos'):
        if arquivos.endswith('.py'):
            try:
                await bot.load_extension((f'eventos.{arquivos[:-3]}'))
            except Exception as er:
                logs = logs_admin.logs(f'**Novo erro - Cogs_Eventos**\n ```{er}```')
                await logs.enviar_logs()
    print(Fore.blue,'[Eventos] - Carregados com sucesso.')

    #carregando comandos
    for pastas in os.listdir('comandos'):
        if pastas != '__pycache__':
            for arquivos in os.listdir(f'comandos/{pastas}'):
                if arquivos.endswith('.py'):
                    try:
                        await bot.load_extension((f'comandos.{pastas}.{arquivos[:-3]}'))
                    except Exception as er:
                        logs = logs_admin.logs(f'**Novo erro - Cogs_comandos**\n ```{er}```')
                        await logs.enviar_logs()
    print(Fore.blue,'[Comandos] - Carregados com sucesso.')

    #Carregando Task
    for arquivos in os.listdir('task'):
        if arquivos.endswith('.py'):
            try:
                await bot.load_extension(f'task.{arquivos[:-3]}')
            except Exception as er:
                logs = logs_admin.logs(f'**Novo erro - Cogs_Task**\n ```{er}```')
                logs.enviar_logs()
    print(' [Task] - carregadas com sucesso.', Style.reset)

@bot.event
async def on_ready():
    print(Fore.green,f'[Bot] - Online com sucesso. {bot.user.name}({bot.user.id})' + Style.reset)
    await Cogs()
    stt = discord.activity.Game('Tentando ser o melhor.')
    await bot.change_presence(status=discord.Status.idle, activity=stt)
try: 
    bot.run(config['TOKEN'])
    

except discord.errors.LoginFailure:
    print(Fore.red, '[Error] - Defina corretamente o token.', Style.reset)