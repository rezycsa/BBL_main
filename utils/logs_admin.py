from dotenv import dotenv_values
from colored import Fore, Style
import requests


config = dotenv_values('.env')

avatar_padrao = 'https://media.discordapp.net/attachments/1218972148220035124/1219445431876980837/ef0baf5b46e6da451bc3abb30f1a1bf9.jpg?ex=66303e0f&is=661dc90f&hm=bd92ee75dcd327fb10cd7a061ef09935c127fd9b01440acbcf9e1604af34a23a&=&format=webp'
username_padrao = 'Logs - System'
webhook_url = config['WEBHOOK']

class logs():

    def __init__(self,mensagem):
        self.mensagem = mensagem
    
    def enviar_logs(self, username=None, avatar=None):
        if username == None: username = username_padrao 
        else: username = username

        if avatar == None: avatar = avatar_padrao 
        else: avatar = avatar
            
        data = {
            'avatar_url':avatar,
            'username':username,
            'content':self.mensagem
               }
        
        headers = {
            'Content-Type': 'application/json'
                  }
        
        try:
            enviar = requests.post(webhook_url, json=data, headers=headers)

            if enviar.status_code != 204:
                print(Fore.red, 'Nao foi possivel enviar as logs, verifique as configuraçoes e reinicie o bot.', Style.reset)

        except Exception as er:
            print(Fore.red, f'[Error] - Erro na funçao de logs admin.\n {er}', Style.reset)
