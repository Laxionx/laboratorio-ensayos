# laboratorio-ensayos

Laboratorio de ensayos al fuego, **fase 1: preparación de muestras**. Calcula cuánto error de muestreo mete cada etapa de un protocolo de preparación (chancar, dividir, pulverizar, tomar la alícuota de 30 o 50 g) con la ecuación del error fundamental de Gy, cuánto se acumula, y cuántos granos de oro caen en la alícuota cuando el oro es grueso. Implementado desde la literatura y validado contra números publicados.

Sin fusión ni química del ensayo (fase 2). Los códigos de preparación PREP-31 y PREP-31B son públicos de ALS (alsglobal.com); sin afiliación.

## Qué hace

- **Protocolo:** varianza de Gy por etapa y acumulada (suma de varianzas relativas), con un nomograma de muestreo en el que la ruta del protocolo se recorre etapa por etapa (reducir el tamaño es un tramo horizontal; dividir, uno vertical). Presets PREP-31, PREP-31B y el protocolo de una mina de oro de Minnitt (2017).
- **Oro grueso:** granos esperados en la alícuota, simulación de 1 000 ensayos repetidos (Poisson, semilla fija), recomendación de screen fire assay si se esperan menos de 20 granos (criterio de Clifton).
- **Validación:** tabla y gráficos de lo calculado frente a lo publicado.
- **Guía:** el error fundamental, los factores y qué dato pide cada uno, y qué errores de muestreo NO se modelan.

## La ecuación

```
σ² = c·f·g·ℓ·dN³·(1/MS − 1/ML) = K·dN^α·(1/MS − 1/ML)      (dN en cm, masas en g)
```

Las dos formas son la misma: K y α **se calibran por mineral** (ensayo de heterogeneidad o árbol de muestreo) y nunca se suponen. Los del ejemplo (DSA: K = 167,4, α = 1,123; SFA: K = 2 539, α = 1,03) son los que Minnitt (2017) calibró para una mena de oro de Witwatersrand y no valen para otro mineral. El tamaño dN de cada etapa sale de su especificación («70 % bajo 2 mm») más una forma Rosin-Rammler con pendiente m **supuesta** (la app muestra cuánto cambia el error con m, porque dN entra al cubo). La corrección por masa del lote (1/MS − 1/ML) se puede apagar para reproducir la Tabla VIII de Minnitt (2017), que la omite.

## Cómo correrlo

```bash
pip install -e ".[dev,app]"
streamlit run app/streamlit_app.py
pytest --cov=muestreo
```

Para la nube basta `requirements.txt` (versiones fijas; `conminucion` fijado a un commit). La granulometría usa `conminucion.sizes` de [simulador-conminucion](https://github.com/Laxionx/simulador-conminucion).

## Validación

Cortes fijados antes de correr ([tests/test_validacion.py](tests/test_validacion.py)). Lo que no cuadra se muestra tal cual, sin `xfail` ni retoques.

| Fuente | Publicado | Calculado | ¿Cuadra? |
|---|---|---|---|
| Minnitt (2017), *J. SAIMM* 117(2), Tabla VIII | 19 varianzas por etapa (DSA y SFA) | σ² = K·dN^α/MS, sin corrección de lote | **18 de 19** al redondeo publicado. No cuadra una fila de SFA (2 055,56 g, dN 0,0001 cm): publica 0,00005 y sale 0,000094; la fila siguiente sí cuadra |
| Chieregati (2017), *Mining Engineering*, Tabla 2 | 3 etapas y total (0,1079; 32,8 %) | IHL = 3,9787·d^1,6689 con corrección de lote | **14 de 14** al redondeo publicado |
| Clifton et al. (1969), USGS PP 625-C, Fig. 4 | ±34/54 % (20), ±20/25 % (75), ±9/10 % (400), −50/+100 % (7) | ecuaciones (11) y (12) del artículo | **7 de 8** a ±2 puntos; el límite inferior de 7 partículas sale −46,6 % (3,4 puntos: la etiqueta de la figura es redonda). El Poisson exacto da −59,8 % |
| Minnitt, Rice y Spangenberg (2007), *J. SAIMM* 107(8) | 29,58 %, ≈16 kg y 0,9 cm | con los datos impresos: 11,69 %, 2,50 kg y 1,69 cm | **no cuadra: hallazgo, no validación** (ver abajo) |

**Minnitt (2007).** El artículo imprime ℓ = 0,000035, pero sus resultados implican un valor 6,4 veces mayor (c·f·g·ℓ = 448 en lugar de 70, ℓ efectivo 0,000224); aquí se usa la fórmula con los datos impresos. Con 448 se reproducen los tres problemas (29,58 %, 16 015 g, 0,91 cm) y el del apéndice (32,49 %), y lo que sí cuadra del apéndice es el tamaño de liberación dℓ = 1,25·(3,5e-5)^(1/1,5) = 0,001337 cm. Es una errata del artículo, no una validación de la fórmula.

La simulación de oro grueso se valida contra Poisson: media y desviación de los 1 000 ensayos dentro de 3σ del valor analítico (error de Monte Carlo), con semilla fija.

## Límites

- Solo el error fundamental de muestreo de Gy: no hay errores de delimitación y extracción, de preparación (contaminación, pérdidas), de ponderación, de segregación y agrupamiento, ni el error analítico.
- K y α son del ejemplo publicado; cada laboratorio debe calibrar los suyos.
- Los granos de oro se suponen de un solo tamaño y forma (esfera o cubo), libres y al azar.
- Los equipos de preparación no se simulan: el tamaño de cada etapa sale de la especificación del protocolo.

## Licencia

MIT.
