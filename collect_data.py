import requests
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

# =========================
# CONFIGURAÇÕES
# =========================
load_dotenv()
WAQI_TOKEN = os.getenv("WAQI_TOKEN")
CITY_URL = "https://api.waqi.info/feed/brazil/sao-paulo/parque-d.pedro-ii/"
DATA_PATH = "data/dataset.csv"

# =========================
# FUNÇÃO DE COLETA
# =========================
def fetch_data():
    response = requests.get(
        CITY_URL,
        params={"token": WAQI_TOKEN},
        timeout=10
    )
    data = response.json()

    if data["status"] != "ok":
        raise Exception("Erro na API WAQI")

    iaqi = data["data"]["iaqi"]

    row = {
        "timestamp": datetime.now(),
        "aqi": data["data"]["aqi"],
        "pm25": iaqi.get("pm25", {}).get("v"),
        "pm10": iaqi.get("pm10", {}).get("v"),
        "o3": iaqi.get("o3", {}).get("v"),
        "no2": iaqi.get("no2", {}).get("v"),
        "temp": iaqi.get("t", {}).get("v"),
        "humidity": iaqi.get("h", {}).get("v"),
    }

    return pd.DataFrame([row])

# =========================
# SALVAR NO CSV
# =========================
def save_data(df_new):
    os.makedirs("data", exist_ok=True)

    if os.path.exists(DATA_PATH) and os.path.getsize(DATA_PATH) > 0:
        df_old = pd.read_csv(DATA_PATH)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_csv(DATA_PATH, index=False)

# =========================
# EXECUÇÃO
# =========================
if __name__ == "__main__":
    df = fetch_data()
    save_data(df)
    print("Dados coletados com sucesso:", datetime.now())
