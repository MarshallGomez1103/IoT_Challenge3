# Prompt 01 · Generación de Esquema JSON para Gemini 2.5 Flash

* **Herramienta:** Google Gemini
* **Fecha:** 28 de octubre de 2026
* **Consultado por:** Elioth Thomas Gomez Morales
* **Módulo:** 06 · Módulo de IA

---

## Prompt Formulado
```text
Necesito un script en Python con google-genai para llamar a gemini-2.5-flash enviando un resumen de 24 horas de telemetría de agua y clima. El modelo DEBE responder obligatoriamente en JSON estricto sin saludos ni texto introductorio, con las llaves: nivel_riesgo_sugerido, diagnostico, anomalia_detectada (booleano) y acciones_recomendadas (lista). ¿Cómo se configura el schema con Pydantic o el cliente moderno?
```

## Síntesis de Respuesta
La herramienta explicó la configuración de `generation_config` utilizando el parámetro `response_mime_type="application/json"` y la definición de esquemas de respuesta para forzar salida JSON estructurada sin texto conversacional.

## Aplicación Técnica
Se integró en `gateway/ia_analyst.py` para la ingesta periódica de diagnósticos en el gateway Raspberry Pi 5.
