import streamlit as st
import plotly.express as px
import pandas as pd
import zipfile
import io
import plotly.graph_objects as go
import json
from scipy import stats


# run the app with: streamlit run final_vis.py
st.header("Crime Records Visualization")


crimes_sum = pd.read_csv("./data/sum_cr_r_q.csv", index_col=0)
crimes_sum["year"] = crimes_sum['Quarter'].apply(lambda x: int(str(x).split("-")[0]) if not pd.isna(x) else x)
crimes_sum['TikimSum'] = crimes_sum['TikimSum'].apply(lambda x: int(x.replace(',', '')) if not pd.isna(x) else x)


########################################################################################################################


# choropleth map for crime records in each district
st.subheader("Crime Records in Each District")
st.write("The darker the color, the more crime records per 100k people in that district.")


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

sum_by_district_year = crimes_sum.groupby(['PoliceDistrict', 'year'])['TikimSum'].sum().reset_index()
sum_by_district_year['District'] = sum_by_district_year['PoliceDistrict'].apply(lambda x: x.split(" ")[-1] if not pd.isna(x) else x)
sum_by_district_year.dropna(inplace=True)

# insert to district df the difference in crime records between 2018 and 2022
df = sum_by_district_year.pivot(index='District', columns='year', values='TikimSum').reset_index()
df['Difference'] = (df[2022] - df[2018]) / df[2018] * 100

diff = []
for row in district.iterrows():
    diff.append(df[df['District'] == row[1]['district']]['Difference'].values[0])

district['Difference'] = diff

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
    Difference in crime records between 2018 and 2022: {round(row[1]['Difference'], 2):,}%<br>
    """
    texts.append(text)

district['text'] = texts


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


# pie chart for felony type
st.subheader("Felony Type")


felony_type = crimes_det['StatisticCrimeGroup'].value_counts(normalize=True).sort_values(ascending=False)
felony_type = felony_type[0:5]
felony_type['Other'] = 1 - felony_type.sum()


st.write("The most common felony type is", felony_type.index[0], "with", round(felony_type[0]*100, 2), "% of all crimes.")


fig = px.pie(crimes_det, values=felony_type.values, names=felony_type.index)
fig.update_layout(
    autosize=False,
    width=700,
    height=700,
    font_size=18,
)
st.plotly_chart(fig)


########################################################################################################################


# line plot for total TikimSum in each year, x axis is year, y axis is TikimSum
st.subheader("Total Crime Records Each Year")


sum_by_year = crimes_sum.groupby('year')['TikimSum'].sum().reset_index()
sum_by_year["Year"] = sum_by_year["year"]
sum_by_year['Total Crime Records'] = sum_by_year['TikimSum']
sum_by_year = sum_by_year.drop(['year', 'TikimSum'], axis=1)


fig = px.line(sum_by_year[sum_by_year['Year'] < 2023], x="Year", y="Total Crime Records")
fig.update_layout(font_size=18,
                  xaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='LightPink'),
                  yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='LightPink'))
fig.update_traces(line_color='red')
fig.update_traces(line=dict(width=3))
fig.update_traces(mode="markers+lines")
st.plotly_chart(fig)


########################################################################################################################

# select any number of cities and see the crime records for each quarter in each year for comparison in a line plot
st.subheader("Comparison Between Crime Records in Multiple Cities")


grouped_city = crimes_sum.groupby(['Settlement_Council', 'Quarter'])['TikimSum'].sum().reset_index()
cities = st.multiselect("Choose cities", grouped_city['Settlement_Council'].unique())
cities_df = grouped_city[grouped_city['Settlement_Council'].isin(cities)]

fig = go.Figure()
for city in cities:
    city_df = cities_df[cities_df['Settlement_Council'] == city]
    fig.add_trace(go.Scatter(x=city_df['Quarter'], y=city_df['TikimSum'],
                        mode='lines+markers',
                        name=city,
                        line=dict(width=3)))
    
fig.update_layout(
    xaxis_title='Quarter',
    yaxis_title='Crime Records',
    width=800,
    height=500,
    font_size=16,
)
fig.update_layout(xaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='LightPink'),
                  yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='LightPink'))
st.plotly_chart(fig)
