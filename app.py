import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime

# =============================
# CONFIGURAÇÕES
# =============================

WAQI_TOKEN = "d7ba3e94f75ec75b7a30a6f40bad28e906326586"
CITY_URL = "https://api.waqi.info/feed/@8490/"  # Parque D. Pedro II
DATA_PATH = "data/dataset.csv"

# =============================
# FUNÇÃO: BUSCAR DADOS DA API
# =============================

def fetch_air_quality():
    url = f"{CITY_URL}?token={WAQI_TOKEN}"
    response = requests.get(url)
    data = response.json()

    if data["status"] != "ok":
        st.error("Erro ao acessar a API WAQI")
        return None

    iaqi = data["data"]["iaqi"]

    row = {
        "timestamp": datetime.now(),
        "aqi": data["data"]["aqi"],
        "pm25": iaqi.get("pm25", {}).get("v"),
        "pm10": iaqi.get("pm10", {}).get("v"),
        "no2": iaqi.get("no2", {}).get("v"),
        "o3": iaqi.get("o3", {}).get("v"),
        "co": iaqi.get("co", {}).get("v"),
        "so2": iaqi.get("so2", {}).get("v"),
        "temp": iaqi.get("t", {}).get("v"),
        "humidity": iaqi.get("h", {}).get("v")
    }

    return pd.DataFrame([row])

# =============================
# FUNÇÃO: SALVAR DADOS (SEM ERRO)
# =============================

def save_data(df_new):
    # Se o arquivo NÃO existe → cria direto
    if not os.path.exists(DATA_PATH):
        df_new.to_csv(DATA_PATH, index=False)
        return df_new

    # Se existe mas está vazio → sobrescreve
    if os.stat(DATA_PATH).st_size == 0:
        df_new.to_csv(DATA_PATH, index=False)
        return df_new

    # Caso normal → concatena
    df_old = pd.read_csv(DATA_PATH)
    df_all = pd.concat([df_old, df_new], ignore_index=True)
    df_all.to_csv(DATA_PATH, index=False)

    return df_all

# =============================
# INTERFACE STREAMLIT
# =============================

st.set_page_config(page_title="Qualidade do Ar - SP", layout="centered")

st.title("🌫️ Qualidade do Ar — Parque D. Pedro II (SP)")

if st.button("📡 Coletar dados agora"):
    df_new = fetch_air_quality()

    if df_new is not None:
        df_all = save_data(df_new)

        st.success("Dados coletados e salvos com sucesso!")
        st.metric("AQI Atual", int(df_new["aqi"][0]))

# =============================
# VISUALIZAÇÃO DOS DADOS
# =============================

if os.path.exists(DATA_PATH) and os.stat(DATA_PATH).st_size > 0:
    df = pd.read_csv(DATA_PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    st.subheader("📊 Histórico de AQI")
    st.line_chart(df.set_index("timestamp")["aqi"])

    st.subheader("📄 Dados brutos")
    st.dataframe(df)
else:
    st.info("Nenhum dado coletado ainda.")


#  streamlit run app.py
