import streamlit as st
import altair as alt
import pandas as pd
import numpy as np


crimes_sum = pd.read_csv("./data/sum_cr_r_q.csv", index_col=0)
crimes_sum["year"] = crimes_sum['Quarter'].apply(lambda x: int(str(x).split("-")[0]) if not pd.isna(x) else x)
crimes_sum['TikimSum'] = crimes_sum['TikimSum'].apply(lambda x: int(x.replace(',', '')) if not pd.isna(x) else x)

sum_by_year = crimes_sum.groupby('year')['TikimSum'].sum()


st.header("Crime Records Visualization")
st.write("This is a web app to visualize crime records in Israel.")

# line plot for total TikimSum in each year, x axis is year, y axis is TikimSum
st.subheader("Total Crime Records Each Year")
# st.line_chart(sum_by_year[sum_by_year.index != 2023])
summary_by_year = crimes_sum.groupby('year')['TikimSum'].agg(['sum', 'mean']).reset_index()

# Plotting
st.title("Sum and Average of 'TikimSum' by Year (excluding 2023)")
chart = alt.Chart(summary_by_year).mark_line().encode(
    x='Year',
    y='sum',
    color=alt.value('blue'),
    tooltip=['Year', 'sum']
).properties(
    width=600,
    height=400
)

chart += alt.Chart(summary_by_year).mark_line().encode(
    x='Year',
    y='mean',
    color=alt.value('red'),
    tooltip=['Year', 'mean']
)

st.altair_chart(chart)

# run the app with: streamlit run final_vis.py
