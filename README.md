# Retail Analytics Data Platform (2022–2025)

Proyecto de portafolio orientado a **Data Engineering y Business Intelligence**, que simula una **plataforma analítica retail omnicanal** (tienda física y e-commerce), desde la generación de datos hasta el análisis en Power BI.

El proyecto cubre el flujo completo de datos:  
**generación → ingestión → modelado → calidad → consumo en BI**, aplicando buenas prácticas de arquitectura analítica y modelamiento dimensional.

---

## Objetivo del proyecto

Diseñar y construir una **plataforma analítica reproducible** que permita analizar:

- Ventas netas y ventas post devoluciones  
- Comportamiento de clientes y canales  
- Métodos de pago y ticket promedio  
- Categorías, marcas y productos  
- Impacto de estacionalidad y eventos comerciales  
- Evolución temporal YoY (2022–2025)

El enfoque es **realista**, alineado a escenarios comunes en equipos de BI / Analytics y pensado como proyecto demostrable de portafolio.

---

## Arquitectura del pipeline

El proyecto sigue una arquitectura analítica en capas, separando generación, ingestión,
transformación y consumo de datos.

![Arquitectura del pipeline analítico](docs/arquitectura.png)

---

## Capas de datos

- **raw**  
  Datos ingestados desde archivos CSV sin transformación lógica.

- **stg**  
  Limpieza, tipado, deduplicación y validaciones básicas de negocio.

- **mart**  
  Modelo estrella optimizado para análisis (fact + dimensiones), diseñado para consumo en BI.

---

## Modelo de datos

### Tabla de hechos
**mart.fact_sales**  
Grano: *una línea por producto por orden*

Incluye:
- Ventas netas  
- Ventas post devoluciones  
- Cantidad  
- Descuentos  
- Canal de venta  
- Método de pago  

### Dimensiones
- **mart.dim_date** – calendario completo (2022–2025)  
- **mart.dim_product** – producto, subcategoría, categoría y marca  
- **mart.dim_customer** – segmento y nivel de actividad  
- **mart.dim_store** – país, región, ciudad y tipo de tienda  

---

## Componentes principales

### Generación de datos (Python)
- Dataset sintético retail para los años **2022–2025**  
- Estacionalidad (Cyber, Navidad, fines de semana)  
- Canal online vs tienda física  
- Diferenciación realista por método de pago  
- Devoluciones por categoría y canal  
- Distribuciones no uniformes (long tail y productos estrella)  

### Base de datos
- PostgreSQL ejecutándose en Docker  
- Persistencia de datos y reconstrucción del modelo de forma reproducible  

### Transformaciones SQL
- Creación de tablas de staging (`stg`)  
- Construcción del modelo estrella (`mart`)  
- Separación clara entre capas técnicas y analíticas  

### Data Quality Checks
- Integridad referencial (sin ventas huérfanas)  
- Validación de descuentos (0–100%)  
- Validación de cantidades y devoluciones  
- Controles diseñados para prevenir errores en BI  

### Consumo analítico
- Modelo conectado a Power BI  
- Medidas DAX orientadas a negocio  
- Visualizaciones ejecutivas y analíticas  

---

## KPIs y análisis implementados

- Evolución de **Ventas Netas y Ventas Post Devolución** (YoY)  
- Cantidad vendida mensual por año  
- Comparativo anual de:
  - Ventas  
  - Cantidad  
  - Órdenes  
  - Ticket promedio  
- Ventas por categoría y marca  
- Mix de canales (Online vs Tienda)  
- Ventas comparativas por país  

---

## Convención de nombres

- **Base de datos / SQL**: columnas en inglés (estándar analítico)  
- **Capa semántica (Power BI)**: nombres en español, orientados a negocio  
- **Medidas DAX**: definidas en español  

Esto permite mantener compatibilidad técnica sin sacrificar claridad para usuarios finales.

---

## Ejecución del pipeline

### Ejecutar todo el flujo en un solo paso
```powershell
.\run_pipeline.ps1
