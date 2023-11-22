import os

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as cx

from utils import get_min_and_max_timestamp


def load_file_to_df(path):
    print("Loading file into DataFrame")

    df = pd.read_csv(path)

    # make iso_timestamp a proper datetime datatype, not just a string
    df['iso_timestamp'] = pd.to_datetime(
        df['iso_timestamp'],
        format='ISO8601'
    )
    # add hour column which only contains the hour as integer
    df['hour'] = df.iso_timestamp.apply(
        lambda timestamp: timestamp.hour
    )
    return df


def aggregate_df_to_sum_per_location_gdf(df):
    """Turn dataframe into geodataframe by aggregating the lat,lon coordinates"""
    print("Turning DataFrame into GeoDataFrame")

    data = df.groupby("standort").agg({
        "zählstand": "sum",
        "latitude": "mean",
        "longitude": "mean"
    })

    gdf = gpd.GeoDataFrame(
        data=data["zählstand"],
        crs="EPSG:4326",
        geometry=gpd.points_from_xy(
            x=data.longitude.to_numpy().flatten(),
            y=data.latitude.to_numpy().flatten()
        )
    )
    return gdf


def plot_sum_per_location(gdf, df):
    """Turn geodataframe into a nice plot."""
    print("Plotting Sum per Location")

    gdf_web_mercator = gdf.to_crs(epsg=3857)
    ax = gdf_web_mercator.plot(
        "zählstand",
        legend=True,
        cmap="Set2",
        edgecolor="Black"
    )
    cx.add_basemap(ax)

    min_date, max_date = get_min_and_max_timestamp(df)
    plt.savefig(f"../result_figures/{min_date}_{max_date}_total_count_per_city_map.png")


def filter_heidelberg(df):
    """Only return rows that are in 'Stadt Heidelberg'"""
    print("Filtering out non Heidelberg entries")

    return df[(df.standort == "Stadt Heidelberg")]


def calculate_the_average_busiest_hour_for_each_counter(df):
    print("Calculating the average busiest hour for each counter site")

    counter_site_df = df.groupby(["counter_site", "hour"]).agg({
         "zählstand": "mean"
    })

    # to show the whole row we need the index with the max zählstand per counter site
    idx = counter_site_df.groupby(["counter_site"])['zählstand'].transform("max") == counter_site_df['zählstand']
    max_counter_count_df = counter_site_df[idx]

    # filter out empty rows -> one counter measured nothing
    max_counter_count_df = max_counter_count_df[max_counter_count_df.zählstand != 0]

    # build a nice time based format to write the result as csv
    min_date, max_date = get_min_and_max_timestamp(df)

    max_counter_count_df.to_csv(
        f"../result_data/{min_date}_{max_date}_max_average_traffic_per_counter_site.csv"
    )


def plot_average_activity_over_a_day(df):
    """Plot average activity on a day over all counter sites and days"""
    print("Plotting a bar chart of the average bike activity in a day")

    grouped_by_hour_df = df.groupby("hour").agg({"zählstand": "mean"})
    grouped_by_hour_df.plot(title="Hier könnte ihr Titel stehen")
    min_date, max_date = get_min_and_max_timestamp(df)
    plt.savefig(f"../result_figures/{min_date}_{max_date}_average_activity_over_a_day.jpeg")
    grouped_by_hour_df.to_csv(f"../result_data/{min_date}_{max_date}_average_activity_over_a_day.csv")


def main():
    """Here we orchestrate the order of the functions and can comment functions that shall not be executed."""
    # the relative path starts at the directory the main file is currently in
    df = load_file_to_df(path="../input_data/eco_counter_fahrradzaehler.csv")

    gdf = aggregate_df_to_sum_per_location_gdf(df)
    plot_sum_per_location(gdf, df)

    df = filter_heidelberg(df)
    plot_average_activity_over_a_day(df)
    calculate_the_average_busiest_hour_for_each_counter(df)


if __name__ == '__main__':
    """If this file is executed directly start with main function"""
    os.makedirs("../result_figures", exist_ok=True)
    os.makedirs("../result_data", exist_ok=True)

    main()
