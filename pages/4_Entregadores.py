import streamlit as st
from PIL import Image
import data_tools
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib as plt
import folium
from streamlit_folium import folium_static


#IMPORT DATASET
df = pd.read_csv('train.csv')

#CLEAN DATASET 
df1 = data_tools.clean_df(df)



#==============================================================================================================================
#-----------------------------------------LAYOUT NO STREAMLIT------------------------------------------------------------------
#==============================================================================================================================


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=-= SIDEBAR 
#image = 'bike-delivery.png'
#image = Image.open(image)
#st.sidebar.image(image, width=120)
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery In Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')


data_slider = st.sidebar.slider(
    'Até: ',
    value=pd.datetime(2022, 3, 8),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

fdate = str(data_slider)
fdate = fdate.replace(' 00:00:00', '')

st.sidebar.markdown("""---""")

filtro_trafego = st.sidebar.multiselect(
    'Quais condições de trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])


#--------------------------------------------------- Filtros de data
lines = df1['Order_Date'] < data_slider
df1 = df1.loc[lines, :]

#--------------------------------------------------- Filtros de trânsito
lines = df1['Road_traffic_density'].isin(filtro_trafego)
df1 = df1.loc[lines, :]


#==============================================================================================================================
#---------------------------------------------BODY----------------------------------------------------------------------------
#==============================================================================================================================
st.header('MARKETPLACE - VISÃO ENTREGADORES')

tab1, tab2 = st.tabs(['Visão Gerencial', '_'])

with tab1:
    with st.container():
        st.title( 'Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior = df1['Delivery_person_Age'].max()
            col1.metric("Maior Idade", maior)
        with col2:
            menor = df1['Delivery_person_Age'].min()
            col2.metric("Menor Idade", menor)
        with col3:
            melhor = df1['Vehicle_condition'].max()
            col3.metric('Melhor condição de veículo', melhor)
        with col4:
            pior = df1['Vehicle_condition'].min()
            col4.metric('Pior condição de veículo', pior)
    with st.container():
        st.markdown("""---""")
        st.title('Avaliaçãoes')
        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.subheader('Avaliações médias por entregador')
            st.dataframe(df1.groupby('Delivery_person_ID').agg({'Delivery_person_Ratings' : 'mean'}))
        with col2:
            st.subheader('Avaliação média por transito')
            df_aux = df1.groupby('Road_traffic_density').agg({'Delivery_person_Ratings': ['mean', 'std']}).reset_index()
            df_aux.columns = ['Densidade', 'Média', 'Desvio Padrão']
            st.dataframe(df_aux)
            
            st.subheader('Avaliação média por clima')
            df_aux = df1.groupby('Weatherconditions').agg({'Delivery_person_Ratings': ['mean', 'std']})
            df_aux.columns = ['Média', 'Desvio']
            df_aux.reset_index()
            st.dataframe(df_aux)
            
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Top entregadores mais rápidos')
            df2 = (df1[['Delivery_person_ID', 'City', 'Time_taken(min)']]
                   .groupby(['City', 'Delivery_person_ID'])
                   .min().sort_values(['City', 'Time_taken(min)'], ascending=True)
                   .reset_index())
            
            df01 = df2.loc[df2['City']=='Metropolitian', :].head(10)
            df02 = df2.loc[df2['City']=='Urban', :].head(10)
            df03 = df2.loc[df2['City']=='Semi-Urban', :].head(10)
            df_aux = pd.concat([df01, df02, df03]).reset_index(drop=True)
            st.dataframe(df_aux)
            
        with col2:
            st.subheader('Top entregadores mais lentos')
            df2 = (df1[['Delivery_person_ID', 'City', 'Time_taken(min)']]
                   .groupby(['City', 'Delivery_person_ID'])
                   .min().sort_values(['City', 'Time_taken(min)'], ascending=True)
                   .reset_index())
            
            df01 = df2.loc[df2['City']=='Metropolitian', :].tail(10)
            df02 = df2.loc[df2['City']=='Urban', :].tail(10)
            df03 = df2.loc[df2['City']=='Semi-Urban', :].tail(10)
            df_aux = pd.concat([df01, df02, df03]).reset_index(drop=True)
            st.dataframe(df_aux)
            
            
            