#!/usr/bin/env python3
"""
WMS Gateway - MQTT to SQLite Bridge and Cloud Forwarder (Store-and-Forward)
Challenge #3 · Internet de las Cosas · Universidad de La Sabana (2026-2)
Autores: Elioth Thomas Gomez, David Jasub Sastre, Andrés Felipe Suárez
"""

import json
import sqlite3
import time
import os
import logging
import threading
import paho.mqtt.client as mqtt

# Configuración
DB_PATH = os.environ.get("WMS_DB_PATH", "/var/lib/wms/wms_telemetry.db")
LOCAL_BROKER = "localhost"
LOCAL_PORT = 1883
LOCAL_TOPIC_TELEMETRY = "wms/sabana/+/telemetria"
LOCAL_TOPIC_ACK = "wms/sabana/+/alarmas/ack"

UBIDOTS_BROKER = "industrial.api.ubidots.com"
UBIDOTS_PORT = 1883
UBIDOTS_TOKEN = os.environ.get("UBIDOTS_TOKEN", "")
UBIDOTS_DEVICE_LABEL = "wms-nodo1"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def inicializar_bd():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lecturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nodo TEXT NOT NULL,
            dist_cm REAL NOT NULL,
            nivel_pct REAL NOT NULL,
            riesgo REAL NOT NULL,
            luz_pct REAL,
            temp_c REAL,
            hum_pct REAL,
            presion_hpa REAL,
            estado TEXT NOT NULL,
            ts INTEGER NOT NULL,
            synced INTEGER DEFAULT 0
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lecturas_ts ON lecturas(ts);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lecturas_synced ON lecturas(synced);")
    conn.commit()
    conn.close()
    logging.info("Base de datos SQLite inicializada correctamente en %s", DB_PATH)

def guardar_lectura(nodo, payload):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lecturas (nodo, dist_cm, nivel_pct, riesgo, luz_pct, temp_c, hum_pct, presion_hpa, estado, ts, synced)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            nodo,
            payload.get("dist_cm", 0.0),
            payload.get("nivel_pct", 0.0),
            payload.get("riesgo", 0.0),
            payload.get("luz_pct", 0.0),
            payload.get("temp_c", 0.0),
            payload.get("hum_pct", 0.0),
            payload.get("presion_hpa", 0.0),
            payload.get("estado", "NORMAL"),
            payload.get("ts", int(time.time()))
        ))
        conn.commit()
        conn.close()
        logging.info("Lectura guardada en SQLite para nodo %s (synced=0)", nodo)
    except Exception as e:
        logging.error("Error guardando lectura en SQLite: %s", e)

def hilo_sincronizacion_cloud():
    """Hilo trabajador periódico para Store-and-Forward hacia Ubidots."""
    while True:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, dist_cm, nivel_pct, riesgo, luz_pct, temp_c, hum_pct, presion_hpa, ts
                FROM lecturas
                WHERE synced = 0
                ORDER BY ts ASC
                LIMIT 50
            """)
            filas = cursor.fetchall()
            
            if filas and UBIDOTS_TOKEN:
                # Intentar conexión con Ubidots
                client_cloud = mqtt.Client(client_id="wms_gateway_forwarder")
                client_cloud.username_pw_set(UBIDOTS_TOKEN, password="")
                client_cloud.connect(UBIDOTS_BROKER, UBIDOTS_PORT, 30)
                
                ids_sincronizados = []
                for fila in filas:
                    id_rec, dist, nivel, riesgo, luz, temp, hum, pres, ts = fila
                    payload_cloud = {
                        "distancia": dist,
                        "nivel": nivel,
                        "riesgo": riesgo,
                        "luz": luz,
                        "temperatura": temp,
                        "humedad": hum,
                        "presion": pres,
                        "timestamp": ts * 1000
                    }
                    topic = f"/v1.6/devices/{UBIDOTS_DEVICE_LABEL}"
                    client_cloud.publish(topic, json.dumps(payload_cloud), qos=1)
                    ids_sincronizados.append(id_rec)
                
                client_cloud.disconnect()
                
                # Actualizar bandera synced
                cursor.executemany("UPDATE lecturas SET synced = 1 WHERE id = ?", [(i,) for i in ids_sincronizados])
                conn.commit()
                logging.info("Sincronizados %d registros hacia Ubidots Cloud con exito", len(ids_sincronizados))
            
            conn.close()
        except Exception as e:
            logging.debug("Esperando conexion WAN para sincronizar: %s", e)
            
        time.sleep(15)

def on_message(client, userdata, msg):
    try:
        topic_parts = msg.topic.split('/')
        nodo = topic_parts[2] if len(topic_parts) >= 3 else "desconocido"
        payload = json.loads(msg.payload.decode('utf-8'))
        guardar_lectura(nodo, payload)
    except Exception as e:
        logging.error("Error procesando mensaje MQTT: %s", e)

def main():
    inicializar_bd()
    
    # Iniciar hilo de sincronización Store-and-Forward
    t_sync = threading.Thread(target=hilo_sincronizacion_cloud, daemon=True)
    t_sync.start()
    
    cliente_local = mqtt.Client(client_id="wms_gateway_local_bridge")
    cliente_local.on_message = on_message
    
    logging.info("Conectando al broker MQTT local %s:%d...", LOCAL_BROKER, LOCAL_PORT)
    cliente_local.connect(LOCAL_BROKER, LOCAL_PORT, 60)
    cliente_local.subscribe(LOCAL_TOPIC_TELEMETRY, qos=1)
    cliente_local.loop_forever()

if __name__ == "__main__":
    main()
