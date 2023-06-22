import streamlit as st
import matplotlib.pyplot as plt
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
summary_by_year = crimes_sum.groupby('Year')['TikimSum'].agg(['sum', 'mean'])
plt.plot(summary_by_year.index, summary_by_year['sum'], label='Sum')
plt.plot(summary_by_year.index, summary_by_year['mean'], label='Average')
plt.xlabel('Year')
plt.ylabel('Value')
plt.legend()
st.pyplot(plt)

# run the app with: streamlit run final_vis.py
