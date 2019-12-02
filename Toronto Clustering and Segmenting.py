#!/usr/bin/env python
# coding: utf-8

# # Clustering and Segmenting the Neighborhoods in Toronto

# In[1]:


get_ipython().system('conda install -c conda-forge geopy --yes')
get_ipython().system('conda install -c conda-forge folium=0.5.0 --yes')


# In[2]:


conda install -c anaconda beautifulsoup4 


# In[16]:


import pandas as pd
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as colors
from sklearn.cluster import KMeans
from geopy.geocoders import Nominatim
import folium
import requests
from bs4 import BeautifulSoup
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# In[42]:


#recursive function for geopy timeouts but didn't have to use
from geopy.exc import GeocoderTimedOut

def do_geocode(address):
    try:
        return geopy.geocode(address)
    except GeocoderTimedOut:
        return do_geocode(address)


# ## TASK1: Scrape data from wikipedia clone wikizero page using BeautifulSoup and create Toronto neighborhoods dataframe

# In[2]:


# Normally, I'd use the Wikipedia link but since Wikipedia is blocked by government in Turkey I need to use its close, Wikizero
# This would be the normal code:
# wiki = requests.get("https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M")
# Instead the one below with different link but same data is used

wiki = requests.get("https://www.wikizeroo.org/index.php?q=aHR0cHM6Ly9lbi53aWtpcGVkaWEub3JnL3dpa2kvTGlzdF9vZl9wb3N0YWxfY29kZXNfb2ZfQ2FuYWRhOl9N")
soup = BeautifulSoup(wiki.content, 'html.parser')


# In[3]:


#read the table from scraped data
table = soup.find('tbody')
rows = table.select('tr')
row = [r.get_text() for r in rows]


# In[4]:


#creating and cleaning the dataframe
df = pd.DataFrame(row)
df = df[0].str.split('\n', expand=True)
df = df.rename(columns=df.iloc[0])
df = df.drop(df.index[0])
df = df[df.Borough != 'Not assigned']
df = df.groupby(['Postcode', 'Borough'], sort = False).agg(','.join)
df.reset_index(inplace = True)
df = df.replace("Not assigned", "Queen's Park")
df.head()


# ## TASK2: Find coordinates by postcode and merge with the main dataframe

# In[7]:


#reading geospatial data and creating its dataframe
url = "http://cocl.us/Geospatial_data"
df_coord = pd.read_csv(url)
df_coord.rename(columns={'Postal Code': 'Postcode'}, inplace=True) 
df_coord.head()


# In[9]:


#merge two dataframes
df_GTA = pd.merge(df, df_coord, on='Postcode')
df_GTA.head()


# ## TASK3: Explore and cluster neighborhoods in Toronto

# In[11]:


#number of neighborhoods
print('There are {} boroughs and {} neighbourhoods.'.format(
        len(df_GTA['Borough'].unique()),
        df_GTA.shape[0]
    )
)


# In[33]:


# Create a new dataframe with boroughs that contain the word Toronto

Toronto_df = df_GTA[df_GTA['Borough'].str.contains('Toronto')]
Toronto_df.head()


# In[44]:


# Visualize the boroughs on the map

address = 'Toronto'
geolocator = Nominatim(user_agent="Ege_Toronto")
location = geolocator.geocode(address, timeout=15)
latitude = location.latitude
longitude = location.longitude

map_Toronto = folium.Map(location=[latitude, longitude], zoom_start=10)

for lat, lng, borough, neighborhood in zip(Toronto_df['Latitude'], Toronto_df['Longitude'], 
                                           Toronto_df['Borough'], Toronto_df['Neighbourhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_Toronto)  
    
map_Toronto


# In[ ]:




