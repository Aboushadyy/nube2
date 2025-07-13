import pandas as pd
from datetime import datetime, timedelta
import hashlib
from supabase import create_client, Client
import os

# Configuración de Supabase desde variables de entorno
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# FUNCIONES

def cargar_inventario():
    res = supabase.table("inventario").select("*").execute()
    data = res.data or []
    return pd.DataFrame(data)

def cargar_historial():
    res = supabase.table("historial").select("*").order("fecha", desc=True).execute()
    data = res.data or []
    return pd.DataFrame(data)

def guardar_historial(fecha, producto, movimiento, cantidad, bodega, nota=""):
    supabase.table("historial").insert({
        "fecha": fecha,
        "producto": producto,
        "movimiento": movimiento,
        "cantidad": cantidad,
        "bodega": bodega,
        "nota": nota
    }).execute()

def agregar_producto(nombre, cantidad, bodega):
    nombre = nombre.strip().lower().capitalize()
    df = cargar_inventario()

    now = datetime.utcnow() - timedelta(hours=6)

    if nombre in df["producto"].values:
        fila = df[df["producto"] == nombre].iloc[0]
        nuevo_stock = int(fila["stock"]) + cantidad
        supabase.table("inventario").update({
            "stock": nuevo_stock,
            "bodega": bodega
        }).eq("id", fila["id"]).execute()
    else:
        supabase.table("inventario").insert({
            "producto": nombre,
            "stock": cantidad,
            "bodega": bodega,
            "piezas_fardo": 0
        }).execute()

    guardar_historial(now, nombre, "entrada", cantidad, bodega)

def actualizar_stock(index, cantidad, tipo):
    df = cargar_inventario()
    row = df.loc[index]
    now = datetime.utcnow() - timedelta(hours=6)

    if tipo == "agregar":
        nuevo_stock = int(row["stock"]) + cantidad
        movimiento = "entrada"
    else:
        if int(row["stock"]) < cantidad:
            return
        nuevo_stock = int(row["stock"]) - cantidad
        movimiento = "salida"

    supabase.table("inventario").update({
        "stock": nuevo_stock
    }).eq("id", row["id"]).execute()

    guardar_historial(now, row["producto"], movimiento, cantidad, row["bodega"])

def eliminar_producto(index):
    df = cargar_inventario()
    id_producto = df.loc[index]["id"]
    supabase.table("inventario").delete().eq("id", id_producto).execute()

# 🔐 LOGIN

def encriptar(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

USUARIOS = {
    "admin": encriptar("1234")
}

def validar_usuario(user, pwd):
    return user in USUARIOS and USUARIOS[user] == encriptar(pwd)
