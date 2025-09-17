# streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="해수 온난화 대시보드", layout="wide")
st.title("🌊 해수 온난화와 청소년 학습 환경 대시보드")
st.markdown("전 지구 및 한반도 해수면 온도, 폭염일수, 해수면 상승 데이터를 시각화합니다.")

# ------------------------------
# 1. 사이드바: 기간 선택
# ------------------------------
st.sidebar.header("데이터 기간 선택")
min_date = datetime(2000, 1, 1)
max_date = datetime(2035, 12, 31)
start_date = st.sidebar.date_input("시작 날짜", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("종료 날짜", value=max_date, min_value=min_date, max_value=max_date)
if start_date > end_date:
    st.sidebar.error("시작 날짜가 종료 날짜보다 늦습니다.")
    st.stop()

# ------------------------------
# 2. 전지구 해수면 온도 예시 데이터
# ------------------------------
dates_global = pd.date_range(start="2000-01-01", end="2035-12-31", freq="M")
sst_global = 15 + 0.02 * np.arange(len(dates_global)) + np.random.normal(0, 0.1, len(dates_global))
df_global_sst = pd.DataFrame({"date": dates_global, "전지구 해수면 온도(℃)": sst_global})
df_global_sst = df_global_sst[(df_global_sst["date"] >= pd.to_datetime(start_date)) &
                              (df_global_sst["date"] <= pd.to_datetime(end_date))]

fig_global = px.line(df_global_sst, x="date", y="전지구 해수면 온도(℃)", title="전지구 해수면 온도 추이")
st.plotly_chart(fig_global, use_container_width=True)

# ------------------------------
# 3. 한반도 해수면 온도
# ------------------------------
dates_korea = pd.date_range(start="2000-01-01", end="2035-12-31", freq="M")
sst_korea = 16 + 0.03 * np.arange(len(dates_korea)) + np.random.normal(0, 0.2, len(dates_korea))
df_korea_sst = pd.DataFrame({"date": dates_korea, "한반도 해수면 온도(℃)": sst_korea})
df_korea_sst = df_korea_sst[(df_korea_sst["date"] >= pd.to_datetime(start_date)) &
                            (df_korea_sst["date"] <= pd.to_datetime(end_date))]

fig_korea = px.line(df_korea_sst, x="date", y="한반도 해수면 온도(℃)", title="한반도 해수면 온도 추이")
st.plotly_chart(fig_korea, use_container_width=True)

# ------------------------------
# 4. 서울 폭염일수
# ------------------------------
dates_heat = pd.date_range(start="2000-01-01", end="2035-12-31", freq="Y")
heat_days = np.clip(np.random.normal(15, 5, len(dates_heat)) + 0.2 * np.arange(len(dates_heat)), 0, None)
df_heat = pd.DataFrame({"date": dates_heat, "서울 폭염일수(일)": heat_days})
df_heat = df_heat[(df_heat["date"] >= pd.to_datetime(start_date)) &
                  (df_heat["date"] <= pd.to_datetime(end_date))]

fig_heat = px.bar(df_heat, x="date", y="서울 폭염일수(일)", title="서울 폭염일수 변화")
st.plotly_chart(fig_heat, use_container_width=True)

# ------------------------------
# 5. 한국 연안 해수면 상승
# ------------------------------
dates_sea = pd.date_range(start="2000-01-01", end="2035-12-31", freq="Y")
sea_level = np.cumsum(3 + np.random.normal(0, 0.5, len(dates_sea)))
df_sea = pd.DataFrame({"date": dates_sea, "해수면 상승(mm)": sea_level})
df_sea = df_sea[(df_sea["date"] >= pd.to_datetime(start_date)) &
                (df_sea["date"] <= pd.to_datetime(end_date))]

fig_sea = px.line(df_sea, x="date", y="해수면 상승(mm)", title="한국 연안 해수면 상승 추이")
st.plotly_chart(fig_sea, use_container_width=True)

# ------------------------------
# 6. 지도 시각화: 해수온 Heatmap
# ------------------------------
st.header("5️⃣ 전 지구 해수온 지도")
selected_date = st.slider("지도에서 보고 싶은 날짜 선택", min_value=min_date, max_value=max_date,
                          value=min_date, format="YYYY-MM-DD")

# 예시 해수온 그리드 데이터 (위도, 경도)
lats = np.linspace(-90, 90, 180)
lons = np.linspace(-180, 180, 3)
lon_grid, lat_grid = np.meshgrid(lons, lats)
sst_map = 15 + 0.02 * ((selected_date.year-2000)*12 + selected_date.month) + np.random.normal(0, 2, lon_grid.shape)

df_map = pd.DataFrame({
    "lat": lat_grid.flatten(),
    "lon": lon_grid.flatten(),
    "sst": sst_map.flatten()
})

fig_map = px.density_mapbox(df_map, lat="lat", lon="lon", z="sst", radius=10,
                            center=dict(lat=0, lon=0), zoom=0,
                            mapbox_style="carto-positron",
                            title=f"{selected_date.strftime('%Y-%m')} 기준 전 지구 해수온(℃)")
st.plotly_chart(fig_map, use_container_width=True)

# ------------------------------
# 7. CSV 다운로드
# ------------------------------
st.header("📥 데이터 다운로드")
df_download = df_global_sst.merge(df_korea_sst, on="date", how="outer")
df_download = df_download.merge(df_heat, on="date", how="outer")
df_download = df_download.merge(df_sea, on="date", how="outer")

csv = df_download.to_csv(index=False).encode("utf-8")
st.download_button(label="CSV 다운로드", data=csv, file_name="climate_dashboard.csv", mime="text/csv")
