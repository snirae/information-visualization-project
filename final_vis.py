import streamlit as st
import pydeck as pdk
import plotly.express as px
import pandas as pd
import numpy as np
import zipfile
import io
import plotly.graph_objects as go
import json
from scipy import stats


# run the app with: streamlit run final_vis.py
st.header("Crime Records Visualization")

########################################################################################################################

crimes_sum = pd.read_csv("./data/sum_cr_r_q.csv", index_col=0)
crimes_sum["year"] = crimes_sum['Quarter'].apply(lambda x: int(str(x).split("-")[0]) if not pd.isna(x) else x)
crimes_sum['TikimSum'] = crimes_sum['TikimSum'].apply(lambda x: int(x.replace(',', '')) if not pd.isna(x) else x)

sum_by_year = crimes_sum.groupby('year')['TikimSum'].sum().reset_index()
sum_by_year["Year"] = sum_by_year["year"]
sum_by_year['Total Crime Records'] = sum_by_year['TikimSum']
sum_by_year = sum_by_year.drop(['year', 'TikimSum'], axis=1)

# line plot for total TikimSum in each year, x axis is year, y axis is TikimSum
st.subheader("Total Crime Records Each Year")
fig = px.line(sum_by_year[sum_by_year['Year'] < 2023], x="Year", y="Total Crime Records")
# change grid color
fig.update_layout(font_size=18,
                  xaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='LightPink'),
                  yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='LightPink'))
fig.update_traces(line_color='red')
fig.update_traces(line=dict(width=3))
fig.update_traces(mode="markers+lines")
st.plotly_chart(fig)


########################################################################################################################


with zipfile.ZipFile("./data/cr_r_q_ft.csv.zip", 'r') as zip_ref:
    csv = zip_ref.read('cr_r_q_ft.csv')
    crimes_det = pd.read_csv(io.BytesIO(csv), index_col=0)

districts = pd.read_csv("./data/districts.csv")
districts['density'] = districts['population'] / districts['area']


crimes_det["year"] = crimes_det['Quarter'].apply(lambda x: int(str(x).split("-")[0]) if not pd.isna(x) else x)
district = crimes_det[crimes_det['year'] == 2022]
district['district'] = district['PoliceDistrict'].apply(lambda x: x.split(" ")[-1] if not pd.isna(x) else x)
district = district.groupby('district').agg({'TikimSum': 'sum', 'StatisticCrimeGroup': stats.mode}).reset_index()

district = district.merge(districts, on='district')
district['crimes_per_100k'] = district['TikimSum'] / (district['population'] / 100000)

texts = []
for row in district.iterrows():
    text = f"""
    District: {row[1]['district']}<br>
    Population: {row[1]['population']:,}<br>
    Area: {row[1]['area']:,} km<sup>2</sup><br>
    Population density: {row[1]['density']:,} people/km<sup>2</sup><br>
    <b>Crime records per 100k people: {round(row[1]['crimes_per_100k'], 2):,}</b><br>
    Total crime records: {row[1]['TikimSum']:,}<br>
    Most common crime: {row[1]['StatisticCrimeGroup'][0][0]} (count: {row[1]['StatisticCrimeGroup'][1][0]:,})<br>
    """
    texts.append(text)

district['text'] = texts


# choropleth map for crime records in each canton
st.subheader("Crime Records in Each District")
st.write("The darker the color, the more crime records in that district.")

geojson_path = "data/map.geojson"
with open(geojson_path) as f:
    geo = json.load(f)

fig = go.Figure(
    go.Choroplethmapbox(
        geojson=geo,
        locations=district.district.apply(lambda x: x.split(" ")[-1]),
        featureidkey="properties.heb_name",
        z=district.crimes_per_100k,
        text=district.text,
        # hovertemplate='%{text}',
        colorscale="sunsetdark",
        marker_opacity=0.5,
        marker_line_width=0,
    )
)
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=6.6,
    mapbox_center={"lat": 31.5, "lon": 34.8516},
    width=800,
    height=600,
)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
st.plotly_chart(fig)


########################################################################################################################


felony_type = crimes_det['StatisticCrimeGroup'].value_counts(normalize=True).sort_values(ascending=False)
felony_type = felony_type[0:5]
felony_type['Other'] = 1 - felony_type.sum()

# pie chart for felony type
st.subheader("Felony Type")
st.write("The most common felony type is", felony_type.index[0], "with", round(felony_type[0]*100, 2), "% of all crimes.")

fig = px.pie(crimes_det, values=felony_type.values, names=felony_type.index)
fig.update_layout(
    autosize=False,
    width=800,
    height=800,
    font_size=20,
)
st.plotly_chart(fig)


########################################################################################################################


st.subheader("Crime Records Difference in Percentage For The Last 5 Years")

sum_by_district_year = crimes_sum.groupby(['PoliceDistrict', 'year'])['TikimSum'].sum().reset_index()
sum_by_district_year['District'] = sum_by_district_year['PoliceDistrict']
sum_by_district_year.dropna(inplace=True)

# new df that shows the difference in percentage betweeen TikimSum in 2018 and 2022 for each district
df = sum_by_district_year.pivot(index='District', columns='year', values='TikimSum').reset_index()
df['Difference'] = (df[2022] - df[2018]) / df[2018] * 100
df = df.sort_values(by='Difference', ascending=False)

# Create a horizontal bar plot using Plotly Express
fig = px.bar(df, x='Difference', y='District', orientation='h', color='Difference', 
             color_continuous_scale='RdBu', labels={'Difference': 'Crime Rate Difference'})

# Add a line at y=0
fig.add_shape(type='line', x0=0, x1=0, y0=-0.5, y1=len(df)-0.5, line=dict(color='black', width=2))

# Customize the layout
fig.update_layout(
    title='Crime Rate Difference by District',
    xaxis_title='Difference',
    yaxis_title='District',
    # as higher values are worse, we want the colors to be red
    coloraxis_colorbar=dict(title='Difference', tickvals=[-50, 0, 50], ticktext=['-50%', '0%', '50%']),
    plot_bgcolor='white',
    paper_bgcolor='white',
    font_color='black',
    # yaxis=dict(tickmode='array', tickvals=df.index, ticktext=df['District']),
    width=700,
    height=500,
)


# Show the horizontal bar plot
st.plotly_chart(fig)
