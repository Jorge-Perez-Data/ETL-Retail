# Retail Analytics Data Platform (2022–2025)

Proyecto de portafolio orientado a **Data Engineering y Business Intelligence**, que simula una plataforma analítica para un negocio retail omnicanal (tienda física y e-commerce).

El proyecto cubre el flujo completo de datos: **generación → ingestión → modelado → calidad → consumo en BI**, aplicando buenas prácticas de arquitectura analítica.

---

## Objetivo del proyecto

Diseñar y construir una **plataforma analítica reproducible** que permita analizar:

- Ventas netas y ventas post devoluciones  
- Comportamiento de clientes y canales  
- Métodos de pago y ticket promedio  
- Categorías, marcas y productos  
- Impacto de estacionalidad y eventos comerciales  

El enfoque es **realista**, alineado a escenarios comunes en equipos de BI / Analytics.


## Arquitectura del pipeline

Python (Data Generation)
↓
PostgreSQL (Docker)
↓
raw → stg → mart (SQL)
↓
Power BI (Modelo estrella y dashboards)


### Capas de datos
- **raw**: datos ingestados desde archivos CSV  
- **stg**: limpieza, tipado y deduplicación  
- **mart**: modelo estrella optimizado para análisis (facts & dimensions)  

---

## Componentes principales

### 🔹 Generación de datos (Python)
- Dataset sintético retail para los años 2024–2025  
- Estacionalidad (Cyber, Navidad, fines de semana)  
- Canal online vs tienda física  
- Diferenciación realista por método de pago  
- Devoluciones por categoría y canal  
- Distribuciones no uniformes (long tail, top sellers)  

### 🔹 Base de datos
- PostgreSQL ejecutándose en Docker  
- Persistencia de datos y reconstrucción del modelo  

### 🔹 Transformaciones SQL
- Creación de tablas de staging (`stg`)  
- Construcción de modelo estrella (`mart`)  
- Separación clara entre capas técnicas y analíticas  

### 🔹 Data Quality Checks
- Integridad referencial (ventas sin dimensión asociada)  
- Validación de descuentos, cantidades y devoluciones  
- Controles pensados para evitar errores en BI  

### 🔹 Consumo analítico
- Modelo conectado a Power BI  
- Medidas DAX orientadas a negocio  
- Visualizaciones ejecutivas y operativas  

---

## Convención de nombres

- **Base de datos / SQL**: columnas en inglés (estándar analítico)  
- **Capa semántica (Power BI)**: nombres en español, orientados a negocio  
- **Medidas DAX**: definidas en español  

Esto permite mantener compatibilidad técnica sin sacrificar claridad para usuarios finales.

## Ejecución del pipeline

### Ejecutar todo el flujo en un solo paso
```powershell
.\run_pipeline.ps1
```

## Definición de KPIs

### 1 KPI: Cantidad vendida mensualmente por Año.
### 2 KPI: Comparativo Anual entre Ventas, Cantidad, Ordenes y Promedio Ordenes.
### 3 KPI: Total de Ventas por Categorías.
### 4 KPI: Ventas comparativas por País.