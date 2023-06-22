import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np


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


crimes_det = pd.read_csv("./data/cr_r_q_ft.csv", index_col=0)
felony_type = crimes_det['StatisticCrimeGroup'].value_counts(normalize=True).sort_values(ascending=False)

# pie chart for felony type
st.subheader("Felony Type")
st.write("The most common felony type is", felony_type.index[0], "with", round(felony_type[0]*100, 2), "% of all crimes.")

fig = px.pie(crimes_det, values=felony_type.values, names=felony_type.index, title='Felony Type')
st.plotly_chart(fig)
