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
st.sidebar.image(image, width=120)
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
st.header('MARKETPLACE - VISÃO EMPRESA')

#-----------------TABS

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:


    # 1 - QUANTIDADE DE PEDIDOS POR DIA
    with st.container():
        st.markdown('# Pedidos por dia')
        colunas = df1[['ID', 'Order_Date']]
        ordersperday = colunas.groupby('Order_Date')['ID'].count().reset_index()
        fig = px.bar(ordersperday, x='Order_Date', y='ID')
        st.plotly_chart(fig, use_container_width=True)
    
    # Colunas
    with st.container():
        col1 , col2 = st.columns(2)
        with col1:
            st.header('Pedidos por tipo de Tráfego')
            colunas3 = df1[['Road_traffic_density', 'ID']]
            ordersbytraffic = colunas3.groupby('Road_traffic_density').count().reset_index()
            ordersbytraffic.rename(columns={'ID':'Orders'}, inplace=True)
            total = ordersbytraffic['Orders'].sum()
            ordersbytraffic['Percent'] = ordersbytraffic['Orders'] / total

            #Plotar um pieplot (gráfico de pizza)
            fig = px.pie(ordersbytraffic, values='Percent', names='Road_traffic_density')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.header('Entregas por Cidade e por Tráfego')
            colunas4 = df1[['ID', 'City', 'Road_traffic_density']].dropna()

            df_aux = colunas4.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
            df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

            #Plotar o gráfico de bolhas(gráfico de disperção)
            fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID')
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        st.markdown('# Pedidos por semana')
        #Criar uma nova coluna para indicar as semanas do anos
        df1['Week_of_year'] = df1['Order_Date'].dt.strftime('%U') # utiliza o atributo .dt para formatar a nova coluna
        colunas2 = df1[['Week_of_year', 'ID']] #Seleciona apenas as colunas a serem utilizadas
        ordersperweek = colunas2.groupby('Week_of_year')['ID'].count().reset_index() #É necessário utilizar o reset_index para que week_of_year também seja considerado como coluna

        #plotar gráfico de barras com plotly
        #px.bar(ordersperweek, x='Week_of_year', y='ID')

        #plotar um gráfico de linhas
        fig = px.line(ordersperweek, x='Week_of_year', y='ID')
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        st.markdown('# Entregas semanais por entregador')
        # Quantidade de pedidos por semana / numero de entregadores únicos da semana
        df_aux01 = df1.loc[:, ['ID', 'Week_of_year']].groupby('Week_of_year').count().reset_index()
        df_aux02 = df1.loc[:, ['Delivery_person_ID', 'Week_of_year']].groupby('Week_of_year').nunique().reset_index()

        df_aux = pd.merge(df_aux01, df_aux02, how='inner')
        df_aux['order_by_deliverer'] = df_aux['ID'] / df_aux['Delivery_person_ID']

        #plotar o gráfico
        fig = px.line(df_aux, x='Week_of_year', y='order_by_deliverer')
        st.plotly_chart(fig, use_container_width=True)
        
with tab3:
    with st.container():
        st.markdown('# Localização central de cada tipo de tráfego')
        
        #Mapa
        df_aux = df1.loc[: , ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
        df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
        df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
        df_aux = df_aux.reset_index()
        
        coordenadas = []
        for i in range(len(df_aux)):
            loc = {}
            loc['name'] = df_aux.loc[i, 'City'] + ' ' + df_aux.loc[i, 'Road_traffic_density']
            loc['location'] = [df_aux.loc[i, 'Delivery_location_latitude'], df_aux.loc[i, 'Delivery_location_longitude']]

            coordenadas.append(loc)
        
        mapa = folium.Map(location=[df_aux.loc[0, 'Delivery_location_latitude'],df_aux.loc[0, 'Delivery_location_longitude']], zoom_start=5)
        for i in coordenadas:
            folium.Marker(location=i['location'], popup=i['name']).add_to(mapa)
        
        folium_static(mapa, width=800, height=600)

