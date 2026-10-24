"""Demostracion del visor: no lee archivos ni servicios catastrales."""

import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent


def polygon(x, y, width, height, properties):
    return {
        "type": "Feature",
        "properties": properties,
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [x, y], [x + width, y], [x + width, y + height],
                [x, y + height], [x, y],
            ]],
        },
    }


def collection(features):
    return {"type": "FeatureCollection", "features": features}


def demo_payload():
    parcels = []
    buildings = []
    units = []
    for index in range(1, 4):
        npn = "0000000000000" + "0001" + f"{index:04d}" + "000000000"
        x = -75.282 + (index - 1) * 0.001
        parcels.append(polygon(x, 2.934, 0.0008, 0.0008, {
            "npn": npn,
            "npn_anterior": f"DEMO-{index:04d}",
            "direccion": f"DEMO CALLE {index}",
            "destinacion": "Habitacional (ficticio)",
            "area_terreno": 100.0,
        }))
        attributes = {
            "npn": npn, "tipo": "Demostracion", "dominio": "Ficticio",
            "pisos": 1, "sotanos": 0, "altura": 3,
            "destinacion": "Habitacional (ficticio)",
            "area_construida": 60.0,
            "estado_area_construida": "Dato inventado para probar la interfaz",
            "area_construida_predio": 60.0,
            "uso_construccion": "Vivienda (ficticio)",
        }
        buildings.append(polygon(x + 0.0001, 2.9341, 0.0004, 0.0004, attributes))
        units.append(polygon(x + 0.0001, 2.9341, 0.0004, 0.0004, {
            "npn": npn, "tipo_planta": "Ficticia",
            "planta_ubicacion": 1, "altura": 3,
        }))
    layers = {}

    def add(name, title, dataset, features):
        layers[name] = {"title": title, "dataset": dataset, "data": collection(features)}

    add("limite", "Extensión de ejemplo — NO es el límite municipal", "Cartografia_Catastral", [
        polygon(-75.283, 2.932, 0.005, 0.004, {"codigo_municipio": "DEMO"}),
    ])
    add("manzanas", "Manzana ficticia", "Cartografia_Catastral", [
        polygon(-75.2822, 2.9338, 0.0032, 0.0012, {"codigo": "00000000000000001"}),
    ])
    add("veredas", "Veredas ficticias", "Cartografia_Catastral", [
        polygon(-75.283, 2.932, 0.0025, 0.004, {"nombre": "VEREDA DEMO A"}),
        polygon(-75.2805, 2.932, 0.0025, 0.004, {"nombre": "VEREDA DEMO B"}),
    ])
    for name, title in (
        ("zhf_urbana", "Zonas físicas urbanas ficticias"),
        ("zhf_rural", "Zonas físicas rurales ficticias"),
        ("zhg_urbana", "Zonas geoeconómicas urbanas ficticias"),
        ("zhg_rural", "Zonas geoeconómicas rurales ficticias"),
    ):
        field = "codigo_zona_fisica" if name.startswith("zhf") else "codigo_zona_geoeconomica"
        add(name, title, "Avaluos", [
            polygon(-75.283, 2.932, 0.0025, 0.004, {field: "DEMO-01"}),
            polygon(-75.2805, 2.932, 0.0025, 0.004, {field: "DEMO-02"}),
        ])
    return {
        "layers": layers, "predios": collection(parcels),
        "construcciones": collection(buildings),
        "unidades_construccion": collection(units),
    }


def build_demo_document():
    html = (ROOT / "viewer.html").read_text(encoding="utf-8")
    css = (ROOT / "resources" / "ol.css").read_text(encoding="utf-8")
    javascript = (ROOT / "resources" / "ol.js").read_text(encoding="utf-8")
    payload = json.dumps(demo_payload(), ensure_ascii=True)
    bootstrap = """
    <script>
    const demoData = __PAYLOAD__;
    const originalFetch = globalThis.fetch.bind(globalThis);
    globalThis.fetch = async (input, init) => {
      const url = new URL(String(input), "https://demo.invalid/");
      const respond = (body, status = 200) => new Response(JSON.stringify(body), {
        status, headers: {"Content-Type": "application/json"}
      });
      if (url.pathname === "/api/layers") return respond({layers: demoData.layers});
      if (url.pathname === "/api/search") {
        const query = (url.searchParams.get("q") || "").trim().toUpperCase();
        if (query.length < 4) return respond({error: "Escriba al menos 4 caracteres."}, 400);
        const features = demoData.predios.features.filter(f =>
          [f.properties.npn, f.properties.npn_anterior, f.properties.direccion]
            .some(value => String(value).toUpperCase().startsWith(query)));
        const codes = new Set(features.map(f => f.properties.npn));
        return respond({
          predios: {type: "FeatureCollection", features},
          construcciones: {type: "FeatureCollection",
            features: demoData.construcciones.features.filter(f => codes.has(f.properties.npn))}
        });
      }
      if (url.pathname === "/api/features") {
        const layer = url.searchParams.get("layer");
        if (!["predios", "construcciones", "unidades_construccion"].includes(layer))
          return respond({error: "Capa de ejemplo no disponible."}, 400);
        const bbox = (url.searchParams.get("bbox") || "").split(",").map(Number);
        if (bbox.length !== 4 || !bbox.every(Number.isFinite))
          return respond({error: "Extensión inválida."}, 400);
        return respond({type: "FeatureCollection",
          features: demoData[layer].features.filter(f => {
            const ring = f.geometry.coordinates[0];
            const xs = ring.map(c => c[0]), ys = ring.map(c => c[1]);
            return Math.max(...xs) >= bbox[0] && Math.min(...xs) <= bbox[2]
              && Math.max(...ys) >= bbox[1] && Math.min(...ys) <= bbox[3];
          })
        });
      }
      if (url.pathname.startsWith("/api/"))
        return respond({error: "Servicio no disponible en la demostración."}, 404);
      return originalFetch(input, init);
    };
    </script>
    """.replace("__PAYLOAD__", payload)
    replacements = {
        '<link rel="stylesheet" href="/resources/ol.css" />': f"<style>{css}</style>",
        '<script src="/resources/ol.js"></script>': f"<script>{javascript}</script>{bootstrap}",
        "Visor geográfico catastral de Neiva — ambiente de pruebas":
            "Geoportal de Neiva — DEMOSTRACIÓN CON DATOS FICTICIOS",
        "Información 2026 · visor local · no publicado en Internet":
            "Geometrías inventadas · sin información catastral real · no válido para trámites",
        "El servicio está ligado a este equipo (127.0.0.1). La búsqueda muestra solo datos catastrales autorizados para esta prueba; no incluye nombres de personas, documentos de identidad, matrículas inmobiliarias ni valores por m²/hectárea.":
            "Demostración sin conexión a la GDB. Busque DEMO para consultar los tres predios ficticios.",
        "Fuente: GDB 2026. Consulta informativa; no constituye certificación catastral.":
            "DATOS FICTICIOS: no representan predios, áreas ni límites reales.",
        "GDB · 2026-05-14": "DATOS FICTICIOS · DEMO",
        "Se muestran geometrías existentes y vinculadas a predios. La GDB incluye registros de unidades sin geometría; no se dibujan ubicaciones supuestas.":
            "Todos los polígonos de esta demostración son rectángulos inventados.",
    }
    for old, new in replacements.items():
        if old not in html:
            raise ValueError("La plantilla del visor cambió; revise las sustituciones de demostración.")
        html = html.replace(old, new)
    return html


def main():
    st.set_page_config(page_title="Geoportal Neiva | Demo", layout="wide")
    st.title("Geoportal de Neiva · demostración")
    st.warning(
        "Solo datos ficticios. No se ha cargado la GDB ni información predial real. "
        "Esta aplicación no certifica información catastral."
    )
    st.caption(
        "Pruebe la búsqueda escribiendo DEMO. El acceso privado se configura "
        "en Streamlit Community Cloud → Settings → Sharing; no dentro de este mapa."
    )
    st.iframe(build_demo_document(), height=850)


if __name__ == "__main__":
    main()
