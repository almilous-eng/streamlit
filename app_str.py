import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import json
from copy import deepcopy
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

mpg_df_raw = load_data("../data/mpg.csv")
mpg_df = deepcopy(mpg_df_raw)
st.title("Introduction to Streamlit")
st.header("MPG Data Exploration")

if st.checkbox("Show Dataframe"):
    st.subheader("This is my dataset:")
    st.dataframe(mpg_df)


# left_col, right_col = st.columns(2)

# left_col.button("I am a button")

# with right_col:
#     st.write("This is text")

left_column, middle_column, right_column = st.columns([3,1,1])
# left_column: 3 / 5 of the width

years = ["All"] + sorted(pd.unique(mpg_df["year"]))
year = left_column.selectbox("Choose a year", years)

show_means = middle_column.radio("Show Class Means", ["Yes", "No"])

plot_types = ["Matplotlib", "Plotly"]
plot_type = right_column.radio("Choose Plot type", plot_types)


if year == "All":
    reduced_df = mpg_df
else:
    reduced_df = mpg_df[mpg_df["year"] == year]

means = reduced_df.groupby("class").mean(numeric_only=True)

# st.pyplot(m_fig)

#st.plotly_chart(p_fig)

if plot_type == "Matplotlib":
    # matplotlib
    m_fig, ax = plt.subplots(figsize = (10,8))
    ax.scatter(reduced_df["displ"], reduced_df["hwy"], alpha = 0.7)
    ax.set_title("Engine Size vs Highway Size Fuelage")
    ax.set_xlabel("Displacement (Liters)")
    ax.set_ylabel("MPG")

    if show_means == "Yes":
        ax.scatter(means["displ"], means["hwy"], alpha = 0.7, color = "red", label = "Class Means")
        # ax.legend()
    st.pyplot(m_fig)
else: #elif plot_type == "Plotly":
    # plotly
    p_fig = px.scatter(reduced_df, x = "displ", y = "hwy", opacity = 0.5,
                    range_x = [1,8], range_y = [10,50],
                    width = 750, height = 600, 
                    labels = {"displ": "Displacement (Liters)", "hwy" : "MPG"},
                    title = "Engine Size vs Highway Size Fuelage"                   
                    )
    p_fig.update_layout(title_font_size = 22)

    if show_means == "Yes":
        p_fig.add_trace(go.Scatter(x=means["displ"], y = means["hwy"], mode = "markers", marker = {"color": "red"}))
        p_fig.update_layout(showlegend = False)
    st.plotly_chart(p_fig)

url = "https://archive.ics.uci.edu/ml/datasets/auto+mpg"
st.write("Data Source", url)
#"This works too", url

