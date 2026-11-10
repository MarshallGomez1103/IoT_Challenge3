#!/usr/bin/env python3
"""
WMS - Water Management System · AI Diagnostic Analyst
Challenge #3 · Internet de las Cosas · Universidad de La Sabana (2026-2)
Autores: Elioth Thomas Gomez, David Jasub Sastre, Andrés Felipe Suárez

Servicio perimetral que consulta el histórico local SQLite y genera un diagnóstico
estructurado invocando la API de Google Gemini (gemini-2.5-flash) en modo JSON estricto,
con fallback determinista offline.
"""

import json
import sqlite3
import time
import os
import paho.mqtt.client as mqtt
from google import genai
from google.genai import types

# Configuración institucional
DB_PATH = os.environ.get("WMS_DB_PATH", "/var/lib/wms/wms_telemetry.db")
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPIC_IA = "wms/sabana/nodo1/ia"

def consultar_ventana_historica(horas: int = 24) -> list:
    """Extrae las lecturas horarias de la base de datos perimetral."""
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    limite_ts = int(time.time()) - (horas * 3600)
    cursor.execute("""
        SELECT ts, dist_cm, nivel_pct, riesgo, luz_pct, temp_c, hum_pct, presion_hpa
        FROM lecturas
        WHERE ts >= ?
        ORDER BY ts ASC
    """, (limite_ts,))
    filas = cursor.fetchall()
    conn.close()
    return filas

def generar_diagnostico_ia(filas: list) -> dict:
    """Invoca la API de Google Gemini forzando salida determinista en JSON."""
    if not filas:
        return {
            "estado": "Sin datos",
            "tipo_anomalia": "SIN_ANOMALIA",
            "motivo": "No se encontraron lecturas en la ventana histórica requerida.",
            "recomendacion_alcaldia": "Verificar enlace de comunicación del nodo sensor."
        }

    muestras = [
        {
            "ts": f[0], "dist_cm": f[1], "nivel_pct": f[2], "riesgo": f[3],
            "luz_pct": f[4], "temp_c": f[5], "hum_pct": f[6], "presion_hpa": f[7]
        }
        for f in filas
    ]

    payload_entrada = {
        "nodo": "nodo1",
        "ubicacion": "Sabana Centro (2560 msnm)",
        "ventana": f"ultimas_{len(filas)}_muestras",
        "modelo": "Multiplicativo IEC/ISO 31010 + FAO-56",
        "muestras": muestras
    }

    try:
        # Inicializa cliente tomando GEMINI_API_KEY de las variables de entorno
        cliente = genai.Client()
        prompt_sistema = (
            "Eres el Analista Hidrometeorológico de WMS para Sabana Centro. "
            "Responde estrictamente en formato JSON con las claves: "
            "'estado', 'tipo_anomalia', 'motivo', 'recomendacion_alcaldia'. "
            "Prohibido emitir texto conversacional fuera del JSON."
        )

        respuesta = cliente.models.generate_content(
            model="gemini-2.5-flash",
            contents=json.dumps(payload_entrada),
            config=types.GenerateContentConfig(
                system_instruction=prompt_sistema,
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        return json.loads(respuesta.text)

    except Exception:
        # Fallback determinista perimetral si la WAN o la API no responden
        return ejecutar_fallback_local(muestras[-1])

def ejecutar_fallback_local(ultima_muestra: dict) -> dict:
    """Regla determinista local ejecutada ante indisponibilidad de conexión a Internet."""
    riesgo = ultima_muestra.get("riesgo", 0.0)
    nivel = ultima_muestra.get("nivel_pct", 100.0)

    if nivel <= 15.0 or riesgo >= 0.85:
        return {
            "estado": "Crítico",
            "tipo_anomalia": "FUGA_O_VACIADO_CRITICO",
            "motivo": f"Fallback local: Reserva crítica detectada ({nivel:.1f}%), riesgo {riesgo:.2f}.",
            "recomendacion_alcaldia": "Inspección física urgente de válvulas y activación de racionamiento."
        }
    elif riesgo >= 0.70:
        return {
            "estado": "Riesgo Alto",
            "tipo_anomalia": "EVAPORACION_PREVENTIVA",
            "motivo": f"Fallback local: Demanda ambiental elevada, riesgo {riesgo:.2f}.",
            "recomendacion_alcaldia": "Monitoreo preventivo y restricción de usos suntuarios del agua."
        }
    return {
        "estado": "Normal",
        "tipo_anomalia": "SIN_ANOMALIA",
        "motivo": "Fallback local: Parámetros operativos dentro del margen de seguridad.",
        "recomendacion_alcaldia": "Mantener régimen de operación ordinario."
    }

def publicar_diagnostico(diagnostico: dict):
    """Publica el dictamen en el broker Mosquitto con retención activa."""
    cliente_mqtt = mqtt.Client(client_id="wms_ia_worker")
    cliente_mqtt.connect(MQTT_BROKER, MQTT_PORT, 60)
    payload_str = json.dumps(diagnostico, ensure_ascii=False)
    cliente_mqtt.publish(TOPIC_IA, payload_str, qos=1, retain=True)
    cliente_mqtt.disconnect()

if __name__ == "__main__":
    datos = consultar_ventana_historica(24)
    resultado = generar_diagnostico_ia(datos)
    publicar_diagnostico(resultado)
