# -*- coding: utf-8 -*-
"""Roshni-DrugRecommendation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fb_aAJAsmWdy3cVV9okNg9eTUh8AIl8t
"""

import pandas as pd
import streamlit as st

df = pd.read_csv('clean_drugs.csv')


# Content Based

df.drop_duplicates(subset=['review'],inplace=True)

# Creates a column that contains a combination of drugs and conditions
original_df = df.copy()
df = df.sample(n=15000, replace=True,random_state=1289)
df = df.reset_index()
df['soup'] = df['review']+" "+df['condition']
df.dropna(axis=0, inplace=True)

from sklearn.feature_extraction.text import HashingVectorizer,TfidfVectorizer, CountVectorizer
# Vectorizes words to numbers and builds a sparse matrix
count = CountVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
count_matrix = count.fit_transform(df['soup'])

from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
#Computes similarity between drugs using cosine similarity metric
cosine_sim = cosine_similarity(count_matrix, count_matrix)

df = df.reset_index()
titles = df[['condition','drugName']]
indices = pd.Series(df.index, index=[df['condition'],df['drugName']])

# Collaborative Based

from surprise import Reader, Dataset
#Define a Reader object-The Reader object helps in parsing the file or dataframe containing ratings
reader = Reader()

#df_content=df
#df=original_df
# label encoding
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
df['drugId']= le.fit_transform(df['drugName'])
df['condId']= le.fit_transform(df['condition'])

reader = Reader()
#Create dataset to be used for building the filter
data = Dataset.load_from_df(df[['uniqueID', 'drugId','rating']], reader)


# Hybrid Based

id_map=df[['uniqueID','drugId','drugName']]
id_map.columns = ['uniqueID','drugId','drugName']
id_map = id_map.merge(df[['condition', 'uniqueID']], on='uniqueID').set_index('condition')
id_map.drop_duplicates(inplace=True)
indices_map = id_map.set_index('uniqueID')

def hybrid(userId,drugName,condition):
    
    #Extract index of durg and condition
    idx = indices[condition,drugName]
    
    #Extract the similarity scores and their corresponding index for every drug from the cosine similarity matrix
    #print(idx)
    sim_scores = list(enumerate(cosine_sim[int(idx[0])]))
    #Sort the (index,score) tuples in decreasing order of similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    #Select top 25
    sim_scores = sim_scores[1:26]
    #Store the cosine_sim indices of the top 25 drug in a list
    drug_indices = [i[0] for i in sim_scores]
    
    #Extract metadata of the drug
    drugs = df.iloc[drug_indices][['drugName','drugId', 'rating', 'uniqueID','condition']]
    
    drugs = drugs.sort_values(by='rating', ascending=False)
    #Return top 10 drugs as recommendations
    return drugs.head(10)

try:
    st.title("Drug Recommendation System")
    st.subheader("Fill out your details below: ")
    id = st.number_input("Enter your User ID", 1, 1000000)
    id=int(id)
    drug = st.text_input("Enter Drug Name")
    condition = st.text_input("Enter Condition")
    st.subheader("Similar Drugs recommended are:")
    st.dataframe(hybrid(id, drug, condition))
except:
    st.info("Do not leave any input as blank.")
