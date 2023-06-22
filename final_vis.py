import streamlit as st
import pandas as pd


crimes_detailed = pd.read_csv("./data/cr_r_q_ft.csv")
crimes_detailed["year"] = crimes_detailed['Quarter'].apply(lambda x: int(x.split("-")[0]))

st.header("Crime Records Visualization")

st.write("This is a web app to visualize crime records in the US.")

# line plot for total crime records each year
st.subheader("Total Crime Records Each Year")
st.line_chart(crimes_detailed.groupby("year").size())

# run the app with: streamlit run final_vis.py
