import pandas as pd
import numpy as np
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from datetime import datetime
import pytz
import matplotlib.pyplot as plt

# ---------------- FILE PATHS ----------------
RAIN1 = r"C:\Users\vansh\Downloads\rainfall in india 1901-2015.csv"
RAIN2 = r"C:\Users\vansh\Downloads\district wise rainfall normal.csv"

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df1 = pd.read_csv(RAIN1)
    df2 = pd.read_csv(RAIN2)
    return df1, df2

df1, df2 = load_data()

# ---------------- CLEAN ----------------
df1.columns = df1.columns.str.strip()
df2.columns = df2.columns.str.strip()

df1 = df1.dropna()
df1['YEAR'] = pd.to_numeric(df1['YEAR'], errors='coerce')
df1 = df1.dropna()

# ---------------- MODEL ----------------
rain_cols = ['JAN','FEB','MAR','APR','MAY','JUN',
             'JUL','AUG','SEP','OCT','NOV','DEC']

X = df1[['YEAR']]
y = df1[rain_cols].sum(axis=1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)

# ---------------- UI ----------------
st.set_page_config(page_title="Ultimate Weather System", layout="wide")
st.title("🌍 Ultimate Weather Prediction System")

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙ Controls")

region = st.sidebar.selectbox("Select Region", sorted(df1['SUBDIVISION'].unique()))
district = st.sidebar.selectbox("Select District", sorted(df2['DISTRICT'].unique()))
year = st.sidebar.number_input("Enter Year", 1901, 2100, 2025)

# 🔥 NEW SLIDER (Main control)
weather_slider = st.sidebar.slider("🌦 Weather Control", 0, 3000, 800)

wind_range = st.sidebar.slider("💨 Wind Range", 0, 100, (5,30))
date_range = st.sidebar.date_input("📅 Date Range", [])

# ---------------- REAL TIME ----------------
timezone = pytz.timezone("Asia/Kolkata")
current_time = datetime.now(timezone)

hour = current_time.hour

if 5 <= hour < 11:
    time_of_day = "Morning"
elif 11 <= hour < 17:
    time_of_day = "Day"
elif 17 <= hour < 20:
    time_of_day = "Evening"
else:
    time_of_day = "Night"

st.success(f"⏰ {current_time.strftime('%d-%m-%Y %H:%M:%S')} | {time_of_day}")

# ---------------- PREDICTION ----------------
prediction = model.predict([[year]])[0]
wind_speed = round(prediction / 100, 2)
humidity = min(100, max(20, int(prediction / 25)))

# ---------------- CORRECT WEATHER LOGIC ----------------
# 👉 Slider + Prediction dono ka use hoga

final_value = (prediction + weather_slider) / 2

if final_value < 500:
    weather_type = "Sunny"
elif final_value < 1200:
    weather_type = "Cloudy"
else:
    weather_type = "Rainy"

# ---------------- RAIN INTENSITY ----------------
if final_value < 500:
    rain_status = "☀️ No Rain"
elif final_value < 1200:
    rain_status = "🌥 Light Clouds"
elif final_value < 2000:
    rain_status = "🌧 Moderate Rain"
else:
    rain_status = "🌊 Heavy Rain / Flood Risk"

# ---------------- WIND ----------------
if wind_speed < wind_range[0]:
    wind_status = "🟢 Safe"
elif wind_speed <= wind_range[1]:
    wind_status = "🟡 Moderate"
else:
    wind_status = "🔴 Dangerous"

# ---------------- ANIMATIONS ----------------

# 🌧 Rain
rain_html = """<canvas id="rain"></canvas>
<script>
var c=document.getElementById("rain"),ctx=c.getContext("2d");
c.width=window.innerWidth;c.height=300;
var d=[];
for(var i=0;i<100;i++){
d.push({x:Math.random()*c.width,y:Math.random()*c.height,l:Math.random()*20,s:Math.random()*5+5});
}
function draw(){
ctx.clearRect(0,0,c.width,c.height);
ctx.strokeStyle="rgba(174,194,224,0.5)";
for(var i=0;i<d.length;i++){
var r=d[i];
ctx.beginPath();
ctx.moveTo(r.x,r.y);
ctx.lineTo(r.x,r.y+r.l);
ctx.stroke();
r.y+=r.s;
if(r.y>c.height)r.y=0;
}}
setInterval(draw,30);
</script>"""

# ☀️ Sun
sun_html = """<div style="font-size:80px;">☀️</div>"""

# ☁️ Cloud
cloud_html = """<div style="font-size:60px;">☁️ ☁️ ☁️</div>"""

# ---------------- BUTTONS ----------------
col1, col2, col3 = st.columns(3)

# 🌧 Rainfall
with col1:
    if st.button("🌧 Rainfall Prediction"):
        st.success(f"{round(prediction,2)} mm")
        st.info(rain_status)

# 🌤 Weather
with col2:
    if st.button("🌤 Weather Prediction"):

        st.subheader(f"{time_of_day} Weather")

        if weather_type == "Sunny":
            st.components.v1.html(sun_html, height=120)
            bg = "#FFD54F"

        elif weather_type == "Cloudy":
            st.components.v1.html(cloud_html, height=120)
            bg = "#90A4AE"

        else:
            st.components.v1.html(rain_html, height=200)
            bg = "#37474F"

        st.markdown(f"""
        <div style="background:{bg};padding:20px;border-radius:15px;text-align:center;color:black;">
        <h2>{weather_type}</h2>
        <p>{rain_status}</p>
        <p>🌡 Temp: {round(prediction/50,1)}°C</p>
        <p>💧 Humidity: {humidity}%</p>
        <p>💨 Wind: {wind_speed} km/h</p>
        </div>
        """, unsafe_allow_html=True)

# 💨 Wind
with col3:
    if st.button("💨 Wind Prediction"):
        st.success(f"{wind_speed} km/h")
        st.write(wind_status)

# ---------------- DATE RANGE ----------------
if len(date_range) == 2:
    days = (date_range[1] - date_range[0]).days
    est = (prediction / 365) * days
    st.subheader("📅 Rainfall for Selected Dates")
    st.success(f"{round(est,2)} mm")

# ---------------- ALERT ----------------
st.subheader("🚨 Alerts")

if final_value > 2000:
    st.error("🚨 Flood Risk")
elif wind_speed > 50:
    st.warning("🌪 Storm Risk")
else:
    st.success("✅ Safe")

# ---------------- GRAPH ----------------
st.subheader("📈 Rainfall Trend")

trend = df1.groupby('YEAR')[rain_cols].sum().sum(axis=1)
fig, ax = plt.subplots()
ax.plot(trend.index, trend.values)
st.pyplot(fig)

# ---------------- FUTURE ----------------
st.subheader("🔮 Future Prediction")

for i in range(1,6):
    f = year + i
    st.write(f"{f} → {round(model.predict([[f]])[0],2)} mm")

# ---------------- FOOTER ----------------
st.markdown("---")
st.info("☀️ Sunny | ☁️ Cloudy | 🌧 Rain | 🎯 Slider + AI Combined Prediction")