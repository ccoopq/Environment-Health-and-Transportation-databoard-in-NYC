import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
import time
import base64
from io import BytesIO
import folium
from folium import IFrame
from streamlit_folium import st_folium
import json
import requests
from urllib.parse import urlencode
from folium.plugins import HeatMap
from branca.colormap import linear

st.set_page_config(layout="wide")
# Streamlit page setup for Pollution, Vehicle Miles Traveled, and PM2.5 Deaths Dashboards
st.title('Environment, Health, and Transportation databoard in NYC')
col1, col2, col3 = st.columns([1, 1.2, 1.2])

# st.sidebar.header('Environment, Health, and Transportation databoard in NYC')
st.sidebar.write('## This dashboard was created on 10/04/2024 and contains data on Environment, \
                Health, and Transportation in New York City, with the aim of supporting \
                some research in related areas. All data comes from NYC OpenData (https://opendata.cityofnewyork.us/).')

# Load the processed data
data = pd.read_csv('Air_Quality_with_Coordinates.csv')

# -------------------------------------------------Pollution
with col1:
    # Streamlit page setup
    st.write('## Annual Average Pollution')
    st.sidebar.header('Filters For Annual Average Pollution')

    # Sidebar filters
    # selected_year = st.sidebar.selectbox('Select Year', options=data['Time Period'].unique())
    selected_region = st.sidebar.selectbox('Select Region', options=data['Geo Place Name'].unique(), key='pollution_region')
    selected_pollutant = st.sidebar.selectbox('Select Pollutant', options=['Fine particles (PM 2.5)', 'Nitrogen dioxide (NO2)'], key='polludtant')

    # Filtering data based on selection
    filtered_data = data[(data['Geo Place Name'] == selected_region) & (data['Name'] == selected_pollutant)]
    # Further filter the data for rows where 'Time Period' contains 'Annual Average'
    filtered_data = filtered_data[filtered_data['Time Period'].str.contains('Annual Average', na=False)]
    # Extract the year from 'Time Period' and sort by year
    filtered_data['Year'] = filtered_data['Time Period'].str.extract(r'(\d{4})').astype(int)
    filtered_data = filtered_data.sort_values(by='Year')

    # Display filtered data and plot
    if not filtered_data.empty:
        st.write(f"#### Annual Average Pollution of {selected_pollutant} in {selected_region}")
        st.write(filtered_data)
        
        # Plotting the data with Year on the x-axis and Data Value on the y-axis using Streamlit
        st.bar_chart(data=filtered_data.set_index('Year')['Data Value'])
    else:
        st.error("No annual average data available for the selected filters.")

# ------------------------------------------------- Annual vehicle miles traveled
with col2:
    # Streamlit page setup
    st.write('## Annual Vehicle Miles Traveled')
    st.sidebar.header('Filters For Annual Vehicle Miles Traveled')

    # Sidebar filters
    selected_vehicles = st.sidebar.selectbox('Select Vehicles', options=['Annual vehicle miles traveled (cars)', 'Annual vehicle miles traveled (trucks)'], key='vehicles')
    selected_years = st.sidebar.selectbox('Select Years', options=['2005', '2010', '2019'], key='time')

    # Filtering data based on selection
    filtered_data = data[(data['Name'] == selected_vehicles) & (data['Time Period'] == selected_years)]

    # Extract the year from 'Time Period' and sort by year
    filtered_data['Year'] = filtered_data['Time Period'].str.extract(r'(\d{4})').astype(int)

    # Display map with simulated bar chart[]
    if not filtered_data.empty:
        # Create a folium map centered around New York City
        folium_map = folium.Map(location=[40.7028, -73.900], zoom_start=10, tiles='CartoDB positron')

        # Iterate over each unique region and plot a "bar" at each location
        for _, row in filtered_data.iterrows():
            latitude = row['latitude']
            longitude = row['longitude']
            data_value = row['Data Value']

            # Define the rectangle coordinates to simulate a bar
            # Adjust the longitude slightly for the width of the bar
            width_offset = 0.002  # Offset to determine the width of the bar
            height_offset = data_value * 0.0005  # Scale the data value to determine the height

            # Create coordinates for a rectangle (bar) that represents the data value
            rectangle_coordinates = [
                [latitude, longitude - width_offset],  # Bottom left
                [latitude + height_offset, longitude - width_offset],  # Top left
                [latitude + height_offset, longitude + width_offset],  # Top right
                [latitude, longitude + width_offset],  # Bottom right
            ]

            # Add the rectangle to the map to simulate a bar chart
            folium.Polygon(
                locations=rectangle_coordinates,
                color='orange',
                fill=True,
                # fill_color='orange',
                fill_opacity=0.6,
                tooltip=f"{row['Geo Place Name']}: {data_value} {row['Measure Info']}"
            ).add_to(folium_map)

        # Display the folium map in Streamlit using st_folium
        st.write(f"#### Map of the Selected Vehicle Miles Traveled in {selected_years}")
        st_folium(folium_map, width=600, height=500)
    else:
        st.error("No data available for the selected filters.")

# -------------------------------------------------Deaths due to PM2.5
with col3:
    # Streamlit page setup
    st.write('## Deaths due to PM2.5 (over age 30)')
    st.sidebar.header('Filters For Deaths due to PM2.5')

    # Sidebar filters
    selected_region = st.sidebar.selectbox('Select Region', options=data['Geo Place Name'].unique(), key='drpm2.5_region')

    # Filtering data based on selection
    filtered_data = data[(data['Geo Place Name'] == selected_region) & (data['Name'] == 'Deaths due to PM2.5')]
    # Extract the year from 'Time Period' and sort by year
    filtered_data['Year'] = filtered_data['Time Period'].str.extract(r'(\d{4})').astype(int)
    filtered_data = filtered_data.sort_values(by='Year')

    # Display filtered data and plot
    if not filtered_data.empty:
        st.write(f"#### Deaths due to PM2.5 in {selected_region}")
        st.write(filtered_data)
        
        # Plotting the data with Year on the x-axis and Data Value on the y-axis using Streamlit
        st.line_chart(data=filtered_data.set_index('Year')['Data Value'])
    else:
        st.error("No annual average data available for the selected filters.")


# Load the processed data
data1 = pd.read_csv('NYC_Climate_Budgeting_Report__Forecast_of_Citywide_Emissions_20241004.csv')

# -------------------------------------------------Target Emissions
with col1:
    # Streamlit page setup
    st.write('## Target CO2 Emissions in NYC')
    st.sidebar.header('Filters For Target CO2 Emissions in NYC')

    # Sidebar filters 
    selected_source = st.sidebar.selectbox('Select Source', options=['Total','Electricity','Fuel Oil','Natural Gas','Steam','Transportation - Other','CNG Vehicles','Diesel Vehicles','Electric Vehicles','Gasoline Vehicles','Waste'], key='co2 source')
    
    # Filtering data based on selection
    filtered_data = data1[(data1['Source'] == selected_source) & (data1['Scenario'] == 'NYC Forecast')]
    # Extract the year from 'Time Period' and sort by year
    filtered_data['Year'] = filtered_data['Forecast Year']
    filtered_data = filtered_data.sort_values(by='Year')

    # Display filtered data and plot
    if not filtered_data.empty:
        st.write(f"#### Target CO2 Emissions of {selected_source} from 2023 to 2050 in NYC")
        st.write(filtered_data)
        
        # Plotting the data with Year on the x-axis and Data Value on the y-axis using Streamlit
        st.bar_chart(data=filtered_data.set_index('Year')['Metric tons of CO2e'])
    else:
        st.error("No annual average data available for the selected filters.")


# Load the processed data
population_data = pd.read_csv('New_York_City_Population_by_Borough__1950_-_2040_20241004.csv')

# -------------------------------------------------NYC Population
with col2:
    # Streamlit页面设置
    st.write('## New York City Population by Borough from 1950 to 2040')
    st.write("#### Click a region to see the bar chart")

    # 将年份转换为列
    years = [str(year) for year in range(1950, 2050, 10)]
    population_data_long = population_data.melt(id_vars=['Borough'], value_vars=years, var_name='Year', value_name='Population')

    # 加载GeoJSON数据
    geojson_path = "Borough Boundaries.geojson"
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)

    # 生成柱状图并转换为Base64编码的HTML图像
    def plot_to_base64(data, borough_name):
        plt.figure(figsize=(4, 3))
        plt.bar(data['Year'], data['Population'], color='skyblue')  # 使用条形图绘制，确保年份作为x轴
        ## plt.title(f'Population Trend for {borough_name}')
        plt.xlabel('Year', color='gray')
        plt.ylabel('Population', color='gray')
        plt.xticks(rotation=45, color='gray')
        plt.yticks(color='gray')
        # 隐藏图像上边和右边的边框
        ax = plt.gca()  # 获取当前的Axes2
        img = BytesIO()
        plt.savefig(img, format='png')
        plt.close()
        img.seek(0)
        base64_img = base64.b64encode(img.getvalue()).decode('utf-8')
        return f'<img src="data:image/png;base64,{base64_img}">'

    # 创建地图并添加柱状图的Popup
    def create_map(data, geojson):
        m = folium.Map(location=[40.7128, -73.9060], zoom_start=10, tiles='CartoDB positron')
        # 为每个区域添加柱状图的Popup
        for feature in geojson['features']:
            borough_name = feature['properties']['boro_name']
            borough_data = data[data['Borough'] == borough_name][['Year', 'Population']]
            popup_content = plot_to_base64(borough_data, borough_name)
            popup = folium.Popup(popup_content, max_width=800)
            folium.GeoJson(
                feature,
                style_function=lambda feature: {'color': 'black', 'fillColor': '#ffff00', 'weight': 1},
                highlight_function=lambda feature: {'weight':3, 'color':'green'},
                tooltip=borough_name
            ).add_child(popup).add_to(m)
        return m

    # 显示地图
    map_obj = create_map(population_data_long, geojson_data)
    st_folium(map_obj, width=480, height=480)


# -------------------------------------------------NYC Traffic Volume
with col3:
    st.write('## New York City Average Traffic Volume Distribution')

    def load_data():
        data = pd.read_csv('Traffic_Volume_Counts_20241004_with_Coordinates.csv')
        # 转换日期为 datetime 类型
        data['Date'] = pd.to_datetime(data['Date'])
        # 计算每条记录的总车流量
        data['Total Volume'] = data[[col for col in data.columns if 'AM' in col or 'PM' in col]].sum(axis=1)
        return data

    data = load_data()

    # 计算每个地点每天的平均车流量
    data['Year'] = data['Date'].dt.year
    # 聚合数据并计算平均值
    average_daily_volume = data.groupby(['Year', 'Latitude', 'Longitude']).agg({
        'Total Volume': 'mean'
    }).reset_index()

    # Streamlit 侧边栏
    st.sidebar.header('Filters For NYC Traffic Volume (Note: Not each roadway has data recoarded in the given year.)')
    years = average_daily_volume['Year'].unique()
    year_to_filter = st.sidebar.selectbox('Select Years', years)

    # 过滤数据
    filtered_data = average_daily_volume[average_daily_volume['Year'] == year_to_filter]
    st.write(f"#### Average Traffic Volume per day in {year_to_filter} (Drag the map to load the heat map)")

    # 创建地图对象
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)  # 可以调整中心点和初始缩放级别

    # 添加热力图层
    heat_map = HeatMap(data=filtered_data[['Latitude', 'Longitude', 'Total Volume']].values, radius=15).add_to(m)  # radius 控制每个点的影响半径

    # 添加颜色条
    min_vol = filtered_data['Total Volume'].min()
    max_vol = filtered_data['Total Volume'].max()
    colormap = linear.YlOrRd_09.scale(min_vol, max_vol)
    colormap.caption = '每天的平均车流量'  # 为颜色条添加标题
    colormap.add_to(m)

    # 将热力图层添加到地图
    heat_map.add_to(m)

    # 将Folium地图显示在Streamlit上
    from streamlit_folium import folium_static
    folium_static(m, width=500, height=500)
