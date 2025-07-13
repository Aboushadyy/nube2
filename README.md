# 📦 Inventario Amazon IB

Aplicación web de gestión de inventario desarrollada en Streamlit y conectada a Supabase.

## 🔐 Características

- Login seguro con contraseña cifrada (SHA-256)
- Agregado de productos por lotes (p. ej., `Producto1: 100`)
- Control de stock (sumar/quitar unidades)
- Eliminación de productos
- Registro automático en historial
- Descarga de inventario e historial en CSV
- Diseño compatible con PC y teléfono

## 🚀 Despliegue

Este proyecto se despliega en [Render](https://render.com) con las siguientes variables de entorno:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

## 🧾 Requisitos

- Python 3.10
- Streamlit
- Pandas
- Supabase

Instala dependencias:

```bash
pip install -r requirements.txt
