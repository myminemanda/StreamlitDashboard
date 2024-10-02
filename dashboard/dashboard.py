import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')


def create_average_bike_rentals_by_season(df):
    average_bike_rentals_df = df.groupby("season_x")["cnt_x"].mean().reset_index()
    average_bike_rentals_df.rename(columns={
        "cnt_x": "average_count",
        "season_x": "season"
    }, inplace=True)
    return average_bike_rentals_df


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
    byweather_df = df.groupby(by='weathersit_x')['cnt_x'].mean().reset_index()
    byweather_df.rename(columns={
        "cnt_x": "unique_rentals_count",
        "weathersit_y": "weather_condition"
    }, inplace=True)

    return byweather_df

def plot_weather_pie_chart(byweather_df):
    plt.pie(
        byweather_df['unique_rentals_count'],
        labels=['Cerah', 'Kabut', 'Hujan Ringan/Salju'],
        autopct='%1.1f%%',
        startangle=90
    )
    return byweather_df


def create_rfm_bike_rentals_df(Bike_df):
    rfm_df = Bike_df.groupby(by="weekday_x", as_index=False).agg({
        "dteday": "max",  #Mengambil tanggal terakhir penyewaan sepeda
        "cnt_y": ["count", "sum"]  
    })

    rfm_df.columns = ["weekday", "max_rent_timestamp", "frequency", "monetary"]
    rfm_df["max_rent_timestamp"] = pd.to_datetime(rfm_df["max_rent_timestamp"]).dt.date
    recent_date = Bike_df["dteday"].dt.date.max()
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


byweekday_df = create_byweekday_df(main_df)
byweather_df = create_byweather_df(main_df)
rfm_df = create_rfm_bike_rentals_df(main_df)
average_bike_rentals_df= create_average_bike_rentals_by_season(main_df)


st.title('Bike Sharing Dashboard :sparkles:')
st.write('oleh Salsabila Selavieamanda A.')

st.subheader("Rata-rata Peminjaman Sepeda berdasarkan Musim")

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(35, 15))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(x='season', y='average_count', data=average_bike_rentals_df, palette='Set2', ax=ax)

ax.set_ylabel("Rata-rata Peminjaman", fontsize=50)
ax.set_xlabel("Musim", fontsize=50)
ax.set_xticks([0, 1, 2, 3])
ax.set_xticklabels(['Musim Semi', 'Musim Panas', 'Musim Gugur', 'Musim Dingin'], fontsize=30)
ax.tick_params(axis='y', labelsize=35)
ax.tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.subheader('Rata-rata Penyewaan Sepeda berdasarkan Cuaca')

fig, ax = plt.subplots(figsize=(2,1))
ax.pie(
    byweather_df['unique_rentals_count'],
    labels=['Cerah', 'Kabut', 'Hujan Ringan/Salju'],
    autopct='%1.1f%%',
    startangle=90,
    textprops={'fontsize': 4}
)

st.pyplot(fig)


st.subheader("Penyewaan Terbaik Berdasarkan RFM Parameters")

rfm_df= create_rfm_bike_rentals_df(main_df)

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO')
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
weekday_labels = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu']
rfm_df['weekday'] = pd.Categorical(rfm_df['weekday'], categories=[0, 1, 2, 3, 4, 5, 6], ordered=True)
rfm_df['weekday'] = rfm_df['weekday'].cat.rename_categories(weekday_labels)

#Barplot berdasarkan Recency
sns.barplot(y="recency", x="weekday", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel("Recency (days)", fontsize=20)
ax[0].set_xlabel("Weekday", fontsize=20)
ax[0].set_title("By Recency (days)", loc="center", fontsize=25)
ax[0].tick_params(axis='y', labelsize=15)
ax[0].tick_params(axis='x', labelsize=15)

#Barplot berdasarkan Frequency
sns.barplot(y="frequency", x="weekday", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel("Frequency", fontsize=20)
ax[1].set_xlabel("Weekday", fontsize=20)
ax[1].set_title("By Frequency", loc="center", fontsize=25)
ax[1].tick_params(axis='y', labelsize=15)
ax[1].tick_params(axis='x', labelsize=15)

#Barplot berdasarkan Monetary
sns.barplot(y="monetary", x="weekday", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel("Monetary", fontsize=20)
ax[2].set_xlabel("Weekday", fontsize=20)
ax[2].set_title("By Monetary", loc="center", fontsize=25)
ax[2].tick_params(axis='y', labelsize=15)
ax[2].tick_params(axis='x', labelsize=15)

st.pyplot(fig)
