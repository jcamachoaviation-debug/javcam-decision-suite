import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import itertools
import os

# 1. CONFIGURACIÓN DE IDENTIDAD Y SEGURIDAD
st.set_page_config(page_title="JAVCAM Decision Suite v6.0", page_icon="🛡️", layout="wide")

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

# LOGIN OBLIGATORIO
if not st.session_state.autenticado:
    st.title("🛡️ Control de Acceso - JAVCAM Decision Suite")
    st.subheader("Infraestructura de Gestión de Activos Físicos v6.0")
    
    usuario = st.text_input("Usuario Corporativo:")
    contrasena = st.text_input("Contraseña de Acceso:", type="password")
    
    if st.button("Autenticar Sistema", use_container_width=True):
        if usuario == ADMIN_USER and contrasena == ADMIN_PASSWORD:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Acceso Denegado.")
    st.stop()

# 2. CONTROL DE LICENCIA
st.sidebar.title("🛸 Panel Operativo v6.0")
token_ingresado = st.sidebar.text_input("🔑 Token de Licencia Activa:", value="", type="password")

if token_ingresado == TOKEN_VALIDO:
    ES_ENTERPRISE = True
    st.sidebar.success("👑 LICENCIA ENTERPRISE: ACTIVA")
    limite_max = 10
else:
    ES_ENTERPRISE = False
    st.sidebar.warning("⚠️ MODO LIMITADO (FREE)")
    limite_max = 3

# 3. CONFIGURACIÓN DEL MODELO
st.title("📈 JAVCAM Decision Suite - Inteligencia Visual")
col_dim1, col_dim2 = st.columns(2)
with col_dim1:
    num_alternativas = st.slider("Alternativas:", 2, limite_max, 3)
with col_dim2:
    num_criterios = st.slider("Criterios:", 2, limite_max, 3)

st.markdown("---")

# 4. CRITERIOS Y DIRECCIÓN
st.subheader("🎯 1. Configuración de Criterios")
criterios_lista = []
direcciones_lista = []
cols_crit = st.columns(int(num_criterios))
for i in range(int(num_criterios)):
    with cols_crit[i]:
        nombre = st.text_input(f"C{i+1}:", f"Criterio {i+1}", key=f"nc_{i}")
        direccion = st.selectbox(f"Optimización:", ["Max (+)", "Min (-)"], key=f"dc_{i}")
        criterios_lista.append(nombre)
        direcciones_lista.append(True if "Max" in direccion else False)

# 5. SAATY
st.subheader("📐 2. Ponderación Científica (Saaty)")
combinaciones = list(itertools.combinations(range(int(num_criterios)), 2))
A = np.ones((int(num_criterios), int(num_criterios)))
if len(combinaciones) > 0:
    cols_saaty = st.columns(min(3, len(combinaciones)))
    for idx, (c_i, c_j) in enumerate(combinaciones):
        with cols_saaty[idx % min(3, len(combinaciones))]:
            v = st.slider(f"{criterios_lista[c_i]} vs {criterios_lista[c_j]}", 0.1, 9.0, 1.0, key=f"s_{i}_{j}")
            A[c_i, c_j] = v
            A[c_j, c_i] = 1.0 / v

pesos_saaty = (A / A.sum(axis=0)).mean(axis=1)

# 6. DATOS Y NORMALIZACIÓN
st.subheader("📊 3. Matriz de Rendimiento")
n_alt = [f"Alt {i+1}" for i in range(int(num_alternativas))]
df_bruto = pd.DataFrame({c: [80.0]*int(num_alternativas) for c in criterios_lista}, index=n_alt)
matriz_bruta = st.data_editor(df_bruto, use_container_width=True)

matriz_np = matriz_bruta.to_numpy()
matriz_norm = np.zeros_like(matriz_np)
for j in range(int(num_criterios)):
    mx, mn = matriz_np[:,j].max(), matriz_np[:,j].min()
    if mx == mn: matriz_norm[:,j] = 1.0
    else:
        if direcciones_lista[j]: matriz_norm[:,j] = (matriz_np[:,j]-mn)/(mx-mn)
        else: matriz_norm[:,j] = (mx-matriz_np[:,j])/(mx-mn)

scores = np.dot(matriz_norm, pesos_saaty)
df_res = pd.DataFrame({"Score": scores}, index=n_alt).sort_values("Score", ascending=False)

st.markdown("---")

# 7. VISUALIZACIÓN RADIAL (DIAGRAMA DE ARAÑA)
st.subheader("🕸️ 4. Comparativa Radial de Alternativas")
categories = criterios_lista
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

fig_radar, ax_radar = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
for i, alt_name in enumerate(n_alt):
    values = matriz_norm[i].tolist()
    values += values[:1]
    ax_radar.plot(angles, values, linewidth=2, linestyle='solid', label=alt_name)
    ax_radar.fill(angles, values, alpha=0.1)

ax_radar.set_theta_offset(np.pi / 2)
ax_radar.set_theta_direction(-1)
plt.xticks(angles[:-1], categories)
plt.title("Perfil de Desempeño por Criterio", size=15, y=1.1)
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
st.pyplot(fig_radar)

st.markdown("---")

# 8. PROSPECTIVA (SÓLO ENTERPRISE)
st.subheader("🔮 5. Análisis Prospectivo")
fig_scen, ax_scen = plt.subplots(figsize=(10, 4)) # Pre-creamos para el PDF
if not ES_ENTERPRISE:
    st.info("🔒 Módulo Bloqueado. Ingrese Token.")
else:
    # Cálculo de Escenarios
    p_pes = np.array([0.9 if not d else 0.1 for d in direcciones_lista])
    p_pes /= p_pes.sum()
    p_opt = np.array([0.9 if d else 0.1 for d in direcciones_lista])
    p_opt /= p_opt.sum()
    
    df_pros = pd.DataFrame({
        "Pesimista": np.dot(matriz_norm, p_pes),
        "Esperado": scores,
        "Optimista": np.dot(matriz_norm, p_opt)
    }, index=n_alt)
    
    st.dataframe(df_pros, use_container_width=True)
    df_pros.T.plot(kind="line", marker="o", ax=ax_scen)
    plt.title("Resiliencia por Escenario")
    st.pyplot(fig_scen)

# 9. REPORTE PDF MAESTRO
st.markdown("---")
if st.button("📥 Generar Reporte Integral Certificado (PDF)", use_container_width=True):
    if not ES_ENTERPRISE:
        st.error("Función exclusiva de la Licencia Enterprise.")
    else:
        with st.spinner("Compilando gráficos y análisis técnico..."):
            pdf = FPDF()
            pdf.add_page()
            
            # Encabezado
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, "JAVCAM DECISION SUITE v6.0 - AUDITORIA", ln=True, align='C')
            pdf.set_font("Arial", '', 12)
            pdf.cell(200, 10, f"Operario: {ADMIN_USER} | Certificación Enterprise", ln=True, align='C')
            pdf.ln(10)
            
            # Tabla de Resultados
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, "1. Ranking de Seleccion Optima", ln=True)
            pdf.set_font("Arial", '', 11)
            for i, row in df_res.iterrows():
                pdf.cell(200, 8, f"{i}: {row['Score']:.4f}", ln=True)
            pdf.ln(5)
            
            # Insertar Gráfico Radial
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_radar:
                fig_radar.savefig(tmp_radar.name, bbox_inches='tight')
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, "2. Analisis de Perfil (Diagrama Radial)", ln=True)
                pdf.image(tmp_radar.name, x=15, w=180)
            
            # Insertar Gráfico Prospectivo
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_scen:
                fig_scen.savefig(tmp_scen.name, bbox_inches='tight')
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, "3. Analisis Prospectivo de Escenarios", ln=True)
                pdf.image(tmp_scen.name, x=15, w=180)
                pdf.ln(5)
                pdf.set_font("Arial", 'I', 11)
                pdf.multi_cell(0, 10, f"Conclusion: El activo {df_res.index[0]} presenta la mayor eficiencia global.")

            # Generar Descarga
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                pdf.output(tmp_pdf.name)
                with open(tmp_pdf.name, "rb") as f:
                    st.download_button("Descargar Reporte Completo", data=f, file_name="Reporte_Certificado_JAVCAM_v6.pdf")
