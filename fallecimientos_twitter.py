import tweepy
import configparser
import pandas as pd
import nltk
from datetime import date,timedelta,datetime

import re, string
from nltk.corpus import stopwords

import os
from email.message import EmailMessage
import ssl
import smtplib

now = datetime.now()

nltk.download('punkt')

nltk.download('stopwords')
stop_words = set(stopwords.words('spanish')) 

stop_add=['con','com','media','excelsior','https','muere','t','co','AT_USER','rt','URL','is','am','are','was','were','a','an','of','the',
        'to','in','for','and','i','you','at','this','there','that','he','she','it','his','her',
        'will','on','by','about','with','and','or','la','el','en','que','y','no','los','es','al',
        'lo','todo','se','de','muere','jajajja','si','hay','me','mas','por','este','con','del',
        'para','las','dia','una','un','cada','ni','porque','vez','te','hoy','como','mi','su','hace',
        'mientras','q','sin','todos','.','le','pero','nos','tu','sus','*se','we','dice','o','ver',
        'era','día','ser','ha','solo','fue','más','“','”',"rt",'murió','fallecimiento','fallece','años','nunca','gente','hierro','d','ahí',
        'voy','interesa']

for i in range(0,len(stop_add)):
    stop_words.add(stop_add[i])

contador=0
tweets_list=""
limite=100
anterior=""
minutos=datetime.now().replace(second=0,microsecond=0)


print("MINUTOS - Ultima Version 2.0: ")
print(minutos)

# read configs
config = configparser.ConfigParser()
config.read('config.ini')

api_key = 't7Vz5Kp6syH61yKd91RtOQ28b'
api_key_secret = 'eNQAniEy7bBR77MVfQaAtaf0gPf33LazyT1zEac9grW6qEGndu'

access_token = '840651100688605184-XGt6JUBuGgkdESZAL6IJax3AXvRFXS2'
access_token_secret = 'skl5vJOzNzQVUbkw4ZJuB0U3VnkgFIB65AlWd1TpoloL4'

# authentication
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

def enviar_correo(trends):
    email_emisor='tendenciasimagendigital@gmail.com'
    email_password='kkneizqoyvnvxsma'
    email_receptor=['aaron.juarez@imagendigital.com','diego.esteva@imagendigital.com']
    email_receptor2='diego.esteva@imagendigital.com'

    asunto='NUEVO TREND DETECTADO'
    cuerpo="""KEYWORDS TRENDS: """ +"\n" + "keywords(muere,fallece,fallecimiento,murió):"+ "\n"

    for i in range(0,9):

        cuerpo=cuerpo +"\n"+str(trends[i][0]) +": "+str(trends[i][1]) +"\n"

 

    em=EmailMessage()
    em['From']=email_emisor
    em['To']=email_receptor
    em['Subject']=asunto
    em.set_content(cuerpo)

    contexto=ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=contexto) as smtp:
        smtp.login(email_emisor,email_password)
        smtp.sendmail(email_emisor,email_receptor,em.as_string())
        #smtp.sendmail(email_emisor,email_receptor2,em.as_string())


def eliminar_caracteresesp(texto):
        
    texto=texto.lower()    #Hace minusculas todas las letras del cuerpo

    texto=re.sub('[%s]' % re.escape(string.punctuation), ' ', texto) #Elimina puntuacion

    auxtexto=nltk.word_tokenize(texto)
    auxtexto2=[]  

    for w in auxtexto:  #Elimina articulos gramaticales
        if w not in stop_words: 
            auxtexto2.append(w)
    return auxtexto2


def contar_tweets(tweet):

    global contador,tweets_list,limite,minutos,anterior
    

    if datetime.now().replace(second=0,microsecond=0) == (minutos+timedelta(minutes=10)) :
        print("--- RESETEANDO CONTADOR /n /n /n ---")
        minutos=datetime.now().replace(second=0,microsecond=0)
        tweets_list=""
        limite=100


    tweets_list=tweets_list+" "+tweet

    tweets_tokens=eliminar_caracteresesp(tweets_list)
    #print(len(tweets_tokens))

    palabras=nltk.FreqDist(tweets_tokens).most_common(10)

    if palabras[0][1] > limite:

        if anterior != palabras[0][0]:
            anterior=palabras[0][0]
            enviar_correo(palabras)
        limite=limite+100

        print("Nuevo trend detectado")


    print(palabras)



 
class Linstener(tweepy.Stream):


 #   tweets = []
 #   limit = 1
#    def on_status(self, status):

#        print(status.text)
#        contar_tweets(status.extended_tweet["full_text"])

    def on_status(self, status):
        if hasattr(status, "retweeted_status"):  # Check if Retweet
            try:
              #  print(status.retweeted_status.extended_tweet["full_text"])
                contar_tweets(status.retweeted_status.extended_tweet["full_text"])
            except AttributeError:
               # print(status.retweeted_status.text)
                contar_tweets(status.retweeted_status.text)
        else:
            try:
                #print(status.extended_tweet["full_text"])
                try:
                    contar_tweets(status.extended_tweet["full_text"])
                except:
                    print("Error reiniciando")
            except AttributeError:
                #print(status.text)
                contar_tweets(status.text)

    def on_error(self, status_code):
        if status_code == 420:  # end of monthly limit rate (500k)
            return False





stream_tweet = Linstener(api_key, api_key_secret, access_token, access_token_secret)


stream_tweet.filter(languages=['es'],track=['muere','fallece','fallecimiento','murió'])


