# Prompt 03 · Histéresis Anti-rebote y Promedio Móvil en C++

* **Herramienta:** OpenAI Codex / Claude Code
* **Fecha:** 30 de octubre de 2026
* **Consultado por:** Elioth Thomas Gomez Morales / David Jasub Sastre Arias
* **Módulos:** 04 · Hardware / 05 · Software y Red

---

## Prompt Formulado
```text
En un ESP32 en C++ para Arduino IDE, el sensor ultrasónico HC-SR04 oscila cerca de los 15 cm por el oleaje del agua. Escribe una función de histéresis no bloqueante con millis() que pase a estado crítico si la distancia es >= 15.0 cm, pero solo regrese a normal si baja de 14.5 cm, aplicando además un promedio móvil de 5 muestras.
```

## Síntesis de Respuesta
Proporcionó el patrón de búfer circular para 5 muestras con una banda de histéresis asimétrica de 0.5 cm, garantizando conmutación limpia sin bloqueos de ejecución.

## Aplicación Técnica
Se integró en la función `actualizarNivelCritico()` del firmware oficial `ESP32_Sensores.ino`, validado en el ensayo QA-01.
