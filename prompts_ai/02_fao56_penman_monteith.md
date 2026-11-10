# Prompt 02 · Sensibilidad Agroclimática FAO-56 Penman-Monteith

* **Herramienta:** Anthropic Claude 3.5 Sonnet
* **Fecha:** 2 de noviembre de 2026
* **Consultado por:** Andrés Felipe Suárez Banoy
* **Módulos:** 03 · Solución y Arquitectura / 08 · Resultados y Análisis

---

## Prompt Formulado
```text
Tenemos un tanque de agua en Chía, Cundinamarca (altitud 2560 msnm, presión 75 kPa, temp media 14 °C). Queremos fundamentar el factor climático del riesgo hídrico basándonos en la ecuación FAO-56 Penman-Monteith. ¿Cómo se descomponen los términos de radiación neta frente al término aerodinámico (déficit de presión de vapor y viento) para justificar los pesos relativos de los sensores (LDR, DHT11, BMP180)?
```

## Síntesis de Respuesta
Suministró la descomposición analítica de la ecuación estándar FAO-56, calculando la pendiente de saturación psicrométrica y demostrando que la radiación solar neta y el déficit de presión de vapor concentran más del 70 % de la evapotranspiración potencial en la Sabana Centro.

## Aplicación Técnica
Fundamentó los pesos de los sensores en el factor climático $F_{\text{clima}}$ del algoritmo de riesgo multiplicativo.
