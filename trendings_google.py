#!pip install pytrends
#!pip install translators --upgrade
#!pip install googletrans
from pytrends.request import TrendReq
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import translators as ts
from googletrans import Translator

pytrend = TrendReq(hl='es-MX')

# Se extrae dataframe con 10 trendings google realtime
trends = pytrend.realtime_trending_searches(pn='MX')
trends = trends.head(10)

# Se añade fecha de la extracción
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
trends['date'] = dt_string

# Se obtienen las consultas relacionadas por cada keyword
trends['relatedqueries'] = ''
for index, row in trends.iterrows():
    kw_list = row['title'].split(', ')
    kw_list = [ts.google(t,from_language='en', to_language='es') for t in kw_list]
    pytrend.build_payload(kw_list, cat=0, timeframe='now 1-d', geo='MX', gprop='')
    data = pytrend.related_queries()
    d = {'query':[], 'value':[]}
    df_related = pd.DataFrame(data=d)
    for i in kw_list:
        df_related = pd.concat([df_related,data[i]['top']])
    #df_related = df_related.groupby(['query'],sort=True).sum()
    df_related.sort_values(['value'], ascending=False)
    row['relatedqueries'] = df_related['query'].iloc[0] + '--' + df_related['query'].iloc[1] + '--' + df_related['query'].iloc[2]+ '--' + df_related['query'].iloc[3]+ '--' + df_related['query'].iloc[4]
    trends.to_csv('trendings_google.csv', index=False) 

   