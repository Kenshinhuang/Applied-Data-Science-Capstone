#!/usr/bin/env python
# coding: utf-8

# # <center> Segmenting and Clustering Toronto Neighbourhoods <center>

# # Objective: Segment and cluster the Toronto neighbourhoods based on post codes

# Download the table of post codes for neighbourhoods in Toronto from Wikipedia. https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M 

# I have Excel 2016, which can hold 1,048,576 rows. The post code table has only 287 rows. I tried using BeautifulSoup first. But when I was half-way through and dealing with all those issues of cleaning the data, I realized that for such a small table, directlying downloading it into Excel, then uploading it into Jupyter Notebook will be much easier and faster as well. So, I scraped all my BeautifulSoup codes.

# In[96]:


import pandas as pd
postcode_df=pd.read_excel('Toronto Post Codes.xlsx')
postcode_df.head()


# In[97]:


# size of the table
postcode_df.shape


# In[98]:


# number of unique Boroughs
import numpy as np
postcode_df["Borough"].value_counts()


# Okay. So there are 77 "Not assigned" in the Borough column. I could use drop.duplicates() to drop those "Not assigned". However, that will drop the other boroughs as well, since there are boroughs that have more than one neighbourhoods assigned to it. So, drop by "Borough" won't work.

# Let's check the Neighbourhood column. The neighbourhoods should be unique, except for the "Not assigned".

# In[99]:


postcode_df["Neighbourhood"].value_counts()


# All the neighbourhoods are unique, except for 1) the "Not assigned" and  2) "Runnymede" and "St. James Town" where there are two copies.

# In[100]:


#Remove the "Not assigned" from the Borough column.
postcode_df.drop_duplicates(subset="Neighbourhood",keep=False, inplace=True)
postcode_df


# All the "Not assigned" in the Neighbourhood column has been dropped. However, since the parameter "keep" was set to False. The process above dropped the two neighbourhoods "Runnemede" and "St. James Town" as well. But I would like to keep those two neighbourhoods, since each copy belong to two different boroughs.

# Put the two neighbourhoods back.

# In[101]:


append1=pd.DataFrame({"Postcode":["M5C","M6N","M6S","M4X"],"Borough":["Downtown Toronto","York","West Toronto","Downtown Toronto"],"Neighbourhood":["St. James Town","Runnymede","Runnymede","St. James Town"]})
postcode_df.append(append1,ignore_index=False)


# As shown above,the original table has 287 rows in total and 77 "Not assigned" in the Borough column. After the 77 "Not assigned" rows are dropped, the cleaned table should have 287-77=210 rows. The result of the above code block shows 210 rows. 

# Let's confirm that there is no more "Not assigned" in Borough column.

# In[102]:


postcode_df["Borough"].value_counts()


# Cool. There is no more "Not assigned" in the Borough column. 

# The table is cleaned now. I can start working with it. The next thing I am going to do is to put the neighbourhoods that have the same postcode in the same row. Let's see how many unique postcodes are in the cleaned table.

# In[103]:


count=postcode_df["Postcode"].value_counts()


# There are 102 unique postcodes. Most of the postcodes has only 1 neighbourhoods associated with it. However, postcodeS "M8Y" and "M9V" have 8 neighbourhoods associated with it, "M5V" has 7, "M4V" and "M8Z" have 5. I need to concatenate all those neighbourhoods under the postcode they are associated with, in one row.

# In[104]:


postcode_df=pd.DataFrame(postcode_df.groupby(["Postcode","Borough"])["Neighbourhood"].apply(lambda x: ','.join(x)))
postcode_df


# All the neighbourhoods are now concatenated under the postcode they are associated with. However, instead of regular index, the table has "Postcode" and "Borough" as its multi-column index. I am going to fix it below.

# In[105]:


postcode_df.reset_index(inplace=True)
postcode_df


# In[106]:


print(postcode_df.shape)


# Next, find the latitude and longitude coordinates for each postcode.

# In[107]:


# Load the "Geospatial_Coordinates.csv" dataset
Geo_df=pd.read_csv("Geospatial_Coordinates.csv")
Geo_df.head()


# In[108]:


# Merge "postcode_df" and "Geo_df". 
# Use "left" join so that all records from "postcode_df" and matched records from "Geo_df" are returned.
Geomerge_df=pd.merge(postcode_df,Geo_df, how="left")
Geomerge_df


# Cluster the neighbourhoods and create visualizations.

# Import the necessary libraries first.

# In[109]:


import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json # library to handle JSON files

#!conda install -c conda-forge geopy --yes # uncomment this line if you haven't completed the Foursquare API lab
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

#!conda install -c conda-forge folium=0.5.0 --yes # uncomment this line if you haven't completed the Foursquare API lab
import folium # map rendering library


# Get the latitude and longitude for Toronto City.

# In[111]:


address = 'Toronto, Canada'

geolocator = Nominatim(user_agent="ny_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Toronto, Canada are {}, {}.'.format(latitude, longitude))


# Create a map of Toronto City with the neighbourhoods superimposed on it.

# In[112]:


# Toronto latitude and longitude.
latitude= 43.653963
longitude=-79.387207

# create map and display it
toronto_map = folium.Map(location=[latitude, longitude], zoom_start=12)

# instantiate a feature group for the incidents in the dataframe
incidents = folium.map.FeatureGroup()

# loop through the 100 crimes and add each to the incidents feature group
for lat, lng, in zip(Geomerge_df.Latitude, Geomerge_df.Longitude):
    incidents.add_child(
        folium.features.CircleMarker(
            [lat, lng],
            radius=5, # define how big you want the circle markers to be
            color='red',
            fill=True,
            fill_color='blue',
            fill_opacity=0.6
        )
    )

# add incidents to map
toronto_map.add_child(incidents)


# Simplify the above map and segment and cluster only the neighborhoods with "Toronto" in their borough names. These are the neighbourhoods associated with the following boroughs: Central Toronto, Downtown Toronto, East Toronto and West Toronta. So let's slice the original dataframe and create a new dataframe for the Toronto boroughs.

# In[113]:


toronto_data1 = Geomerge_df[Geomerge_df['Borough'] == 'Central Toronto'].reset_index(drop=True)
toronto_data2 = Geomerge_df[Geomerge_df['Borough'] == 'Downtown Toronto'].reset_index(drop=True)
toronto_data3 = Geomerge_df[Geomerge_df['Borough'] == 'East Toronto'].reset_index(drop=True)
toronto_data4 = Geomerge_df[Geomerge_df['Borough'] == 'West Toronto'].reset_index(drop=True)
frames=[toronto_data1,toronto_data2,toronto_data3,toronto_data4]
toronto_data=pd.concat(frames)     
toronto_data.head()


# Let's get the latitude and longitude for Downtown Toronto.

# Visualize the Toronto boroughs with their neighbourhoods.

# In[114]:



# create map of Manhattan using latitude and longitude values
toronto_map = folium.Map(location=[latitude, longitude], zoom_start=12)

# add markers to map
for lat, lng, label in zip(toronto_data['Latitude'], toronto_data['Longitude'], toronto_data['Borough']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(toronto_map)  
    
toronto_map


# Let's cluster the neighbourhoods in Downtown Toronto.

# In[115]:


# Onehot coding
toronto_data_onehot = pd.get_dummies(toronto_data[['Neighbourhood']], prefix="", prefix_sep="")

# add Borough column back to dataframe
toronto_data_onehot['Borough'] = toronto_data['Borough'] 

# move neighborhood column to the first column
fixed_columns = [toronto_data_onehot.columns[-1]] + list(toronto_data_onehot.columns[:-1])
toronto_data_onehot = toronto_data_onehot[fixed_columns]

toronto_data_onehot.head(10)


# Group the rows by boroughs and by taking the mean of the frequency of occurrence of each category.

# In[116]:


toronto_grouped =toronto_data_onehot.groupby('Borough').mean().reset_index()
toronto_grouped


# Cluster the neighbourhoods in Central Toronto, Downtown Toronto, East Toronto and West Toronto.

# In[117]:


from sklearn.cluster import KMeans
# set number of clusters
kclusters = 4

toronto_clustering = toronto_grouped.drop('Borough', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(toronto_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:3] 


# Visualize the clusters of the neighbourhoods in Central Toronto, Downtown Toronto, East Toronto and West Toronto on the map.

# In[118]:


# Add cluster labels
toronto_grouped.insert(0,"Cluster label",kmeans.labels_)


# In[119]:


toronto_data=toronto_data.join(toronto_grouped.set_index("Borough"),on="Borough")
toronto_data.head()


# In[120]:



# create map
map_clusters = folium.Map(location=[latitude, longitude], zoom_start=11.5)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(toronto_data['Latitude'], toronto_data['Longitude'], toronto_data['Borough'],toronto_data['Cluster label']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.8).add_to(map_clusters)
       
map_clusters


# There we have the map of Toronto City with the four boroughs with Toronton in their names (Central Toronto, Downtown Toronto, East Toronto and West Toronto) superimposed on it. Each color represents a different borough, while each dot represents a neighbbourhood. To see which borough and cluster a dot represents, hover the cursor over the dot and click on it.

# # Thanks for reading!

# In[ ]:




