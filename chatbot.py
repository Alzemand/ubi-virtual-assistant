# -*- coding:utf-8 -*-

from chatterbot.trainers import ListTrainer
from chatterbot import ChatBot

carregar_conversa = open("CONVERSA", "r")

bot = ChatBot('test')

# conv = ['oi', 'olá', 'bom dia', 'bom dia pra vc!', 'obrigado']

conv = carregar_conversa.readlines()

bot.set_trainer(ListTrainer)

bot.train(conv)

while True:
    quest = input('voce: ')
    response = bot.get_response(quest)
    if float(response.confidence) > 0.5:
        print ('Bot: ', response)
    else:
        print ('Bot: Não sei responder')
