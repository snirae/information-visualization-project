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


crimes_sum = pd.read_csv("./data/sum_cr_r_q.csv", index_col=0)
crimes_sum["year"] = crimes_sum['Quarter'].apply(lambda x: int(str(x).split("-")[0]) if not pd.isna(x) else x)
crimes_sum['TikimSum'] = crimes_sum['TikimSum'].apply(lambda x: int(x.replace(',', '')) if not pd.isna(x) else x)

sum_by_year = crimes_sum.groupby('year')['TikimSum'].sum()


st.header("Crime Records Visualization")
st.write("This is an app to visualize crime records in Israel.")

# line plot for total TikimSum in each year, x axis is year, y axis is TikimSum
st.subheader("Total Crime Records Each Year")
st.line_chart(sum_by_year[sum_by_year.index != 2023])


with zipfile.ZipFile("./data/cr_r_q_ft.csv.zip", 'r') as zip_ref:
    csv = zip_ref.read('cr_r_q_ft.csv')
    crimes_det = pd.read_csv(io.BytesIO(csv), index_col=0)

crimes_det["year"] = crimes_det['Quarter'].apply(lambda x: int(str(x).split("-")[0]) if not pd.isna(x) else x)
district = crimes_det[crimes_det['year'] == 2022]
district['district'] = district['PoliceDistrict'].apply(lambda x: x.split(" ")[-1] if not pd.isna(x) else x)
district = district.groupby('district').agg({'TikimSum': 'sum'}).reset_index()

# choropleth map for crime records in each canton
st.subheader("Crime Records in Each Canton")
st.write("The darker the color, the more crime records in that canton.")

geojson_path = "data/map.geojson"
with open(geojson_path) as f:
    geo = json.load(f)

fig = go.Figure(
    go.Choroplethmapbox(
        geojson=geo,
        locations=district.district,
        featureidkey="properties.heb_name",
        z=district.TikimSum,
        colorscale="sunsetdark",
        marker_opacity=0.5,
        marker_line_width=0,
    )
)
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=6.6,
    mapbox_center={"lat": 31.0461, "lon": 34.8516},
    width=800,
    height=600,
)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
st.plotly_chart(fig)



felony_type = crimes_det['StatisticCrimeGroup'].value_counts(normalize=True).sort_values(ascending=False)
felony_type = felony_type[0:5]
felony_type['Other'] = 1 - felony_type.sum()

# pie chart for felony type
st.subheader("Felony Type")
st.write("The most common felony type is", felony_type.index[0], "with", round(felony_type[0]*100, 2), "% of all crimes.")

fig = px.pie(crimes_det, values=felony_type.values, names=felony_type.index, title='Felony Type')
st.plotly_chart(fig)
