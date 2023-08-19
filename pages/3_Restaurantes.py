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
from haversine import haversine
import numpy as np




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
st.header('MARKETPLACE - VISÃO RESTAURANTES')

tab1, tab2 = st.tabs(['Visão Gerencial', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            #st.markdown('### Entregadores Únicos')
            qt_entr = df1['Delivery_person_ID'].nunique()
            col1.metric('Entregadores Únicos', qt_entr)
        with col2:
            
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df1['Distance'] = df1.loc[:, cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                                         (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ),axis=1)
            
            avg_distance = np.round(df1['Distance'].mean(), 2)
            col2.metric('Distância Média', avg_distance)
                       
            
        with col3:
            
            
            df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)':['mean', 'std']})
            df_aux.columns = ['Média', 'Desvio Padrão']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'Média'], 2)
            
            col3.metric('Tempo médio de entrega c/ Festival', df_aux)
            
            
        with col4:
            #st.markdown('### Desvio Padrão Entregas c/ Festival')
            df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)':['mean', 'std']})
            df_aux.columns = ['Média', 'Desvio Padrão']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'Desvio Padrão'], 2)
            
            col4.metric('Desvio Padrão entrega c/ Festival', df_aux)
            
        with col5:
            #st.markdown('### Tempo de Entrega Médio s/ Festival')
            df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)':['mean', 'std']})
            df_aux.columns = ['Média', 'Desvio Padrão']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'Média'], 2)
            
            col5.metric('Tempo médio de entrega s/ Festival', df_aux)
            
            
        with col6:
            #st.markdown('### Desvio Padrão Entregas s/ Festival')
            df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)':['mean', 'std']})
            df_aux.columns = ['Média', 'Desvio Padrão']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'Desvio Padrão'], 2)
            
            col6.metric('Desvio Padrão entrega s/ Festival', df_aux)
        
    st.markdown("""---""")
    with st.container():
        st.title('Tempo médio de entrega por cidade')
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
        df1['Distance'] = df1.loc[:, cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                                         (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ),axis=1)
        avg_distance = df1.loc[:, ['City', 'Distance']].groupby('City').mean().reset_index()
        fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['Distance'], pull=[0, 0.1, 0])])
        st.plotly_chart(fig)
        
        
    st.markdown("""---""")
    with st.container():
        st.title('Distribuição do tempo')
        col1, col2 = st.columns(2)
        with col1:
            
            df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)' : ['mean','std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            fig = go.Figure()
            fig.add_trace( go.Bar( name='Control',
                                  x=df_aux['City'],
                                  y=df_aux['avg_time'],
                                  error_y=dict( type='data', array=df_aux['std_time'])))
            fig.update_layout(barmode='group')
            st.plotly_chart(fig)
            
        with col2:
            
            cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
            df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)' : ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                             color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std_time']))
            st.plotly_chart(fig)
            
    st.markdown("""---""")
    with st.container():
        st.title('Distribuição da distância')
        cols = ['City','Time_taken(min)', 'Type_of_order']
        df_aux = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)' : ['mean', 'std']})
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
        st.table(df_aux)
        