!pip install seaborn
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import seaborn as sns
import time
import pydeck as pdk
import plotly.express as px


#Loading the data
@st.cache_data(show_spinner="Loading..")
def load_data(file):
    df_map = pd.read_csv(file)
    return df_map

st.title("Used Car Analysis")

cars_df = load_data('used_cars_data.csv')
    

cars_df['Brand'] = cars_df.Name.str.split().str.get(0)
cars_df['Model'] = cars_df.Name.str.split().str.get(1) + " " + cars_df.Name.str.split().str.get(2)



df_cities=cars_df['Location'].unique()
data_cordinates = {
    'Location': ['Mumbai', 'Pune', 'Chennai', 'Coimbatore', 'Hyderabad', 'Jaipur', 'Kochi', 'Kolkata', 'Delhi', 'Bangalore', 'Ahmedabad'],
    'Latitude': [19.0760, 18.5204, 13.0827, 11.0168, 17.3850, 26.9124, 9.9312, 22.5726, 28.6139, 12.9716, 23.0225],
    'Longitude': [72.8777, 73.8567, 80.2707, 76.9558, 78.4867, 75.7873, 76.2673, 88.3639, 77.2090, 77.5946, 72.5714]
}

df_cordinates=pd.DataFrame(data_cordinates)
df_cars = pd.merge(cars_df, df_cordinates, on='Location', how='left')

# Aggregate to get the average price for each city
df_avg_price_by_city = df_cars.groupby(['Location','Latitude','Longitude']).agg({'Price': 'mean'}).reset_index()

# Rename columns for clarity
df_avg_price_by_city.rename(columns={'Price': 'Average_Price'}, inplace=True)
df_avg_price_by_city['Price_in_thousands']=round(df_avg_price_by_city['Average_Price']*100,1)
df_avg_price_by_city['Price']=df_avg_price_by_city['Price_in_thousands'].astype(str) + "K"

latitude=df_cars['Latitude'].mean()
longitude=df_cars['Longitude'].mean()
token = "pk.eyJ1Ijoia3NvZGVyaG9sbTIyIiwiYSI6ImNsZjI2djJkOTBmazU0NHBqdzBvdjR2dzYifQ.9GkSN9FUYa86xldpQvCvxA" # you will need your own token

fig1 = px.scatter_mapbox(df_avg_price_by_city, lat='Latitude', lon='Longitude',
                hover_name='Location', hover_data=['Price'],
                color_discrete_sequence=["fuchsia"],zoom=4) #base layout mapbox contains configuration 
                                                            #information for the map itself and defines the lowest layers. 

fig1.update_traces(marker={'size': 15}) #Size of the marker

fig1.update_layout(mapbox_style="mapbox://styles/mapbox/satellite-streets-v12",
                mapbox_accesstoken=token)  #Choose the style for the map

fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# Display the map in Streamlit
st.subheader('Average Car Price by Location in India')
st.plotly_chart(fig1,use_container_width=True)




#Calculate Average Price based on Brand, Model and Year
st.markdown("Choose the Brand, Model and year to know the average price of the car")

selected_Brand = st.selectbox('Select the Brand of car  ',cars_df.Brand.unique())
selected_Model = st.selectbox('Select the Model of car  ',cars_df[cars_df.Brand==selected_Brand].Model.unique())
selected_Year = st.selectbox('Select the Year  ',cars_df[(cars_df.Brand==selected_Brand) & (cars_df.Model==selected_Model)].Year.unique())
cars_df_filtered=cars_df[(cars_df.Brand==selected_Brand) & (cars_df.Model==selected_Model) & (cars_df.Year==selected_Year)]

# Calculate the average price
average_price = cars_df_filtered['Price'].mean()


# Display the average price using st.markdown
st.markdown(f'The average price of the car is: **{average_price * 100000:.2f}**')





#Average Price through Bar Chart
st.subheader('Average Car Price in India')
#sel_year = st.selectbox('Select the Year  ',cars_df.Year.unique())
df_avg_price_by_city_new = cars_df_filtered.groupby(['Location']).agg({'Price': 'mean'}).reset_index()

# Rename columns for clarity
df_avg_price_by_city_new.rename(columns={'Price': 'Average_Price'}, inplace=True)
df_avg_price_by_city_new['Formatted_Price']=round(df_avg_price_by_city_new['Average_Price']*100,2)
df_avg_price_by_city_new['Price_K']=df_avg_price_by_city_new['Formatted_Price'].astype(str) + "K"

# Filter the DataFrame to include only the top 5 brands
df_top_5 = df_avg_price_by_city_new.nlargest(5, 'Average_Price')


chart = (
    alt.Chart(df_top_5)
    .mark_bar()  # Use bar mark for bar chart
    .encode(
        x=alt.X('Formatted_Price:Q', title='Average Price', axis=alt.Axis(format='~s')),  # Format x-axis
        y=alt.Y('Location:N', title='Location').sort('-x'),  # Sort by average price
        color=alt.Color('Formatted_Price:Q', scale=alt.Scale(scheme='viridis'), title='Average Price'),
        tooltip=[
            alt.Tooltip('Location:N', title='Location'),
            alt.Tooltip('Price_K', title='Average Price')
        ]
    )
    .properties(
        title='Top 5 Cities by Average Car Price',
        height=300,  # Set the height of the chart
        width=600    # Set the width of the chart
    )
)

# Display the chart
st.altair_chart(chart, use_container_width=True)
