import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile

# 1. CONFIGURACIÓN DE IDENTIDAD Y SEGURIDAD DE SERVIDORES
st.set_page_config(page_title="JAVCAM Decision Suite v5.0", page_icon="🛡️", layout="wide")

if "credentials" in st.secrets:
    ADMIN_USER = st.secrets["credentials"]["admin_user"]
    ADMIN_PASSWORD = st.secrets["credentials"]["admin_password"]
    TOKEN_VALIDO = st.secrets["credentials"]["licencia_valida"]
else:
    ADMIN_USER = "comandante@javcam.com"
    ADMIN_PASSWORD = "PremiumPassword2026"
    TOKEN_VALIDO = "JAVCAM-ENTERPRISE-2026-X9"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# INTERFAZ DE LOGIN OBLIGATORIA
if not st.session_state.autenticado:
    st.title("🛡️ Control de Acceso - JAVCAM Decision Suite")
    st.subheader("Infraestructura de Gestión de Activos Físicos v5.0")
    
    usuario = st.text_input("Usuario Corporativo:")
    contrasena = st.text_input("Contraseña de Acceso:", type="password")
    
    if st.button("Autenticar Sistema", use_container_width=True):
        if usuario == ADMIN_USER and contrasena == ADMIN_PASSWORD:
            st.session_state.autenticado = True
            st.success("Autenticación exitosa. Cargando entorno de operaciones...")
            st.rerun()
        else:
            st.error("Acceso Denegado. Credenciales inválidas.")
    st.stop()

# =========================================================================
# ENTORNO OPERATIVO DESBLOQUEADO
# =========================================================================

# 2. CONTROL DE LICENCIAMIENTO EN LA BARRA LATERAL
st.sidebar.title("🛸 Panel de Control Operativo")
st.sidebar.write(f"**Operario:** {ADMIN_USER}")

token_ingresado = st.sidebar.text_input("🔑 Token de Licencia Activa:", value="", type="password")

if token_ingresado == TOKEN_VALIDO:
    ES_ENTERPRISE = True
    st.sidebar.success("👑 LICENCIA ENTERPRISE: ACTIVA")
    max_alternativas = 6
else:
    ES_ENTERPRISE = False
    st.sidebar.warning("⚠️ MODO LIMITADO (FREE)")
    st.sidebar.info("Para evaluar más de 3 alternativas, habilitar el Análisis Prospectivo de Escenarios y descargar reportes PDF, ingrese su Token.")
    max_alternativas = 3

st.sidebar.markdown("---")

# 3. CONFIGURACIÓN DEL MODELO MATEMÁTICO
st.title("📈 JAVCAM Decision Suite - Motor Analítico Avanzado")
st.write("Entorno de optimización multicriterio con matrices de Saaty, normalización y análisis prospectivo.")

st.subheader("⚙️ Parámetros de la Flota / Activos")
num_alternativas = st.slider("Número de Alternativas (Proyectos/Activos):", min_value=2, max_value=max_alternativas, value=3)

# Definimos 3 criterios estáticos de ingeniería para estructurar Saaty con precisión
criterios = ["Disponibilidad Técnica (C1)", "Costos de Ciclo de Vida LCC (C2)", "Confiabilidad MTBF (C3)"]
n_criterios = len(criterios)

st.markdown("---")

# 4. MÉTODO DE SAATY (PROCESO DE JERARQUÍA ANALÍTICA - AHP)
st.subheader("🎯 1. Ponderación de Criterios según la Escala de Saaty")
st.write("Compare la importancia relativa de los criterios. (1: Igual, 3: Moderado, 5: Fuerte, 7: Muy fuerte, 9: Extremo).")

# Matriz de comparación pareada interactiva
st.write("**Establezca los valores de la mitad superior de la matriz:**")
col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    c1_vs_c2 = st.slider("Importancia de Disponibilidad (C1) frente a Costos (C2):", 0.11, 9.0, 1.0, step=0.1)
with col_s2:
    c1_vs_c3 = st.slider("Importancia de Disponibilidad (C1) frente a Confiabilidad (C3):", 0.11, 9.0, 1.0, step=0.1)
with col_s3:
    c2_vs_c3 = st.slider("Importancia de Costos (C2) frente a Confiabilidad (C3):", 0.11, 9.0, 1.0, step=0.1)

# Construcción matemática de la matriz de Saaty
A = np.ones((n_criterios, n_criterios))
A[0, 1] = c1_vs_c2
A[1, 0] = 1.0 / c1_vs_c2
A[0, 2] = c1_vs_c3
A[2, 0] = 1.0 / c1_vs_c3
A[1, 2] = c2_vs_c3
A[2, 1] = 1.0 / c2_vs_c3

# Normalización de Saaty para obtener los pesos (Vector propio aproximado)
suma_columnas = A.sum(axis=0)
A_normalizada = A / suma_columnas
pesos_saaty = A_normalizada.mean(axis=1)

# Cálculo del Índice de Consistencia (CR)
λ_max = np.sum(suma_columnas * pesos_saaty)
CI = (λ_max - n_criterios) / (n_criterios - 1)
RI = 0.58  # Valor de tabla para n=3
CR = CI / RI if RI > 0 else 0

# Despliegue de resultados de Saaty
st.write("**Pesos calculados por el Algoritmo de Saaty:**")
df_pesos = pd.DataFrame({"Criterio": criterios, "Ponderación (Peso)": pesos_saaty})
st.dataframe(df_pesos.set_index("Criterio"), use_container_width=True)

if CR < 0.10:
    st.success(f"✅ Matriz Consistente. Razón de Consistencia (CR): {CR:.4f} < 0.10")
else:
    st.warning(f"⚠️ Alerta de Consistencia: CR = {CR:.4f}. Considere ajustar las comparaciones para mayor rigor.")

st.markdown("---")

# 5. NORMALIZACIÓN Y MATRIZ DE RENDIMIENTO
st.subheader("📊 2. Matriz de Calificación del Operador y Normalización")
st.write("Ingrese los valores brutos de rendimiento para cada alternativa (Escala 1 a 100):")

nombres_alternativas = [f"Alternativa {i+1}" for i in range(num_alternativas)]
datos_iniciales = {crit: [80.0] * num_alternativas for crit in criterios}
df_bruto = pd.DataFrame(datos_iniciales, index=nombres_alternativas)

# Tabla editable
matriz_bruta = st.data_editor(df_bruto, use_container_width=True)

# Proceso de Normalización Lineal (Max-Min)
matriz_np = matriz_bruta.to_numpy()
# Suponemos C1 y C3 Maxmizar (Beneficio), C2 Minimizar (Costo de ciclo de vida)
matriz_normalizada = np.zeros_like(matriz_np)

for j in range(n_criterios):
    max_val = matriz_np[:, j].max()
    min_val = matriz_np[:, j].min()
    if max_val == min_val:
        matriz_normalizada[:, j] = 1.0
    else:
        if j == 1: # C2 es Costo (Minimizar)
            matriz_normalizada[:, j] = (max_val - matriz_np[:, j]) / (max_val - min_val)
        else: # Beneficio (Maximizar)
            matriz_normalizada[:, j] = (matriz_np[:, j] - min_val) / (max_val - min_val)

df_norm = pd.DataFrame(matriz_normalizada, columns=criterios, index=nombres_alternativas)

# Cálculo del Score Consolidado Escenario Base
scores_base = np.dot(matriz_normalizada, pesos_saaty)
df_ranking_base = pd.DataFrame({"Score Optimizado (Base)": scores_base}, index=nombres_alternativas).sort_values(by="Score Optimizado (Base)", ascending=False)

st.write("**Ranking Consolidado (Escenario Base):**")
col_r1, col_r2 = st.columns([1, 2])
with col_r1:
    st.dataframe(df_ranking_base, use_container_width=True)
    st.success(f"🥇 **Selección Óptima:** {df_ranking_base.index[0]}")
with col_r2:
    fig, ax = plt.subplots(figsize=(6, 3))
    df_ranking_base.plot(kind="barh", color="#20b2aa", ax=ax, legend=False)
    plt.title("Rendimiento del Activo - Escenario Base")
    st.pyplot(fig)

st.markdown("---")

# 6. ANÁLISIS PROSPECTIVO BAJO ESCENARIOS (BLOQUEO COMERCIAL INTELIGENTE)
st.subheader("🔮 3. Análisis Prospectivo y de Escenarios")

if not ES_ENTERPRISE:
    st.info("🔒 **Módulo Prospectivo Bloqueado:** Ingrese su Token Enterprise en la barra lateral para simular la sensibilidad de las alternativas bajo escenarios de estrés (Pesimista, Esperado y Optimista).")
else:
    st.write("Este módulo evalúa la resiliencia de las alternativas modificando la prioridad de los criterios frente a variaciones del entorno de negocios.")
    
    # Definición matemática de escenarios mediante alteración de pesos de Saaty
    # Escenario Pesimista: El peso se vuelca drásticamente al Costo (C2)
    pesos_pesimista = np.array([0.15, 0.70, 0.15]) 
    # Escenario Optimista: El peso se enfoca en Máxima Disponibilidad y Confiabilidad (C1 y C3)
    pesos_optimista = np.array([0.45, 0.10, 0.45])
    
    # Cálculo de scores cruzados
    scores_pesimista = np.dot(matriz_normalizada, pesos_pesimista)
    scores_optimista = np.dot(matriz_normalizada, pesos_optimista)
    
    df_prospectiva = pd.DataFrame({
        "Escenario Pesimista (Enfoque Costos)": scores_pesimista,
        "Escenario Esperado (Base Saaty)": scores_base,
        "Escenario Optimista (Enfoque Operaciones)": scores_optimista
    }, index=nombres_alternativas)
    
    st.write("**Matriz de Rendimiento Prospectivo Extrapolado:**")
    st.dataframe(df_prospectiva, use_container_width=True)
    
    # Gráfico de Líneas / Tendencia de Escenarios
    fig_scen, ax_scen = plt.subplots(figsize=(10, 4))
    df_prospectiva.T.plot(kind="line", marker="o", linewidth=2.5, ax=ax_scen)
    plt.title("Análisis de Sensibilidad y Resiliencia de Alternativas por Escenario")
    plt.ylabel("Score Global")
    plt.xlabel("Escenarios Prospectivos")
    plt.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig_scen)
    
    # Ganador estratégico de resiliencia
    ganador_pesimista = df_prospectiva.idxmax().iloc[0]
    st.success(f"💡 **Análisis de Robustez:** En el peor escenario macroeconómico (Pesimista), la opción más resiliente es **{ganador_pesimista}**.")
    # 7. EXPORTACIÓN DEL REPORTE INTEGRAL v5.0
    st.markdown("---")
    st.subheader("📥 Certificación Final")
    if st.button("📥 Generar Reporte de Ingeniería y Prospectiva Completo (PDF)", use_container_width=True):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", style='B', size=16)
        pdf.cell(200, 10, txt="JAVCAM DECISION SUITE v5.0 - INFORME MATEMÁTICO", ln=1, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Análisis de Confiabilidad y Selección de Activos Físicos.", ln=1, align="L")
        pdf.cell(200, 10, txt=f"Razón de Consistencia Saaty: {CR:.4f}", ln=1, align="L")
        pdf.cell(200, 10, txt=f"Ganador Escenario Base: {df_ranking_base.index[0]}", ln=1, align="L")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            with open(tmp.name, "rb") as f:
                st.download_button("Descargar PDF Institucional", data=f, file_name="Reporte_Ingenieria_JAVCAM_v5.pdf", mime="application/pdf")
