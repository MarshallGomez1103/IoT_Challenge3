# WMS · Water Management System

[![GitHub Pages](https://img.shields.io/badge/Gemelo%20Digital%203D-GitHub%20Pages-0ea5e9?style=for-the-badge&logo=three.js)](https://marshallgomez1103.github.io/IoT_Challenge3/)
[![Wiki Oficial](https://img.shields.io/badge/Wiki%20T%C3%A9cnica-12%20M%C3%B3dulos-6366f1?style=for-the-badge&logo=github)](https://github.com/MarshallGomez1103/IoT_Challenge3/wiki)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald?style=for-the-badge)](LICENSE)
[![Hardware](https://img.shields.io/badge/Hardware-ESP32%20%2B%20RPi%205-orange?style=for-the-badge)](docs/)

Sistema distribuido de monitoreo, telemetría y alerta temprana para la gestión y mitigación del riesgo de desabastecimiento hídrico en reservorios agrícolas y comunitarios de la **Sabana Centro de Cundinamarca**, desarrollado para el **Challenge #3 — Internet de las Cosas**, Facultad de Ingeniería, **Universidad de La Sabana (2026-2)**.

---

## 🌐 Visor 3D Interactivo (Gemelo Digital)

El proyecto cuenta con un gemelo digital interactivo desarrollado en **Three.js** con simulación dinámica de la columna de agua, sombreado fotométrico y visualización por capas arquitectónicas:

👉 **[Acceder al Gemelo Digital en GitHub Pages](https://marshallgomez1103.github.io/IoT_Challenge3/)**

---

## 📚 Documentación Técnica (Wiki)

La documentación exhaustiva del proyecto está publicada en la [Wiki Oficial del Repositorio](https://github.com/MarshallGomez1103/IoT_Challenge3/wiki) estructurada en 12 módulos:

1. [01 · Contexto y Requisitos](https://github.com/MarshallGomez1103/IoT_Challenge3/wiki/01-contexto-y-requisitos)
2. [02 · Equipo y Roles](https://github.com/MarshallGomez1103/IoT_Challenge3/wiki/02-equipo-y-roles)
3. [03 · Solución y Arquitectura](https://github.com/MarshallGomez1103/IoT_Challenge3/wiki/03-solucion-y-arquitectura)
4. [04 · Hardware y Esquemáticos](https://github.com/MarshallGomez1103/IoT_Challenge3/wiki/04-hardware)
5. [05 · Software y Red](https://github.com/MarshallGomez1103/IoT_Challenge3/wiki/05-software-y-red)
6. [06 · Módulo de IA](https://github.com/MarshallGomez1103/IoT_Challenge3/wiki/06-modulo-ia)
7. [07 · Pruebas y Validación](https://github.com/MarshallGomez1103/IoT_Challenge3/wiki/07-pruebas-y-validacion)
8. [08 · Resultados y Análisis](https://github.com/MarshallGomez1103/IoT_Challenge3/wiki/08-resultados-y-analisis)
9. [09 · Modelo de Negocio](https://github.com/MarshallGomez1103/IoT_Challenge3/wiki/09-modelo-de-negocio)
10. [10 · Conclusiones y Retos](https://github.com/MarshallGomez1103/IoT_Challenge3/wiki/10-conclusiones)
11. [11 · Declaración de IA](https://github.com/MarshallGomez1103/IoT_Challenge3/wiki/11-declaracion-ia)
12. [12 · Anexos y Referencias](https://github.com/MarshallGomez1103/IoT_Challenge3/wiki/12-anexos)

---

## 🏛️ Arquitectura del Sistema

WMS opera bajo el paradigma de cuatro capas con filosofía ***Offline-First***:

```
[ Capa 1: Borde Físico ]       ESP32 · Ultrasonido HC-SR04 + BMP180 + DHT11 + LDR
            │                   Superloop cooperativo millis() · Alarmas Buzzer/RGB/LCD
            ▼ MQTT (1883)
[ Capa 2: Gateway Perimetral ] Raspberry Pi 5 · Broker Mosquitto + SQLite (Store-and-Forward)
            │                   Demonio Python wms-bridge.service
            ├──────────────────────────────────────────┐
            ▼ HTTPS / JSON estricto                    ▼ MQTT / TLS
[ Capa 3: Analítica de IA ]                    [ Capa 4: Nube & Dashboards ]
Google Gemini 2.5 Flash                        Ubidots IoT Platform
(Diagnósticos y anomalías con fallback)         (Series de tiempo, alertas y ACK)
```

### Algoritmo de Riesgo Multiplicativo
Fundamentado en los **Planes de Seguridad del Agua (PSA) de la OMS** y la norma **IEC/ISO 31010:2019 (AMFE)**:

$$R_{\text{total}} = S_{\text{nivel}} \cdot (1 + 0.25 \cdot F_{\text{clima}})$$

Donde $S_{\text{nivel}}$ representa la severidad intrínseca del tirante de agua y $F_{\text{clima}}$ es el factor ambiental ponderado según el análisis de sensibilidad **FAO-56 Penman-Monteith** (NASA POWER Chía 2000–2025):
* Radiación solar ($40\%$)
* Temperatura ambiente ($25\%$)
* Déficit de presión de vapor ($25\%$)
* Presión barométrica ($10\%$)

---

## 📂 Estructura del Repositorio

```text
IoT_Challenge3/
├── firmware/
│   └── esp32_wms/
│       └── esp32_wms.ino             # Firmware no bloqueante C++ (ESP32)
├── gateway/
│   ├── bridge_mqtt.py                # Bridge MQTT local -> SQLite -> Ubidots
│   ├── ia_analyst.py                 # Orquestador Google Gemini 2.5 Flash
│   ├── requirements.txt              # Dependencias de Python
│   └── systemd/
│       └── wms-bridge.service        # Servicio systemd de autoarranque
├── prompts_ai/                       # Auditoría y registro de prompts de IA
│   ├── README.md                     # Índice de prompts y políticas éticas
│   └── *.md                          # Transcripciones y aplicación técnica
├── docs/
│   ├── plano_hardware_wms_v3_4k.png  # Plano esquemático de hardware en 4K
│   ├── plano_wms_alta_resolucion.png # Plano de conexiones de alta resolución
│   └── gemelo_digital_3d.html        # Respaldo local del visor Three.js
├── index.html                        # Visor 3D desplegado en GitHub Pages
├── LICENSE                           # Licencia MIT
└── README.md                         # Esta guía
```

---

## 👥 Equipo de Desarrollo

| Integrante | Rol en el Proyecto |
| :--- | :--- |
| **David Jasub Sastre Arias** | Líder de Proyecto · Arquitectura General y Telemetría Cloud |
| **Elioth Thomas Gomez Morales** | Ingeniero de Hardware, Firmware, Gateway Perimetral e IA |
| **Andrés Felipe Suárez Banoy** | Jefe de Documentación, Diagramación Técnica y Gemelo Digital 3D |

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consultar el archivo [LICENSE](LICENSE) para más detalles.
