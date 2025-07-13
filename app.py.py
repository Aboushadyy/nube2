import streamlit as st
import pandas as pd
import os
from utils import (
    cargar_inventario,
    cargar_historial,
    agregar_producto,
    actualizar_stock,
    encriptar,
    validar_usuario,
    eliminar_producto
)

st.set_page_config(page_title="📦 Inventario Amazon IB", layout="wide")

# Carga de datos desde Supabase
inventario = cargar_inventario()
historial = cargar_historial()

# Login
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.markdown("### 🔐 Iniciar sesión")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if validar_usuario(user, pwd):
            st.session_state.login = True
            st.rerun()
        else:
            st.warning("Credenciales incorrectas")
    st.stop()

st.title("📦 Inventario Amazon IB")
st.caption("App creada por Abdullah")

# Agregar productos
st.subheader("➕ Agregar productos")
bodega_nueva = st.text_input("Nombre de la bodega")
input_productos = st.text_area("Pega productos (Ejemplo: Producto1: 100)", height=150)

if st.button("Agregar al inventario"):
    if not bodega_nueva.strip():
        st.warning("Por favor, escribe el nombre de la bodega.")
    else:
        lineas = input_productos.strip().split("\n")
        errores = 0
        for linea in lineas:
            if not linea.strip():
                continue
            partes = linea.split(":")
            if len(partes) < 2:
                st.warning(f"Formato incorrecto: {linea}")
                errores += 1
                continue
            nombre = partes[0].strip()
            try:
                cantidad = int(partes[1].strip())
                agregar_producto(nombre, cantidad, bodega_nueva.strip())
            except ValueError:
                st.warning(f"Cantidad inválida en: {linea}")
                errores += 1
            except Exception as e:
                st.error(f"Error inesperado en: {linea} → {e}")
                errores += 1
        if errores == 0:
            st.success("✅ Productos agregados correctamente.")
        else:
            st.warning(f"Se detectaron {errores} líneas con errores.")
        st.rerun()

# Ver inventario
st.subheader("📊 Inventario actual")
busqueda = st.text_input("Buscar producto")
inventario_filtrado = inventario.copy()

if busqueda:
    inventario_filtrado = inventario_filtrado[
        inventario_filtrado["producto"].str.contains(busqueda, case=False)
    ]

if inventario_filtrado.empty:
    st.info("No hay productos en el inventario.")
else:
    for i, row in inventario_filtrado.iterrows():
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 2, 2])
        col1.markdown(f"**{row['producto']}**")
        agregar = col2.number_input("➕", min_value=0, key=f"agregar_{i}")
        quitar = col3.number_input("➖", min_value=0, key=f"quitar_{i}")
        if col2.button("✔", key=f"a_{i}") and agregar > 0:
            actualizar_stock(row.name, agregar, "agregar")
            st.rerun()
        if col3.button("✔", key=f"q_{i}") and quitar > 0:
            actualizar_stock(row.name, quitar, "quitar")
            st.rerun()
        col4.markdown(f"📦 Stock: **{int(row['stock'])}**")
        col5.markdown(f"🏷️ Bodega: {row['bodega']}")
        if st.button("🗑️ Eliminar", key=f"del_{i}"):
            eliminar_producto(row.name)
            st.rerun()

# Historial
st.subheader("🕓 Historial de movimientos")

if historial.empty:
    st.info("No hay movimientos registrados todavía.")
else:
    filtrado = historial.copy()
    filtrado["fecha"] = pd.to_datetime(filtrado["fecha"], errors="coerce")
    filtrado = filtrado.sort_values("fecha", ascending=False)
    filtrado["fecha"] = filtrado["fecha"].dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(filtrado, use_container_width=True)

# Descargar
st.subheader("⬇️ Descargar datos")
col1, col2 = st.columns(2)
col1.download_button("📥 Inventario CSV", inventario.to_csv(index=False), "inventario.csv", "text/csv")
col2.download_button("📥 Historial CSV", historial.to_csv(index=False), "historial.csv", "text/csv")
