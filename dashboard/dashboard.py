import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_bike_rentals_df(df):
    daily_bike_rentals_df = df.resample(rule='D', on='dteday').agg({
        "cnt_y": "sum",
        "casual_y": "sum",
        "registered_y": "sum"
    })
    daily_bike_rentals_df = daily_bike_rentals_df.reset_index()
    daily_bike_rentals_df.rename(columns={
        "cnt_y": "total_rentals",
        "casual_y": "casual_rentals",
        "registered_y":"registered_rentals"
    }, inplace=True)

    return daily_bike_rentals_df

def create_sum_bike_rentals_df(df):
    sum_bike_rentals_df = df.groupby("weathersit_y").cnt_y.sum().sort_values(ascending=False).reset_index()
    sum_bike_rentals_df.rename(columns={
        "cnt_y": "total_rentals",
        "weathersit_y": "weather_condition"
    }, inplace=True)
    return sum_bike_rentals_df

def create_byseason_df(df):
    byseason_df = df.groupby(by="season_x").cnt_y.nunique().reset_index()
    byseason_df.rename(columns={
        "cnt_y": "unique_rentals_count"
    }, inplace=True)

    return byseason_df

def create_byweekday_df(df):
    byweekday_df = df.groupby(by="weekday_x").cnt_y.nunique().reset_index()
    byweekday_df.rename(columns={
        "customer_id": "unique_rentals_count"
    }, inplace=True)
    byweekday_df['age_group'] = pd.Categorical(byweekday_df['weekday_x'], ["Minggu", "Senin", "Selasa","Rabu","Kamis","Jumat","Sabtu"])

    return byweekday_df

def create_byweather_df(df):
    byweather_df = df.groupby(by="weathersit_x").cnt_y.nunique().reset_index()
    byweather_df.rename(columns={
        "cnt_y": "unique_rentals_count",
        "weathersit_y": "weather_condition"
    }, inplace=True)

    return byweather_df

def create_rfm_bike_rentals_df(df):
    rfm_df = df.groupby(by="weekday_x", as_index=False).agg({
        "dteday": "max", #mengambil tanggal terakhir penyewaan sepeda
        "cnt_y": ["count","sum"]
    })
    rfm_df.columns = ["weekday", "max_rent_timestamp", "frequency", "monetary"]

    rfm_df["max_rent_timestamp"] = pd.to_datetime(rfm_df["max_rent_timestamp"]).dt.date
    recent_date = df["dteday"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_rent_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_rent_timestamp", axis=1, inplace=True)

    return rfm_df

all_df = pd.read_csv("dashboard/all_data.csv")

datetime_columns = ["dteday"]
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(drop=True, inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("dashboard/bikelogo.jpg")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["dteday"] >= "2011-01-01") &
(all_df["dteday"] <= "2012-12-31")]


daily_bike_rentals_df = create_daily_bike_rentals_df(main_df)
sum_bike_rentals_df = create_sum_bike_rentals_df(main_df)
byweekday_df = create_byweekday_df(main_df)
byweather_df = create_byweather_df(main_df)
rfm_df = create_rfm_bike_rentals_df(main_df)


st.title('Bike Sharing Dashboard :sparkles:')
st.write('oleh Salsabila Selavieamanda A.')

st.subheader('Daily Rentals')

col1, col2 = st.columns(2)

with col1:
    total_rentals = daily_bike_rentals_df['total_rentals'].sum()
    st.metric("Total Rentals", value=total_rentals)

with col2:
    total_revenue = format_currency(daily_bike_rentals_df['registered_rentals'].sum(), "AUD", locale='es_CO')
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_bike_rentals_df["dteday"],
    daily_bike_rentals_df["registered_rentals"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader("Best Season for Bike Rentals")

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="total_rentals", y="weather_condition", data=sum_bike_rentals_df.head(5), palette='Set2', ax=ax)
ax.set_ylabel("Rata-rata Peminjaman", fontsize=50)
ax.set_xlabel("Musim", fontsize=50)
ax.set_xticks([0, 1, 2, 3])
ax.set_xticklabels(['Musim Gugur', 'Musim Panas', 'Musim Dingin', 'Musim Semi'], fontsize=30)
ax.tick_params(axis='y', labelsize=35)
ax.tick_params(axis='x', labelsize=30)

st.pyplot(fig)
