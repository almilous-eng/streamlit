import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(
    page_title="Global Volcano Dashboard",
    layout="wide"
)

# -------------------------------------------------------
# DATA LOADING
# -------------------------------------------------------
@st.cache_data

def load_data():
    with open('data/countries.geojson') as f:
        countries = json.load(f)

    volcanoes = pd.read_csv(
        'data/volcano_ds_pop.csv',
        sep=',',
        index_col=0
    )

    volcanoes['Number'] = volcanoes['Number'].str.replace(r'=$', '', regex=True)
    volcanoes['Number'] = volcanoes['Number'].str.replace(r'-$', '', regex=True)

    return volcanoes, countries


volcanoes, countries = load_data()

# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------
st.sidebar.title("Volcano Dashboard")

map_selection = st.sidebar.radio(
    "Select Map",
    [
        "Volcano Count",
        "Average Elevation",
        "Exposure Index"
    ]
)

log_scale = st.sidebar.toggle(
    "Log Scale Exposure Index",
    value=False
)

categorical_variable = st.sidebar.radio(
    "Categorical Variable",
    ["Type", "Status"]
)

plot_selection = st.sidebar.radio(
    "Categorical Plot Type",
    [
        "Stacked Bar",
        "Normalized Stacked Bar"
#        "Heatmap"
    ]
)

country_filter = st.sidebar.radio(
    "Country Filter",
    ["Top 10", "Top 20", "Top 50"]
)

country_n = {
    "Top 10": 10,
    "Top 20": 20,
    "Top 50": 50
}[country_filter]

# -------------------------------------------------------
# TITLE
# -------------------------------------------------------
st.title("Global Volcano Analysis Dashboard")
st.markdown("Interactive geospatial exploration of global volcano datasets.")

# -------------------------------------------------------
# AGGREGATIONS
# -------------------------------------------------------

# Volcano count
volcanoes_country = (
    volcanoes.groupby('Country')
    .size()
    .reset_index(name='Total Volcanoes')
)

# Mean elevation
mean_volc_elev = (
    volcanoes.groupby('Country')['Elev']
    .mean()
    .reset_index(name='Average Elevation')
)

# Exposure index
population = (
    volcanoes.groupby('Country')['Population (2020)']
    .first()
    .reset_index()
)

exposure = volcanoes_country.merge(population, on='Country')

exposure['Exposure Index'] = (
    exposure['Total Volcanoes'] /
    np.log(exposure['Population (2020)'])
)

if log_scale:
    exposure['Exposure Display'] = np.log1p(exposure['Exposure Index'])
    exposure_color = 'Exposure Display'
    exposure_title = 'Log Exposure Index'
else:
    exposure_color = 'Exposure Index'
    exposure_title = 'Exposure Index'

# -------------------------------------------------------
# MAPS
# -------------------------------------------------------

st.header("Geospatial Maps")

if map_selection == "Volcano Count":

    fig_map = px.choropleth_mapbox(
    volcanoes_country,
    geojson=countries,
    locations='Country',
    featureidkey='properties.ADMIN',
    color='Total Volcanoes',
    color_continuous_scale='YlOrRd',
    mapbox_style="carto-positron",
    zoom=1.3,
    center={"lat": 20, "lon": 0},
    )


    fig_map.update_traces(
    marker_line_width=0.5,
    marker_line_color="black",
    hovertemplate=(
        "Country: %{location}<br>"
        "Total Volcanoes: %{z}<extra></extra>"
    )
    )

    fig_map.update_coloraxes(
    colorbar=dict(
        title="Volcano Count",
        thickness=15
    )
    )

    fig_map.update_layout(
    title=dict(
        text="Volcanoes of the World",
        font=dict(size=22)
    ),
    height=700,
    margin={"r":0, "t":50, "l":0, "b":0},
    mapbox=dict(
        style="carto-positron"
    )
    )

elif map_selection == "Average Elevation":

    fig_map = px.choropleth_mapbox(
    mean_volc_elev,
    geojson=countries,
    locations='Country',
    featureidkey='properties.ADMIN',
    color='Average Elevation',
    color_continuous_scale='Viridis',
    mapbox_style='carto-positron',
    center={'lat': 20, 'lon': 0},
    zoom=3,
    hover_data={'Average Elevation': ':.0f'}
    )

    fig_map.update_traces(
    hovertemplate=(
        "Country: %{location}<br>"
        "Average Elevation: %{z:.0f} m<extra></extra>"
    )
    )

    fig_map.update_coloraxes(
    colorbar=dict(
        title="Elevation (m)",
        thickness=15
    )
    )

    fig_map.update_layout(
    title=dict(
        text="Average Volcano Elevation",
        font=dict(size=22)
    ),
    height=700,
    margin={"r":0, "t":50, "l":0, "b":0}
    )

elif map_selection == "Exposure Index":

    fig_map = px.choropleth_mapbox(
    exposure,
    geojson=countries,
    locations='Country',
    featureidkey='properties.ADMIN',
    color=exposure_color,
    color_continuous_scale='Plasma',
    mapbox_style='carto-positron',
    center={'lat': 20, 'lon': 0},
    zoom=3,
    hover_data={'Exposure Index': ':.3f'}
    )

    fig_map.update_traces(
    hovertemplate=(
        "Country: %{location}<br>"
        "Exposure Index: %{z:.3f}<extra></extra>"
    )
    )

    fig_map.update_coloraxes(
    colorbar=dict(
        title=exposure_title,
        thickness=15
    )
    )

    fig_map.update_layout(
    title=dict(
        text="Volcanic Exposure Index",
        font=dict(size=22)
    ),
    height=700,
    margin={"r":0, "t":50, "l":0, "b":0}
    )

st.plotly_chart(fig_map, use_container_width=True)

# -------------------------------------------------------
# CATEGORICAL ANALYSIS
# -------------------------------------------------------

st.header("📊 Categorical Volcano Analysis")

cat_df = (
    volcanoes.groupby(['Country', categorical_variable])
    .size()
    .reset_index(name='Count')
)

# Top countries filter

top_countries = (
    volcanoes['Country']
    .value_counts()
    .head(country_n)
    .index
)

cat_df = cat_df[cat_df['Country'].isin(top_countries)]

# -------------------------------------------------------
# STACKED BAR
# -------------------------------------------------------

if plot_selection == "Stacked Bar":

    fig_cat = px.bar(
        cat_df,
        x='Country',
        y='Count',
        color=categorical_variable,
        title=f'{categorical_variable} Distribution per Country'
    )

    fig_cat.update_layout(
        xaxis_tickangle=-45,
        height=700,
        legend_title=categorical_variable
    )

# -------------------------------------------------------
# NORMALIZED STACKED BAR
# -------------------------------------------------------

elif plot_selection == "Normalized Stacked Bar":

    cat_df['Percent'] = (
        cat_df.groupby('Country')['Count']
        .transform(lambda x: x / x.sum() * 100)
    )

    fig_cat = px.bar(
        cat_df,
        x='Country',
        y='Percent',
        color=categorical_variable,
        title=f'{categorical_variable} Percentage Distribution per Country'
    )

    fig_cat.update_layout(
        xaxis_tickangle=-45,
        height=700,
        yaxis_title='Percentage (%)',
        legend_title=categorical_variable
    )

# # -------------------------------------------------------
# # HEATMAP
# # -------------------------------------------------------

# elif plot_selection == "Heatmap":

#     heatmap_df = cat_df.pivot(
#         index='Country',
#         columns=categorical_variable,
#         values='Count'
#     )

#     heatmap_df = np.log1p(heatmap_df)  # Log transform for better visualization

#     fig_cat = go.Figure(
#         data=go.Heatmap(
#             z=heatmap_df.values,
#             x=heatmap_df.columns,
#             y=heatmap_df.index,
#             colorscale="Viridis",
#             colorbar=dict(
#                 title="Log(Count + 1)",
#                 thickness=15
#             ),
#             hoverongaps=False  # 🔥 prevents ghost hover
#         )
#     )

#     fig_cat.update_layout(
#         title=f'{categorical_variable} Heatmap by Country (Log Scale)',
#         height=700,
#         xaxis_title=categorical_variable,
#         yaxis_title="Country",
#         annotations=[
#             dict(
#                 text="Values shown as log(Count + 1)",
#                 showarrow=False,
#                 xref="paper",
#                 yref="paper",
#                 x=0,
#                 y=1.08,
#                 font=dict(size=12)
#             )
#         ]
#     )

st.plotly_chart(fig_cat, use_container_width=True)

# -------------------------------------------------------
# VOLCANO POINT MAP
# -------------------------------------------------------

st.header("🌋 Volcano Point Explorer")

volcanoes["Elev"] = pd.to_numeric(volcanoes["Elev"], errors="coerce")
volcanoes = volcanoes.dropna(subset=["Elev", "Latitude", "Longitude"])
volcanoes = volcanoes[volcanoes["Elev"] > 0]

# Optional: better visual scaling
volcanoes["Elev_scaled"] = volcanoes["Elev"] / volcanoes["Elev"].max() * 30

point_color = st.selectbox(
    "Point Color Variable",
    ["Type", "Status"]
)

fig_points = px.scatter_geo(
    volcanoes,
    lat="Latitude",
    lon="Longitude",
    color=point_color,
    size="Elev_scaled",
    hover_name="Volcano Name",
    hover_data={
        "Country": True,
        "Elev": ":.0f",
        "Type": True,
        "Status": True
    },
    projection="natural earth",
    title="Global Volcano Locations"
)


fig_points.update_traces(
    hovertemplate=
        "<b>%{hovertext}</b><br><br>" +
        "Country: %{customdata[0]}<br>" +
        "Elevation: %{customdata[1]:.0f} m<br>" +
        "Type: %{customdata[2]}<br>" +
        "Status: %{customdata[3]}<extra></extra>"
)


fig_points.update_layout(
    height=800,
    title=dict(
        text="Global Volcano Locations",
        font=dict(size=22)
    ),
    legend_title=point_color
)

st.plotly_chart(fig_points, use_container_width=True)

# -------------------------------------------------------
# NUMERICAL DISTRIBUTION ANALYSIS
# -------------------------------------------------------

st.header("📈 Distribution Analysis")

hist_variable = st.selectbox(
    "Histogram Variable",
    ['Elev', 'Exposure Index']
)

if hist_variable == 'Elev':
    hist_data = volcanoes

elif hist_variable == 'Exposure Index':
    hist_data = exposure


fig_hist = px.histogram(
    hist_data,
    x=hist_variable,
    nbins=50,
    title=f'Distribution of {hist_variable}'
)

fig_hist.update_layout(
    height=500,
    xaxis_title=hist_variable,
    yaxis_title="Number of Volcanoes",
)

st.plotly_chart(fig_hist, use_container_width=True)

# -------------------------------------------------------
# CATEGORICAL DISTRIBUTION ANALYSIS
# -------------------------------------------------------

cat_variable = st.selectbox(
    "Categorical Variable",
    ["Type", "Status"]
)

cat_counts = (
    volcanoes[cat_variable]
    .value_counts()
    .reset_index()
)

cat_counts.columns = [cat_variable, "Count"]

fig_cat = px.bar(
    cat_counts,
    x=cat_variable,
    y="Count",
    title=f"Distribution of {cat_variable}",
    text="Count"
)

fig_cat.update_layout(
    height=500,
    xaxis_title=cat_variable,
    yaxis_title="Number of Volcanoes",
    xaxis_tickangle=-45
)

fig_cat.update_traces(
    textposition="outside",
    hovertemplate=(
        f"{cat_variable}: %{{x}}<br>"
        "Count: %{y}<extra></extra>"
    )
)

st.plotly_chart(fig_cat, use_container_width=True)

# -------------------------------------------------------
# COUNTRY EXPLORER
# -------------------------------------------------------

st.header("🔍 Country Volcano Explorer")

selected_country = st.selectbox(
    "Select Country",
    sorted(volcanoes['Country'].dropna().unique())
)

country_df = volcanoes[volcanoes['Country'] == selected_country]

st.subheader(f'Volcanoes in {selected_country}')

st.dataframe(
    country_df[[
        'Volcano Name',
        'Type',
        'Status',
        'Elev',
        'Population (2020)'
    ]],
    use_container_width=True
)

# -------------------------------------------------------
# FOOTER
# -------------------------------------------------------

st.markdown('---')
st.markdown('Created with Streamlit and Plotly')
