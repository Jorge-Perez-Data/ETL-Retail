from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from datetime import date, timedelta

import numpy as np
import pandas as pd

# =========================
# Config
# =========================
SEED = 42
FECHA_INICIO = date(2022, 1, 1)
FECHA_FIN = date(2025, 12, 31)

N_CLIENTES = 8000
N_TIENDAS = 60
N_PRODUCTOS = 1200
OBJETIVO_LINEAS = 256_000

DIR_SALIDA = Path(__file__).resolve().parent.parent / "data" / "raw"
DIR_SALIDA.mkdir(parents=True, exist_ok=True)

np.random.seed(SEED)
random.seed(SEED)

# =========================
# Dominio: E-commerce deportivo
# =========================
REGIONES = ["Norte", "Centro", "Sur"]
# =========================
# Geografía LATAM (tiendas)
# =========================
GEO_CIUDADES = [
    # country, region_admin, city, lat, lon, region_macro (Norte/Centro/Sur)
    ("Chile", "Metropolitana", "Santiago", -33.4489, -70.6693, "Centro"),
    ("Chile", "Valparaíso", "Viña del Mar", -33.0245, -71.5518, "Centro"),
    ("Chile", "Biobío", "Concepción", -36.8270, -73.0498, "Sur"),

    ("Argentina", "Buenos Aires", "Buenos Aires", -34.6037, -58.3816, "Centro"),
    ("Argentina", "Córdoba", "Córdoba", -31.4201, -64.1888, "Centro"),
    ("Argentina", "Santa Fe", "Rosario", -32.9587, -60.6930, "Centro"),

    ("Peru", "Lima", "Lima", -12.0464, -77.0428, "Centro"),
    ("Peru", "Arequipa", "Arequipa", -16.4090, -71.5375, "Sur"),

    ("Colombia", "Bogotá D.C.", "Bogotá", 4.7110, -74.0721, "Norte"),
    ("Colombia", "Antioquia", "Medellín", 6.2442, -75.5812, "Norte"),
    ("Colombia", "Valle del Cauca", "Cali", 3.4516, -76.5320, "Norte"),

    ("Mexico", "CDMX", "Ciudad de México", 19.4326, -99.1332, "Norte"),
    ("Mexico", "Jalisco", "Guadalajara", 20.6597, -103.3496, "Norte"),
    ("Mexico", "Nuevo León", "Monterrey", 25.6866, -100.3161, "Norte"),

    ("Brazil", "São Paulo", "São Paulo", -23.5505, -46.6333, "Sur"),
    ("Brazil", "Rio de Janeiro", "Rio de Janeiro", -22.9068, -43.1729, "Sur"),
    ("Brazil", "Minas Gerais", "Belo Horizonte", -19.9167, -43.9345, "Sur"),
]

SEGMENTOS = ["Consumidor", "Corporativo", "Hogar"]
NIVELES_ACTIVIDAD = ["Low", "Medium", "High"]


TIPOS_TIENDA = ["Mall", "Street", "Outlet", "Dark Store"]

CANALES = ["Online", "Tienda"]
METODOS_PAGO = ["Tarjeta de Credito", "Tarjeta de Debito", "Transferencia", "Efectivo", "WebPay"]
TIPOS_ENVIO = ["Same Day", "Next Day", "Standard", "Pickup"]

CATEGORIAS = {
    "Running": ["Zapatillas Running", "Poleras", "Shorts", "Calcetines", "Relojes GPS", "Accesorios"],
    "Tenis": ["Raquetas Tenis", "Cuerdas", "Overgrips", "Zapatillas Tenis", "Pelotas Tenis", "Mochilas"],
    "Padel": ["Palas Padel", "Overgrips", "Pelotas Padel", "Zapatillas Padel", "Protectores", "Bolsos"],
    "Fitness": ["Mancuernas", "Bandas Elasticas", "Colchonetas", "Guantes", "Botellas", "Accesorios"],
}

MARCAS = {
    "Running": ["Nike", "Adidas", "ASICS", "New Balance", "Saucony", "Under Armour"],
    "Tenis": ["Wilson", "Babolat", "Head", "Yonex", "Prince"],
    "Padel": ["Bullpadel", "Nox", "Adidas", "Babolat", "Head", "StarVie"],
    "Fitness": ["Nike", "Adidas", "Reebok", "Under Armour", "Everlast", "Domyos"],
}

PRECIO_BASE = {
    "Zapatillas Running": (65000, 160000),
    "Zapatillas Tenis": (70000, 180000),
    "Zapatillas Padel": (70000, 180000),
    "Raquetas Tenis": (90000, 280000),
    "Palas Padel": (90000, 320000),
    "Relojes GPS": (120000, 450000),
    "Pelotas Tenis": (7000, 18000),
    "Pelotas Padel": (7000, 18000),
    "Cuerdas": (9000, 25000),
    "Overgrips": (4000, 12000),
    "Mochilas": (25000, 90000),
    "Bolsos": (25000, 110000),
    "Poleras": (12000, 45000),
    "Shorts": (12000, 45000),
    "Calcetines": (4000, 15000),
    "Protectores": (6000, 25000),
    "Accesorios": (4000, 25000),
    "Mancuernas": (15000, 120000),
    "Bandas Elasticas": (4000, 18000),
    "Colchonetas": (9000, 35000),
    "Guantes": (8000, 28000),
    "Botellas": (4000, 18000),
}

# Tasa de devolucion por subcategoria: (online, tienda)
TASA_DEVOLUCION = {
    "Zapatillas Running": (0.10, 0.05),
    "Zapatillas Tenis": (0.11, 0.06),
    "Zapatillas Padel": (0.11, 0.06),
    "Poleras": (0.08, 0.03),
    "Shorts": (0.08, 0.03),
    "Raquetas Tenis": (0.03, 0.02),
    "Palas Padel": (0.04, 0.02),
    "Relojes GPS": (0.03, 0.02),
}

# Eventos (picos + rango de descuento)
EVENTOS = [
    ("Cyber", date(2024, 6, 3), date(2024, 6, 5), 1.8, (0.15, 0.45)),
    ("Fiestas Patrias", date(2024, 9, 10), date(2024, 9, 22), 1.2, (0.05, 0.20)),
    ("Navidad", date(2024, 12, 1), date(2024, 12, 24), 1.5, (0.05, 0.25)),
    ("Cyber", date(2025, 6, 2), date(2025, 6, 4), 1.9, (0.15, 0.50)),
    ("Fiestas Patrias", date(2025, 9, 10), date(2025, 9, 22), 1.2, (0.05, 0.20)),
    ("Navidad", date(2025, 12, 1), date(2025, 12, 24), 1.6, (0.05, 0.30)),
]

# =========================
# Helpers
# =========================
def rango_fechas(d0: date, d1: date):
    cur = d0
    while cur <= d1:
        yield cur
        cur += timedelta(days=1)

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def elegir(items, weights, size=1):
    w = np.array(weights, dtype=float)
    w = w / w.sum()
    idx = np.random.choice(len(items), size=size, replace=True, p=w)
    return [items[i] for i in idx]

def pesos_pareto(n, alpha=1.18):
    r = np.arange(1, n + 1)
    w = 1 / (r ** alpha)
    return w / w.sum()

def multiplicador_estacional(d: date):
    m = 1.0
    if d.month in [1, 2]:
        m *= 1.10
    if d.month in [3]:
        m *= 1.08
    if d.month in [11]:
        m *= 1.10
    if d.weekday() >= 5:
        m *= 1.06
    return m

def mult_evento_y_descuento(d: date):
    mult = 1.0
    disc_lo, disc_hi = (0.0, 0.15)
    for _, s, e, m, disc_rng in EVENTOS:
        if s <= d <= e:
            mult *= m
            disc_lo, disc_hi = disc_rng
    return mult, disc_lo, disc_hi

def mezcla_canal(d: date):
    online = 0.62
    if d.weekday() >= 5:
        online += 0.08
    for _, s, e, _, _ in EVENTOS:
        if s <= d <= e:
            online += 0.10
            break
    online = clamp(online, 0.45, 0.85)
    return [online, 1 - online]  # Online, Tienda

def envio_y_entrega(region: str, canal: str):
    if canal != "Online":
        return None, 0

    if region == "Centro":
        tipos = ["Same Day", "Next Day", "Standard", "Pickup"]
        w = [0.18, 0.40, 0.32, 0.10]
        base = {"Same Day": 0, "Next Day": 1, "Standard": 2, "Pickup": 1}
    elif region == "Norte":
        tipos = ["Next Day", "Standard", "Pickup"]
        w = [0.15, 0.70, 0.15]
        base = {"Next Day": 2, "Standard": 4, "Pickup": 2}
    else:  # Sur
        tipos = ["Next Day", "Standard", "Pickup"]
        w = [0.18, 0.67, 0.15]
        base = {"Next Day": 2, "Standard": 4, "Pickup": 2}

    tipo = elegir(tipos, w, 1)[0]
    dias = int(clamp(np.random.normal(base[tipo], 1.0), 0, 12))
    return tipo, dias

def elegir_metodo_pago(monto_orden: float, canal: str) -> str:
    """
    Queremos montos bien distintos por metodo:
    - Transferencia/Credito: tickets altos
    - Debito/WebPay: medio
    - Efectivo: bajo (casi solo en tienda)
    """
    if canal == "Online":
        if monto_orden >= 220000:
            return elegir(["Transferencia", "Tarjeta de Credito", "WebPay"], [0.45, 0.45, 0.10], 1)[0]
        if monto_orden >= 90000:
            return elegir(["Tarjeta de Credito", "WebPay", "Tarjeta de Debito"], [0.55, 0.35, 0.10], 1)[0]
        return elegir(["WebPay", "Tarjeta de Debito", "Tarjeta de Credito"], [0.55, 0.35, 0.10], 1)[0]
    else:  # Tienda
        if monto_orden >= 220000:
            return elegir(["Tarjeta de Credito", "Transferencia", "Tarjeta de Debito"], [0.55, 0.25, 0.20], 1)[0]
        if monto_orden >= 90000:
            return elegir(["Tarjeta de Debito", "Tarjeta de Credito", "Efectivo"], [0.55, 0.30, 0.15], 1)[0]
        return elegir(["Efectivo", "Tarjeta de Debito", "WebPay"], [0.55, 0.35, 0.10], 1)[0]

@dataclass
class Producto:
    id_producto: int
    nombre_producto: str
    categoria: str
    subcategoria: str
    marca: str
    es_top_ventas: bool
    precio_min: int
    precio_max: int

def construir_productos(n: int) -> pd.DataFrame:
    subcats = [(cat, sub) for cat, subs in CATEGORIAS.items() for sub in subs]
    prefs = []
    for _, sub in subcats:
        if "Zapatillas" in sub:
            prefs.append(5)
        elif sub in ["Poleras", "Shorts", "Calcetines", "Accesorios", "Overgrips", "Pelotas Tenis", "Pelotas Padel"]:
            prefs.append(3)
        else:
            prefs.append(2)
    probs = np.array(prefs, float); probs /= probs.sum()
    picks = np.random.choice(len(subcats), size=n, replace=True, p=probs)

    productos: list[Producto] = []
    for i in range(n):
        cat, sub = subcats[picks[i]]
        marca = random.choice(MARCAS.get(cat, ["Generic"]))
        lo, hi = PRECIO_BASE.get(sub, (8000, 60000))
        top = ("Zapatillas" in sub) or (sub in ["Overgrips", "Pelotas Tenis", "Pelotas Padel", "Poleras", "Accesorios"])
        if random.random() < 0.08:
            top = True
        nombre = f"{marca} {sub} {random.choice(['Pro', 'Elite', 'Core', 'Sport', 'Max', 'Lite'])} {random.randint(1, 999)}"
        productos.append(Producto(i + 1, nombre, cat, sub, marca, top, lo, hi))

    return pd.DataFrame([p.__dict__ for p in productos])

def construir_clientes(n: int) -> pd.DataFrame:
    w_reg = [0.20, 0.55, 0.25]
    w_seg = [0.70, 0.18, 0.12]
    w_act = [0.30, 0.50, 0.20]
    return pd.DataFrame({
        "id_cliente": np.arange(1, n + 1),
        "segmento": elegir(SEGMENTOS, w_seg, n),
        "region": elegir(REGIONES, w_reg, n),
        "nivel_actividad": elegir(NIVELES_ACTIVIDAD, w_act, n),
    })

def construir_tiendas(n: int) -> pd.DataFrame:
    w_typ = [0.35, 0.35, 0.20, 0.10]

    geo = pd.DataFrame(
        GEO_CIUDADES,
        columns=["pais", "region_admin", "ciudad", "latitud", "longitud", "region_tienda"]
    )

    # Pesos por país (ajusta si quieres más/menos presencia)
    w_pais = {
        "Chile": 0.28,
        "Argentina": 0.18,
        "Peru": 0.12,
        "Colombia": 0.14,
        "Mexico": 0.16,
        "Brazil": 0.12,
    }

    geo["w"] = geo["pais"].map(w_pais).fillna(0.10)
    geo["w"] = geo["w"] / geo["w"].sum()

    picks = np.random.choice(geo.index, size=n, replace=True, p=geo["w"].values)
    chosen = geo.loc[picks].reset_index(drop=True)

    tiendas = pd.DataFrame({
        "id_tienda": np.arange(1, n + 1),
        "region_tienda": chosen["region_tienda"],  # Norte/Centro/Sur (macro)
        "tipo_tienda": elegir(TIPOS_TIENDA, w_typ, n),
        "pais": chosen["pais"],
        "region_admin": chosen["region_admin"],
        "ciudad": chosen["ciudad"],
        "latitud": chosen["latitud"].astype(float),
        "longitud": chosen["longitud"].astype(float),
    })

    return tiendas


def simular_ventas(clientes: pd.DataFrame, tiendas: pd.DataFrame, productos: pd.DataFrame) -> pd.DataFrame:
    # Pesos producto (Pareto) + boost top ventas
    w_base = pesos_pareto(len(productos), alpha=1.18)
    boost = np.where(productos["es_top_ventas"].values, 1.6, 1.0)
    w_prod = w_base * boost
    w_prod = w_prod / w_prod.sum()

    # Peso clientes por actividad
    mapa_act = {"Low": 0.65, "Medium": 1.0, "High": 1.6}
    w_cli = clientes["nivel_actividad"].map(mapa_act).to_numpy()
    w_cli = w_cli / w_cli.sum()

    dias = (FECHA_FIN - FECHA_INICIO).days + 1
    base_lineas_dia = OBJETIVO_LINEAS / dias

    filas = []
    id_orden = 1

    for f in rango_fechas(FECHA_INICIO, FECHA_FIN):
        est = multiplicador_estacional(f)
        mult_ev, d_lo, d_hi = mult_evento_y_descuento(f)
        lam = base_lineas_dia * est * mult_ev
        lineas_dia = int(np.random.poisson(lam))

        # promedio 2 lineas por orden
        n_ordenes = max(1, int(lineas_dia / 2.0))
        w_canal = mezcla_canal(f)

        for _ in range(n_ordenes):
            id_cliente = int(np.random.choice(clientes["id_cliente"].values, p=w_cli))
            region_cliente = clientes.loc[clientes["id_cliente"] == id_cliente, "region"].values[0]

            # tienda más probable de misma region
            misma = (tiendas["region_tienda"].values == region_cliente)
            w_tienda = np.where(misma, 1.6, 1.0)
            w_tienda = w_tienda / w_tienda.sum()
            id_tienda = int(np.random.choice(tiendas["id_tienda"].values, p=w_tienda))

            canal = elegir(CANALES, w_canal, 1)[0]

            # lineas por orden
            n_lineas = int(np.random.choice([1, 2, 3, 4], p=[0.46, 0.32, 0.16, 0.06]))

            lineas_tmp = []
            total_orden = 0.0

            for id_linea in range(1, n_lineas + 1):
                id_producto = int(np.random.choice(productos["id_producto"].values, p=w_prod))
                prod = productos.loc[productos["id_producto"] == id_producto].iloc[0]

                # cantidad
                if prod.subcategoria in ["Pelotas Tenis", "Pelotas Padel", "Overgrips", "Calcetines", "Bandas Elasticas"]:
                    cantidad = int(np.random.choice([1, 2, 3, 4, 5], p=[0.20, 0.28, 0.24, 0.18, 0.10]))
                else:
                    cantidad = int(np.random.choice([1, 2, 3], p=[0.70, 0.22, 0.08]))

                base_precio = np.random.uniform(prod.precio_min, prod.precio_max)
                premium = 1.0 + (0.08 if prod.marca in ["Nike", "Adidas", "ASICS", "Wilson", "Babolat"] else 0.0)
                precio_unitario = round(base_precio * premium, 2)

                desc = float(np.random.uniform(d_lo, d_hi))
                if canal == "Online":
                    desc = clamp(desc + np.random.uniform(0.00, 0.06), 0.0, 0.60)
                descuento_pct = round(desc, 3)

                bruto = precio_unitario * cantidad
                venta_neta = round(bruto * (1 - descuento_pct), 2)

                tipo_envio, dias_entrega = envio_y_entrega(region_cliente, canal)

                rr_online, rr_tienda = TASA_DEVOLUCION.get(prod.subcategoria, (0.04, 0.02))
                tasa = rr_online if canal == "Online" else rr_tienda
                es_devuelto = 1 if random.random() < tasa else 0
                monto_devolucion = round(venta_neta * (1.0 if es_devuelto else 0.0), 2)

                total_orden += venta_neta

                lineas_tmp.append({
                    "id_orden": id_orden,
                    "id_linea": id_linea,
                    "fecha_orden": f.isoformat(),
                    "id_cliente": id_cliente,
                    "id_tienda": id_tienda,
                    "id_producto": id_producto,
                    "canal": canal,
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "descuento_pct": descuento_pct,
                    "venta_neta": venta_neta,
                    "tipo_envio": tipo_envio,
                    "dias_entrega": int(dias_entrega),
                    "es_devuelto": int(es_devuelto),
                    "monto_devolucion": monto_devolucion,
                })

            # método de pago a nivel de orden (clave para que los montos sean distintos por método)
            metodo_pago = elegir_metodo_pago(total_orden, canal)
            for r in lineas_tmp:
                r["metodo_pago"] = metodo_pago

            filas.extend(lineas_tmp)
            id_orden += 1

    df = pd.DataFrame(filas)

    if len(df) > OBJETIVO_LINEAS:
        df = df.sample(n=OBJETIVO_LINEAS, random_state=SEED).sort_values(["fecha_orden", "id_orden", "id_linea"])

    return df.reset_index(drop=True)

def main():
    print(f"Escribiendo CSV en: {DIR_SALIDA}")

    clientes = construir_clientes(N_CLIENTES)
    tiendas = construir_tiendas(N_TIENDAS)
    productos = construir_productos(N_PRODUCTOS)
    ventas = simular_ventas(clientes, tiendas, productos)

    # Mantenemos nombres de archivos igual para no tocar loader
    clientes.to_csv(DIR_SALIDA / "customers.csv", index=False)
    tiendas.to_csv(DIR_SALIDA / "stores.csv", index=False)
    productos.to_csv(DIR_SALIDA / "products.csv", index=False)
    ventas.to_csv(DIR_SALIDA / "sales.csv", index=False)

    print("OK:")
    print(" clientes :", len(clientes))
    print(" tiendas  :", len(tiendas))
    print(" productos:", len(productos))
    print(" ventas   :", len(ventas))

if __name__ == "__main__":
    main()
