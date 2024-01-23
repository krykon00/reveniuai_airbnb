"""Main dashboard app file"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import pydeck as pdk
import streamlit as st

from manipulator import get_joined_dfs


PATH: Path = Path(__file__).parent.resolve()

st.set_page_config(
    page_title="Airbnb Barcelona Pirces",
    page_icon="money_with_wings",
    layout="wide",
    initial_sidebar_state="expanded",
)

df: pd.DataFrame = pd.read_csv(f"{PATH}/data/listings.csv")
df.dropna(subset = ['price'], inplace=True)
# Column alter and creation
df["price"] = df["price"].str.replace(r"[$,]", "", regex=True).astype(float)
df["price_per_bed"] = round(df["price"] / df["beds"], 2)
df["price_per_person"] = round(df["price"] / df["accommodates"], 2)

# Filters
price_min: int = 0
price_max: int = int(df["price"].max())
beds_nr: int = int(df["beds"].max())
accommodates_nr: int = int(df["accommodates"].max())
property_type_list: list[str] = list(df["property_type"].unique())
room_type_list: list[str] = list(df["room_type"].unique())

with st.sidebar:
    st.image("https://pluspng.com/img-png/airbnb-logo-png-airbnb-logo-1600.png")
    with st.expander("Info"):
        st.write(
            """This is a coding test project analising Airbnb data set onfly of Barcelona.
                 Data source: http://data.insideairbnb.com/spain/catalonia/barcelona/2023-12-13/data/listings.csv.gz"""
        )
    st.markdown("## Filters")
    with st.expander("Price value filter step"):
        price_filter_range = st.slider(
            label="Step value in price max & min filters",
            max_value=1000,
            min_value=1,
            step=1,
        )
    price_min = st.slider(
        label="Min price value",
        max_value=price_max,
        step=price_filter_range,
        help="If value is set to 0, this filter will not be applied.",
    )
    price_max = st.slider(
        label="Max price value",
        min_value=price_min + 1,
        max_value=price_max,
        value=price_max-1,
        step=price_filter_range,
    )
    accommodates_nr = st.slider(
        label="Min nr of accommodates",
        max_value=accommodates_nr,
        step=1,
        help="If value is set to 0, this filter will not be applied.",
    )
    beds_nr = st.slider(
        label="Min nr of beds",
        max_value=beds_nr,
        step=1,
        help="If value is set to 0, this filter will not be applied.",
    )
    property_type_list = st.multiselect(
        label="Property type",
        options=property_type_list,
    )
    room_type_list = st.multiselect(
        label="Room type",
        options=room_type_list,
    )
if price_max > 1:
    df = df[df["price"].between(price_min, price_max)]
if accommodates_nr > 0:
    df = df[df["accommodates"] >= accommodates_nr]
if beds_nr > 0:
    df = df[df["beds"] >= beds_nr]
if property_type_list:
    df = df[df["property_type"].isin(property_type_list)]
if room_type_list:
    df = df[df["room_type"].isin(room_type_list)]


with st.container():  # Main body container
    if df.shape[0] == 0:
        st.markdown(
            "## :no_entry: Please change your filtering criteria as no data exists with cuurent ones applied. :no_entry:"
        )
    else:
        with st.container():  # KPIs row
            st.info("All price values are in USD")
            col_avg_p, col_min_p, col_max_p, col_units = st.columns(4)
            with col_avg_p:
                fig = go.Figure()
                fig.add_trace(
                    go.Indicator(
                        value=df["price"].mean(),
                        mode="number",
                    )
                )
                fig.update_layout(
                    title=go.layout.Title(
                        text="Avg price", xanchor="center", yanchor="top", y=0.9, x=0.5
                    )
                )
                st.plotly_chart(fig, theme="streamlit", use_container_width=True)
            with col_min_p:
                fig = go.Figure()
                fig.add_trace(
                    go.Indicator(
                        value=df["price"].min(),
                        mode="number",
                    )
                )
                fig.update_layout(
                    title=go.layout.Title(
                        text="Min price", xanchor="center", yanchor="top", y=0.9, x=0.5
                    )
                )
                st.plotly_chart(fig, theme="streamlit", use_container_width=True)
            with col_max_p:
                fig = go.Figure()
                fig.add_trace(
                    go.Indicator(
                        value=df["price"].max(),
                        mode="number",
                    )
                )
                fig.update_layout(
                    title=go.layout.Title(
                        text="Max price", xanchor="center", yanchor="top", y=0.9, x=0.5
                    )
                )
                st.plotly_chart(fig, theme="streamlit", use_container_width=True)
            with col_units:
                fig = go.Figure()
                fig.add_trace(
                    go.Indicator(
                        value=df.shape[0],
                        mode="number",
                    )
                )
                fig.update_layout(
                    title=go.layout.Title(
                        text="Nr. of units",
                        xanchor="center",
                        yanchor="top",
                        y=0.9,
                        x=0.5,
                    )
                )
                st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        with st.container():
            st.markdown("### Prices by room type")
            with st.container():
                sub_df = get_joined_dfs(df[["room_type", "price"]], group_cols=["room_type"], aggs=["mean", "max", "min"])
                col_room_max, col_room_min, col_room_mean = st.columns(3)
                with col_room_max:
                    sub_df = sub_df.sort_values(by="max")
                    fig = go.Figure()
                    fig.add_trace(
                        go.Bar(x=sub_df["room_type"], 
                               y=sub_df["max"],
                               name='Max price',
                               marker_color='indianred',
                            text=sub_df["max"].round(2),
                    ))
                    fig.update_layout(title='Max price per room type')
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                with col_room_min:
                    sub_df = sub_df.sort_values(by="min")
                    fig = go.Figure()
                    fig.add_trace(
                        go.Bar(x=sub_df["room_type"], 
                            y=sub_df["min"],
                            name='Min price',
                            marker_color='crimson',
                            text=sub_df["min"].round(2),
                    ))
                    fig.update_layout(title='Min price per room type')
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                with col_room_mean:
                    sub_df = sub_df.sort_values(by="mean")
                    fig = go.Figure()
                    fig.add_trace(
                    go.Bar(x=sub_df["room_type"], 
                           y=sub_df["mean"],
                           name='Mean price',
                           marker_color='lightslategray',
                           text=sub_df["mean"].round(2),
                ))
                    fig.update_layout(title='Mean price per room type')
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
            with st.container():
                col_p_room_bed, col_p_room_acc = st.columns(2)
                with col_p_room_bed:
                    sub_df = get_joined_dfs(df[["room_type", "price_per_bed"]], group_cols=["room_type"], aggs=["mean"])
                    sub_df = sub_df.sort_values(by="mean")
                    fig = go.Figure()
                    fig.add_trace(
                    go.Bar(x=sub_df["room_type"], 
                           y=sub_df["mean"].round(2),
                           name='Mean price per bed',
                           marker_color='indigo',
                           text=sub_df["mean"].round(2),
                    ))
                    fig.update_layout(title='Mean price of 1 bed per room type')
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                with col_p_room_acc:
                    sub_df = get_joined_dfs(df[["room_type", "price_per_person"]], group_cols=["room_type"], aggs=["mean"])
                    sub_df = sub_df.sort_values(by="mean")
                    fig = go.Figure()
                    fig.add_trace(
                    go.Bar(x=sub_df["room_type"], 
                           y=sub_df["mean"],
                           name='Mean price per accommodated person.',
                           marker_color='greenyellow',
                           text = sub_df["mean"].round(2)
                    ))
                    fig.update_layout(title='Mean price of 1 accommodated person per room type')
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)



        with st.container():
            st.markdown("### Prices by property type")
            with st.container():
                sub_df = get_joined_dfs(df[["property_type", "price"]], group_cols=["property_type"], aggs=["mean", "max", "min"])
                col_prop_max, col_prop_min, col_prop_mean = st.columns(3)
                with col_prop_max:
                    sub_df = sub_df.sort_values(by="max")
                    fig = go.Figure()
                    fig.add_trace(
                        go.Bar(x=sub_df["property_type"], 
                               y=sub_df["max"],
                               name='Max price',
                               marker_color='indianred',
                               text=sub_df["max"].round(2),
                    ))
                    fig.update_layout(title='Max price per property type')
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                with col_prop_min:
                    sub_df = sub_df.sort_values(by="min")
                    fig = go.Figure()
                    fig.add_trace(
                        go.Bar(x=sub_df["property_type"], 
                               y=sub_df["min"],
                               name='Min price',
                               marker_color='crimson',
                               text=sub_df["min"].round(2),

                    ))
                    fig.update_layout(title='Min price per property type')
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                with col_prop_mean:
                    sub_df = sub_df.sort_values(by="mean")
                    fig = go.Figure()
                    fig.add_trace(
                    go.Bar(x=sub_df["property_type"], 
                           y=sub_df["mean"].round(2),
                           name='Mean price',
                           marker_color='lightslategray',
                               text=sub_df["mean"].round(2),
                ))
                    fig.update_layout(title='Mean price per property type')
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
            with st.container():
                col_p_prop_bed, col_p_prop_acc = st.columns(2)
                with col_p_prop_bed:
                    sub_df = get_joined_dfs(df[["property_type", "price_per_bed"]], group_cols=["property_type"], aggs=["mean"])
                    sub_df = sub_df.sort_values(by="mean")
                    fig = go.Figure()
                    fig.add_trace(
                    go.Bar(x=sub_df["property_type"], 
                           y=sub_df["mean"].round(2),
                           name='Mean price per bed',
                           marker_color='indigo',
                           text=sub_df["mean"].round(2),
                    ))
                    fig.update_layout(title='Mean price of 1 bed per propery type')
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                with col_p_prop_acc:
                    sub_df = get_joined_dfs(df[["property_type", "price_per_person"]], group_cols=["property_type"], aggs=["mean"])
                    sub_df = sub_df.sort_values(by="mean")
                    fig = go.Figure()
                    fig.add_trace(
                    go.Bar(x=sub_df["property_type"], 
                           y=sub_df["mean"],
                           name='Mean price per accommodated person.',
                           marker_color='greenyellow',
                           text = sub_df["mean"].round(2)
                    ))
                    fig.update_layout(title='Mean price of 1 accommodated person per property type')
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)




        with st.container():
            fig = px.histogram(df, x="price", title="Price histogram")
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        with st.container():
            sub_df = (
                df[["neighbourhood", "price"]]
                .groupby(by="neighbourhood", as_index=False)
                .mean()
                .dropna()
                .sort_values(by="price", ascending=False)
            )
            fig = px.bar(
                sub_df,
                y="price",
                x="neighbourhood",
                text_auto=".2s",
                title="Average price per neighbourhood",
                color='price'

            )
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        with st.container():  # Map container
            midpoint = (np.average(df["latitude"]), np.average(df["longitude"]))
            st.markdown("### Barcelons Airbnb appertments price map.")
            st.info(
                "Hexagon cilinder color saturation as well as it height correspond directly to the price value."
            )
            st.write(
                pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v9",
                    initial_view_state={
                        "latitude": midpoint[0],
                        "longitude": midpoint[1],
                        "zoom": 11,
                        "pitch": 50,
                    },
                    layers=[
                        pdk.Layer(
                            "HexagonLayer",
                            data=df[["price", "latitude", "longitude"]],
                            get_position=["longitude", "latitude"],
                            auto_highlight=True,
                            radius=100,
                            extruded=True,
                            pickable=True,
                            elevation_scale=4,
                            elevation_range=[0, 1000],
                        ),
                    ],
                )
            )
        with st.container():  # Data table
            st.markdown("### Data table.")
            st.dataframe(
                data=df[
                    [
                        "name",
                        "price",
                        "neighbourhood",
                        "property_type",
                        "room_type",
                        "beds",
                        "host_name",
                        "listing_url",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )
