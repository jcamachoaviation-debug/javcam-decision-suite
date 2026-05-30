import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import itertools

# 1. CONFIGURACIÓN DE IDENTIDAD Y SEGURIDAD DE SERVIDORES
st.set_page_config(page_title="JAVCAM Decision Suite v5.5", page_icon="🛡️", layout="wide")

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
    st.subheader("Infraestructura de Gestión de Activos Físicos v5.5")
    
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
    limite_max = 10
else:
    ES_ENTERPRISE = False
    st.sidebar.warning("⚠️ MODO LIMITADO (FREE)")
    st.sidebar.info("En el modo Free está limitado a 3 alternativas y 3 criterios. Ingrese su Token Enterprise para desbloquear el escalado hasta 10.")
    limite_max = 3

st.sidebar.markdown("---")

# 3. CONFIGURACIÓN ESCALAR DEL MODELO
st.title("📈 JAVCAM Decision Suite - Motor Analítico Escalable")
st.write("Optimización multicriterio avanzada con direccionalidad de variables y análisis prospectivo.")

st.subheader("⚙️ Dimensión del Modelo de Decisión")
col_dim1, col_dim2 = st.columns(2)

with col_dim1:
    num_alternativas = st.slider("Cantidad de Alternativas a Evaluar:", min_value=2, max_value=limite_max, value=min(3, limite_max))

with col_dim2:
    num_criterios = st.slider("Cantidad de Criterios Tecnológicos:", min_value=2, max_value=limite_max, value=min(3, limite_max))

st.markdown("---")

# 4. DEFINICIÓN Y DIRECCIÓN DE CRITERIOS
st.subheader("🎯 1. Configuración y Direccionalidad de Criterios")
st.write("Defina el nombre de los criterios y su impacto en la toma de decisiones.")

criterios_lista = []
direcciones_lista = []

cols_crit = st.columns(int(num_criterios))
for i in range(int(num_criterios)):
    with cols_crit[i]:
        nombre = st.text_input(f"Nombre C{i+1}:", f"Criterio C{i+1}", key=f"nc_{i}")
        direccion = st.selectbox(f"Optimización C{i+1}:", ["Maximizar (+ es mejor)", "Minimizar (- es mejor)"], key=f"dc_{i}")
        criterios_lista.append(nombre)
        # Guardamos True si es maximizar, False si es minimizar
        direcciones_lista.append(True if "Maximizar" in direccion else False)

st.markdown("---")

# 5. PONDERACIÓN DE SAATY AUTOMATIZADA Y DINÁMICA
st.subheader("📐 2. Matriz de Ponderación (Escala de Saaty)")
st.write("Establezca las relaciones de importancia pareada entre sus criterios.")

# Generar combinaciones únicas de comparación pareada dinámicamente
combinaciones = list(itertools.combinations(range(int(num_criterios)), 2))

A = np.ones((int(num_criterios), int(num_criterios)))

if len(combinaciones) > 0:
    st.write("Compare la importancia del primer criterio frente al segundo:")
    # Organizar los sliders en columnas para no saturar la pantalla verticalmente
    cols_saaty = st.columns(min(3, len(combinaciones)))
    
    for idx, (c_i, c_j) in enumerate(combinaciones):
        col_actual = cols_saaty[idx % min(3, len(combinaciones))]
        with col_actual:
            valor_slider = st.slider(
                f"**{criterios_lista[c_i]}** vs **{criterios_lista[c_j]}**:",
                min_value=0.11, max_value=9.0, value=1.0, step=0.1,
                key=f"saaty_{c_i}_{c_j}"
            )
            A[c_i, c_j] = valor_slider
            A[c_j, c_i] = 1.0 / valor_slider

# Algoritmo de normalización de Saaty para obtener pesos
suma_columnas = A.sum(axis=0)
A_normalizada = A / suma_columnas
pesos_saaty = A_normalizada.mean(axis=1)

# Cálculo del Índice de Consistencia Básica
λ_max = np.sum(suma_columnas * pesos_saaty)
CI = (λ_max - num_criterios) / (num_criterios - 1) if num_criterios > 1 else 0
# Tabla de Índices Aleatorios (RI) hasta n=10
RI_dict = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
RI = RI_dict.get(int(num_criterios), 1.49)
CR = CI / RI if RI > 0 else 0

st.write("**Pesos de Criterios Consolidados:**")
df_pesos = pd.DataFrame({"Criterio": criterios_lista, "Dirección": ["Max (+)" if d else "Min (-)" for d in direcciones_lista], "Peso Asignado": pesos_saaty})
st.dataframe(df_pesos.set_index("Criterio"), use_container_width=True)

if CR < 0.10:
    st.success(f"✅ Consistencia del Modelo Validada. CR: {CR:.4f}")
else:
    st.warning(f"⚠️ Inconsistencia Detectada: CR = {CR:.4f}. Se recomienda calibrar los pesos pareados.")

st.markdown("---")

# 6. MATRIZ DE RENDIMIENTO Y NORMALIZACIÓN SEGÚN DIRECCIÓN
st.subheader("📊 3. Entrada de Datos y Normalización Adaptativa")
st.write("Ingrese los valores brutos de rendimiento para las alternativas de la flota:")

nombres_alternativas = [f"Alternativa {i+1}" for i in range(int(num_alternativas))]
datos_iniciales = {crit: [80.0] * int(num_alternativas) for crit in criterios_lista}
df_bruto = pd.DataFrame(datos_iniciales, index=nombres_alternativas)

# Tabla interactiva editable
matriz_bruta = st.data_editor(df_bruto, use_container_width=True)

# Motor de Normalización Adaptativo Max-Min basado en direcciones_lista
matriz_np = matriz_bruta.to_numpy()
matriz_normalizada = np.zeros_like(matriz_np)

for j in range(int(num_criterios)):
    max_val = matriz_np[:, j].max()
    min_val = matriz_np[:, j].min()
    
    if max_val == min_val:
        matriz_normalizada[:, j] = 1.0
    else:
        if direcciones_lista[j]:  # Si es Maximizar (+ es mejor)
            matriz_normalizada[:, j] = (matriz_np[:, j] - min_val) / (max_val - min_val)
        else:  # Si es Minimizar (- es mejor)
            matriz_normalizada[:, j] = (max_val - matriz_np[:, j]) / (max_val - min_val)

# Cálculo de Puntuación Base
scores_base = np.dot(matriz_normalizada, pesos_saaty)
df_ranking_base = pd.DataFrame({"Score Global": scores_base}, index=nombres_alternativas).sort_values(by="Score Global", ascending=False)

st.write("**Resultado de Selección (Escenario Base):**")
col_r1, col_r2 = st.columns([1, 2])
with col_r1:
    st.dataframe(df_ranking_base, use_container_width=True)
    st.success(f"🥇 **Opción Recomendada:** {df_ranking_base.index[0]}")
with col_r2:
    fig, ax = plt.subplots(figsize=(6, 3))
    df_ranking_base.sort_values(by="Score Global", ascending=True).plot(kind="barh", color="#1a73e8", ax=ax, legend=False)
    plt.title("Rendimiento Óptimo de Activos")
    plt.xlabel("Score")
    st.pyplot(fig)

st.markdown("---")

# 7. ANÁLISIS PROSPECTIVO AVANZADO BAJO ESCENARIOS (BLOQUEADO COMERCIAL)
st.subheader("🔮 4. Análisis Prospectivo de Sensibilidad")

if not ES_ENTERPRISE:
    st.info("🔒 **Módulo Prospectivo Bloqueado:** Introduzca su Token Enterprise en la barra lateral para simular resiliencia ante variaciones del entorno (Pesimista vs Optimista) con matrices completas.")
else:
    st.write("Evaluación de robustez modificando dinámicamente la concentración de pesos ante contingencias operativas o financieras.")
    
    # Escenario Pesimista: Fuerza los pesos drásticamente hacia los criterios de Minimización (Costos/Riesgos)
    # Escenario Optimista: Fuerza los pesos hacia los criterios de Maximización (Rendimiento/Beneficios)
    pesos_pesimista = np.zeros(int(num_criterios))
    pesos_optimista = np.zeros(int(num_criterios))
    
    count_min = direcciones_lista.count(False)
    count_max = direcciones_lista.count(True)
    
    for j in range(int(num_criterios)):
        if direcciones_lista[j]:  # Criterio Max
            pesos_pesimista[j] = 0.10 / count_max if count_max > 0 else 1.0/num_criterios
            pesos_optimista[j] = 0.90 / count_max if count_max > 0 else 1.0/num_criterios
        else:  # Criterio Min
            pesos_pesimista[j] = 0.90 / count_min if count_min > 0 else 1.0/num_criterios
            pesos_optimista[j] = 0.10 / count_min if count_min > 0 else 1.0/num_criterios
            
    # Ajuste de suma 1.0 en casos extremos
    pesos_pesimista /= pesos_pesimista.sum()
    pesos_optimista /= pesos_optimista.sum()
    
    scores_pesimista = np.dot(matriz_normalizada, pesos_pesimista)
    scores_optimista = np.dot(matriz_normalizada, pesos_optimista)
    
    df_prospectiva = pd.DataFrame({
        "Escenario Enfoque Riesgo/Costo (Min)": scores_pesimista,
        "Escenario Esperado (Base Saaty)": scores_base,
        "Escenario Enfoque Operativo (Max)": scores_optimista
    }, index=nombres_alternativas)
    
    st.write("**Matriz de Escenarios Prospectivos Computados:**")
    st.dataframe(df_prospectiva, use_container_width=True)
    
    # Gráfico de tendencias lineales
    fig_scen, ax_scen = plt.subplots(figsize=(10, 4))
    df_prospectiva.T.plot(kind="line", marker="o", linewidth=2.5, ax=ax_scen)
    plt.title("Línea de Tendencia: Resiliencia de Activos ante Cambio de Escenarios")
    plt.ylabel("Score")
    plt.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig_scen)
    
    # Solución definitiva usando .iloc[0] para evitar KeyError
    ganador_pesimista = df_prospectiva.idxmax().iloc[0]
    st.success(f"💡 **Análisis de Robustez:** Ante un escenario adverso enfocado en control riguroso de variables críticas, el activo más resiliente es **{ganador_pesimista}**.")

    # 8. SISTEMA DE EMISIÓN DE REPORTES
    st.markdown("---")
    st.subheader("📥 Certificación Final Corporativa")
    if st.button("📥 Generar Reporte de Ingeniería Escalar Completo (PDF)", use_container_width=True):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", style='B', size=16)
        pdf.cell(200, 10, txt="JAVCAM DECISION SUITE v5.5 - INFORME INGENIERÍA", ln=1, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Modelo Multicriterio Escalable Computado de Forma Exitosa.", ln=1, align="L")
        pdf.cell(200, 10, txt=f"Cantidad de Activos Evaluados: {num_alternativas} | Criterios: {num_criterios}", ln=1, align="L")
        pdf.cell(200, 10, txt=f"Selección de Máxima Eficiencia: {df_ranking_base.index[0]}", ln=1, align="L")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            with open(tmp.name, "rb") as f:
                st.download_button("Descargar Reporte PDF de Flota", data=f, file_name="Reporte_Escalar_JAVCAM.pdf", mime="application/pdf")
