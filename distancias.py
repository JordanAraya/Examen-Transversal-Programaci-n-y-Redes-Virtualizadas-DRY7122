#!/usr/bin/env python3
# distancias.py

import requests
import sys

def get_coords(ciudad):
    """
    Devuelve (lat, lon) de la ciudad usando Nominatim.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": ciudad + ", Chile" if "Chile" in ciudad or "Argentina" not in ciudad else ciudad,
        "format": "json",
        "limit": 1
    }
    resp = requests.get(url, params=params, headers={"User-Agent": "DRY7122-Examen"})
    data = resp.json()
    if not data:
        return None
    return float(data[0]["lat"]), float(data[0]["lon"])

def get_route(origen, destino, modo):
    """
    Llama a OSRM para obtener ruta entre dos coordenadas:
    modo ∈ {"driving", "walking", "cycling"}
    Devuelve un dict con keys: distance (m), duration (s), steps (lista de textos).
    """
    coords = f"{origen[1]},{origen[0]};{destino[1]},{destino[0]}"
    url = f"http://router.project-osrm.org/route/v1/{modo}/{coords}"
    params = {
        "overview": "false",
        "geometries": "polyline",
        "steps": "true"
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if data.get("code") != "Ok":
        return None

    route = data["routes"][0]
    steps = []
    for leg in route["legs"]:
        for step in leg["steps"]:
            # Intentamos leer la instrucción; si falta, usamos el nombre de la calle o un texto genérico
            instr = step.get("maneuver", {}).get("instruction")
            if not instr:
                instr = step.get("name") or "Sin instrucción detallada"
            steps.append(instr)
    return {
        "distance": route["distance"],
        "duration": route["duration"],
        "steps": steps
    }

def format_duration(segundos):
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def main():
    modos = {"1": "driving", "2": "walking", "3": "cycling"}
    while True:
        origen = input("Ciudad de Origen (o 's' para salir): ").strip()
        if origen.lower() == 's':
            print("¡Hasta luego!")
            sys.exit(0)

        destino = input("Ciudad de Destino (o 's' para salir): ").strip()
        if destino.lower() == 's':
            print("¡Hasta luego!")
            sys.exit(0)

        print("Medio de transporte: 1) Auto  2) A pie  3) Bicicleta")
        opcion = input("Elige 1, 2, 3 (o 's' para salir): ").strip()
        if opcion.lower() == 's':
            print("¡Hasta luego!")
            sys.exit(0)
        modo = modos.get(opcion)
        if not modo:
            print("Opción inválida.\n")
            continue

        # Geocodificar
        coords_o = get_coords(origen + ", Chile")
        coords_d = get_coords(destino + ", Argentina")
        if not coords_o or not coords_d:
            print("No se pudo geocodificar alguna de las ciudades.\n")
            continue

        # Obtener ruta
        ruta = get_route(coords_o, coords_d, modo)
        if not ruta:
            print("Error al obtener la ruta.\n")
            continue

        # Mostrar resultados
        km = ruta["distance"] / 1000
        millas = km * 0.621371
        dur = format_duration(ruta["duration"])
        print(f"\nDistancia: {km:.2f} km ({millas:.2f} millas)")
        print(f"Duración aprox.: {dur}\n")
        print("Instrucciones de viaje:")
        for i, paso in enumerate(ruta["steps"], 1):
            print(f"  {i}. {paso}")
        print("\n" + "-"*40 + "\n")

if __name__ == "__main__":
    main()
