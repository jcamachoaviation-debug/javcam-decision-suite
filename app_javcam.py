import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile

# 1. CONFIGURACIÓN DE IDENTIDAD Y SEGURIDAD DE SERVIDORES
st.set_page_config(page_title="JAVCAM Decision Suite v4.0", page_icon="🛡️", layout="wide")

if "credentials" in st.secrets:
    ADMIN_USER = st.secrets["credentials"]["admin_user"]
    ADMIN_PASSWORD = st.secrets["credentials"]["admin_password"]
    TOKEN_VALIDO = st.secrets["credentials"]["licencia_valida"]
else:
    # Respaldos estáticos de emergencia
    ADMIN_USER = "comandante@javcam.com"
    ADMIN_PASSWORD = "PremiumPassword2026"
    TOKEN_VALIDO = "JAVCAM-ENTERPRISE-2026-X9"

# Gestión del estado de la autenticación
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# INTERFAZ DE LOGIN DE ALTA SEGURIDAD
if not st.session_state.autenticado:
    st.title("🛡️ Control de Acceso - JAVCAM Decision Suite")
    st.subheader("Infraestructura de Gestión de Activos Físicos v4.0")
    
    usuario = st.text_input("Usuario Corporativo:")
    contrasena = st.text_input("Contraseña de Acceso:", type="password")
    
    if st.button("Autenticar Sistema", use_container_width=True):
        if usuario == ADMIN_USER and contrasena == ADMIN_PASSWORD:
            st.session_state.autenticado = True
            st.success("Autenticación exitosa. Cargando entorno de operaciones...")
            st.rerun()
        else:
            st.error("Acceso Denegado. Credenciales inválidas o no autorizadas.")
    st.stop()

# =========================================================================
# ENTORNO OPERATIVO DESBLOQUEADO POST-LOGIN
# =========================================================================

# 2. CONTROL DE LICENCIAMIENTO EN LA BARRA LATERAL
st.sidebar.title("🛸 Panel de Control Operativo")
st.sidebar.write(f"**Operario:** {ADMIN_USER}")

# Caja de validación del Token Comercial
token_ingresado = st.sidebar.text_input("🔑 Token de Licencia Activa:", value="", type="password")

# Evaluación del nivel de acceso y establecimiento de límites
if token_ingresado == TOKEN_VALIDO:
    ES_ENTERPRISE = True
    st.sidebar.success("👑 LICENCIA ENTERPRISE: ACTIVA")
    max_alternativas = 6
    max_criterios = 6
else:
    ES_ENTERPRISE = False
    st.sidebar.warning("⚠️ MODO LIMITADO (FREE)")
    st.sidebar.info("Para evaluar más de 3 alternativas, habilitar gráficos de estrés y desbloquear la descarga del reporte PDF certificado, ingrese su Token Corporativo.")
    max_alternativas = 3
    max_criterios = 3

st.sidebar.markdown("---")

# 3. CONFIGURACIÓN DEL MODELO MATEMÁTICO (DINÁMICO)
st.title("📈 JAVCAM Decision Suite - Motor Analítico")
st.write("Bienvenido al entorno de evaluación multicriterio para la toma de decisiones estratégicas.")

st.subheader("⚙️ Parámetros del Modelo de Decisión")
col_cfg1, col_cfg2 = st.columns(2)

with col_cfg1:
    num_alternativas = st.slider("Número de Alternativas a Evaluar:", min_value=2, max_value=max_alternativas, value=2)

with col_cfg2:
    num_criterios = st.slider("Número de Criterios de Evaluación:", min_value=2, max_value=max_criterios, value=2)

st.markdown("---")

# 4. CALIFICACIÓN Y PONDERACIÓN DE CRITERIOS (MATRIZ PESOS)
st.subheader("🎯 Calificación y Ponderación de Criterios")
st.write("Asigne la importancia/peso relativo a cada criterio de evaluación (La suma recomendada es 1.0).")

pesos = []
cols_criterios = st.columns(int(num_criterios))

for i in range(int(num_criterios)):
    with cols_criterios[i]:
        nombre_crit = st.text_input(f"Nombre Criterio {i+1}:", f"Criterio C{i+1}", key=f"name_{i}")
        peso_crit = st.slider(f"Peso de {nombre_crit}:", min_value=0.0, max_value=1.0, value=1.0/num_criterios, step=0.05, key=f"peso_{i}")
        pesos.append((nombre_crit, peso_crit))

total_peso = sum([p[1] for p in pesos])
st.info(f"**Suma consolidada de pesos:** {total_peso:.2f} / 1.00")

st.markdown("---")

# 5. MATRIZ DE RENDIMIENTO - MATRIZ DE CALIFICACIÓN DEL OPERADOR
st.subheader("📊 Matriz de Rendimiento de Activos")
st.write("Introduzca los puntajes de rendimiento esperados para cada alternativa (Escala 1 - 100):")

nombres_alternativas = [f"Alternativa {i+1}" for i in range(int(num_alternativas))]
nombres_criterios = [p[0] for p in pesos]

# Construcción de la matriz dinámica editable
datos_iniciales = {n_crit: [80.0] * int(num_alternativas) for n_crit in nombres_criterios}
df_matriz = pd.DataFrame(datos_iniciales, index=nombres_alternativas)
matriz_evaluada = st.data_editor(df_matriz, use_container_width=True)

st.markdown("---")

# 6. PROCESAMIENTO MATRICIAL Y RANKING ÓPTIMO
st.subheader("🏆 Resultados del Análisis y Certificación")

pesos_vector = np.array([p[1] for p in pesos])
matriz_np = matriz_evaluada.to_numpy()

# Cálculo del Score Final por Ponderación Lineal
scores_totales = np.dot(matriz_np, pesos_vector)
df_resultados = pd.DataFrame({"Puntaje de Optimización": scores_totales}, index=nombres_alternativas)
df_resultados = df_resultados.sort_values(by="Puntaje de Optimización", ascending=False)

col_res1, col_res2 = st.columns([1, 2])

with col_res1:
    st.write("**Ranking Estratégico:**")
    st.dataframe(df_resultados, use_container_width=True)
    st.success(f"🥇 **Opción Recomendada:** {df_resultados.index[0]}")

with col_res2:
    # Renderización del Gráfico Radial Dinámico (Modo Operacional Estándar)
    fig, ax = plt.subplots(figsize=(6, 3.5))
    df_resultados.plot(kind='barh', color='#1f77b4', ax=ax, legend=False)
    plt.title("Rendimiento Consolidado de Alternativas")
    plt.xlabel("Score")
    st.pyplot(fig)

# 7. SECCIÓN CORPORATIVA DE ALTA MONETIZACIÓN (SOLO ENTERPRISE CON TOKEN)
if ES_ENTERPRISE:
    st.markdown("---")
    st.write("### 👑 Módulos de Certificación Avanzada e Informes")
    
    # Gráfica Empresarial Adicional
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    ax2.pie(df_resultados["Puntaje de Optimización"], labels=df_resultados.index, autopct='%1.1f%%', startangle=90, colors=['#2ca02c', '#ff7f0e', '#d62728', '#9467bd'])
    plt.title("Distribución de Idoneidad del Activo")
    st.pyplot(fig2)
    
    # Sistema de descarga de PDF institucional
    if st.button("📥 Descargar Reporte de Auditoría Matemática Certificada (PDF)", use_container_width=True):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", style='B', size=16)
        pdf.cell(200, 10, txt="JAVCAM DECISION SUITE - REPORTE AUDITADO v4.0", ln=1, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Certificación de Licencia Corporativa Enterprise.", ln=1, align="L")
        pdf.cell(200, 10, txt=f"Activo Recomendado por el Sistema: {df_resultados.index[0]}", ln=1, align="L")
        pdf.cell(200, 10, txt=f"Eficiencia Calculada: {df_resultados.iloc[0,0]:.2f} Puntos.", ln=1, align="L")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            with open(tmp.name, "rb") as f:
                st.download_button("Click aquí para descargar PDF Oficial", data=f, file_name="Reporte_Certificado_JAVCAM.pdf", mime="application/pdf")
else:
    st.markdown("---")
    st.write("### 🔒 Funciones de Certificación Bloqueadas")
    st.info("La emisión de Reportes de Auditoría Matemática en PDF Ejecutivo y los gráficos corporativos de distribución se desbloquearán inmediatamente al ingresar un Token Enterprise válido en la barra lateral.")
