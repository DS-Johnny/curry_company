import pandas as pd


def clean_df(df):
    df1 = df.copy()
    
    df1 = df.copy()

    #Eliminar espaço a mais
    df1['ID'] = df1.loc[:, 'ID'].str.strip()
    df1['Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1['Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1['Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1['Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1['Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1['City'] = df1.loc[:, 'City'].str.strip()

    #Converter Order_date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    #Eliminar linhas onde 'Delivery_person_Age' == 'NaN '
    selec_lines = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[selec_lines, :]

    #Formatar a coluna Weather conditions
    def cond_form(x):
        new = x.replace('conditions ', '')
        return new

    df1['Weatherconditions'] = df1['Weatherconditions'].apply(lambda x: cond_form(x))
    selec_lines = df1['Weatherconditions'] != 'NaN'
    df1 = df1.loc[selec_lines, :]

    #Formatar Road_traffic_density
    selec_lines = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[selec_lines, :]

    #Converter as idades para inteiros
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    #Converter notas para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    #Formatar coluna Time_taken(min)
    def tim_conv(x):
        new = x.replace('(min) ', '')
        return new

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: tim_conv(x))
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    #Formatar a coluna City
    selec_lines = df1['City'] != 'NaN'
    df1 = df1.loc[selec_lines, :]

    df1 = df1.reset_index(drop=True)
    
    return df1
