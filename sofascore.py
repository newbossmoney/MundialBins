import requests
import datetime

def obtener_partidos_hoy():
    hoy = datetime.datetime.now().strftime("%Y-%m-%d")
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{hoy}"

    r = requests.get(url)
    data = r.json()

    partidos = []

    for i, evento in enumerate(data.get("events", [])[:10]):
        partidos.append({
            "numero": i+1,
            "equipo1": evento["homeTeam"]["name"],
            "equipo2": evento["awayTeam"]["name"],
            "hora": evento["startTimestamp"]
        })

    return partidos


def obtener_resultados_hoy():
    hoy = datetime.datetime.now().strftime("%Y-%m-%d")
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{hoy}"

    r = requests.get(url)
    data = r.json()

    resultados = {}

    for evento in data.get("events", []):
        if "homeScore" in evento and evento["homeScore"]["current"] is not None:
            home = evento["homeTeam"]["name"]
            away = evento["awayTeam"]["name"]
            marcador = f"{evento['homeScore']['current']}-{evento['awayScore']['current']}"
            resultados[(home, away)] = marcador

    return resultados
