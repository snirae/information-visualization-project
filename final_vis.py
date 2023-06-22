import streamlit as st
import pandas as pd
import numpy as np


crimes_sum = pd.read_csv("./data/sum_cr_r_q.csv")
print(crimes_sum.head(10))

crimes_sum["year"] = crimes_sum['Quarter'].apply(lambda x: int(str(x).split("-")[0]) if not pd.isna(x) else x)
print(crimes_sum["year"].head(10))

st.header("Crime Records Visualization")

st.write("This is a web app to visualize crime records in the US.")

# line plot for total crime records each year
st.subheader("Total Crime Records Each Year")
st.line_chart(crimes_sum.groupby("year").size())

# run the app with: streamlit run final_vis.py
