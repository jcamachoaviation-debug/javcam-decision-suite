import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import itertools

# 1. CONFIGURACIÓN DE IDENTIDAD Y SEGURIDAD
st.set_page_config(page_title="JAVCAM Decision Suite v6.5", page_icon="🛡️", layout="wide")

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
    st.subheader("Infraestructura de Gestión de Activos Físicos v6.5")
    
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
st.sidebar.title("🛸 Panel Operativo v6.5")
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

# 5. SAATY Y CÁLCULO MATEMÁTICO DE CONSISTENCIA
st.subheader("📐 2. Ponderación Científica (Saaty)")
combinaciones = list(itertools.combinations(range(int(num_criterios)), 2))
A = np.ones((int(num_criterios), int(num_criterios)))
if len(combinaciones) > 0:
    cols_saaty = st.columns(min(3, len(combinaciones)))
    for idx, (c_i, c_j) in enumerate(combinaciones):
        with cols_saaty[idx % min(3, len(combinaciones))]:
            v = st.slider(f"{criterios_lista[c_i]} vs {criterios_lista[c_j]}", 0.1, 9.0, 1.0, key=f"s_{c_i}_{c_j}")
            A[c_i, c_j] = v
            A[c_j, c_i] = 1.0 / v

# Cálculo del Vector de Prioridad (Pesos)
suma_columnas = A.sum(axis=0)
A_normalizada = A / suma_columnas
pesos_saaty = A_normalizada.mean(axis=1)

# --- ALGORITMO ESTRICTO DE CONSISTENCIA DE SAATY ---
λ_max = np.sum(suma_columnas * pesos_saaty)
CI = (λ_max - num_criterios) / (num_criterios - 1) if num_criterios > 1 else 0
# Tabla de Índices Aleatorios de Saaty (RI)
RI_dict = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
RI = RI_dict.get(int(num_criterios), 1.49)
CR = CI / RI if RI > 0 else 0

st.write("**Pesos de Criterios Consolidados:**")
df_pesos = pd.DataFrame({"Criterio": criterios_lista, "Peso Asignado": pesos_saaty})
st.dataframe(df_pesos.set_index("Criterio"), use_container_width=True)

# Despliegue de los resultados solicitados del Índice de Consistencia
col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    st.metric(label="Valor Propio Máximo (λ max)", value=f"{λ_max:.4f}")
with col_c2:
    st.metric(label="Índice de Consistencia (CI)", value=f"{CI:.4f}")
with col_c3:
    st.metric(label="Razón de Consistencia (CR)", value=f"{CR*100:.2f}%")

if CR < 0.10:
    st.success(f"✅ Matriz con Consistencia Aceptable (CR < 10%)")
else:
    st.warning(f"⚠️ Inconsistencia elevada (CR >= 10%). Se recomienda revisar los juicios pareados.")

st.markdown("---")

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

fig_radar, ax_radar = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
for i, alt_name in enumerate(n_alt):
    values = matriz_norm[i].tolist()
    values += values[:1]
    ax_radar.plot(angles, values, linewidth=2, linestyle='solid', label=alt_name)
    ax_radar.fill(angles, values, alpha=0.05)

ax_radar.set_theta_offset(np.pi / 2)
ax_radar.set_theta_direction(-1)
plt.xticks(angles[:-1], categories)
plt.title("Perfil de Desempeño por Criterio", size=14, y=1.1)
plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))
st.pyplot(fig_radar)

st.markdown("---")

# 8. PROSPECTIVA (SÓLO ENTERPRISE)
st.subheader("🔮 5. Análisis Prospectivo")
fig_scen, ax_scen = plt.subplots(figsize=(10, 4))
if not ES_ENTERPRISE:
    st.info("🔒 Módulo Bloqueado. Ingrese Token.")
else:
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

# 9. REPORTE PDF MULTIGRÁFICO COMPLETO
st.markdown("---")
if st.button("📥 Generar Reporte Integral Certificado (PDF)", use_container_width=True):
    if not ES_ENTERPRISE:
        st.error("Función exclusiva de la Licencia Enterprise.")
    else:
        with st.spinner("Compilando gráficos y análisis técnico..."):
            pdf = FPDF()
            
            # PÁGINA 1: DATOS, RANKING Y AUDITORÍA DE SAATY
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, "JAVCAM DECISION SUITE v6.5 - INFORME MAESTRO", ln=True, align='C')
            pdf.set_font("Arial", '', 12)
            pdf.cell(200, 10, f"Operario: {ADMIN_USER} | Certificación Enterprise", ln=True, align='C')
            pdf.ln(10)
            
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, "1. Ranking de Seleccion Optima", ln=True)
            pdf.set_font("Arial", '', 11)
            for i, row in df_res.iterrows():
                pdf.cell(200, 8, f"{i}: {row['Score']:.4f}", ln=True)
            pdf.ln(5)
            
            # Datos de Consistencia en el PDF
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, "2. Auditoria de Consistencia (Metodologia Saaty)", ln=True)
            pdf.set_font("Arial", '', 11)
            pdf.cell(200, 8, f"Valor Propio Maximo (Lambda Max): {λ_max:.4f}", ln=True)
            pdf.cell(200, 8, f"Indice de Consistencia (CI): {CI:.4f}", ln=True)
            pdf.cell(200, 8, f"Razon de Consistencia (CR): {CR*100:.2f}%", ln=True)
            pdf.cell(200, 8, f"Estado del Modelo: {'CONSISTENTE' if CR < 0.10 else 'INCONSISTENTE'}", ln=True)
            
            # PÁGINA 2: DIAGRAMA RADIAL
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_radar:
                fig_radar.savefig(tmp_radar.name, bbox_inches='tight')
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, "3. Analisis de Perfil (Diagrama Radial)", ln=True)
                pdf.image(tmp_radar.name, x=15, w=170)
            
            # PÁGINA 3: PROSPECTIVA DE ESCENARIOS
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_scen:
                fig_scen.savefig(tmp_scen.name, bbox_inches='tight')
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, "4. Analisis Prospectivo de Escenarios", ln=True)
                pdf.image(tmp_scen.name, x=15, w=170)
                pdf.ln(10)
                pdf.set_font("Arial", 'I', 11)
                pdf.multi_cell(0, 10, f"Conclusion de Auditoria: El sistema valida que la opcion lider bajo el analisis optimizado y consistente es {df_res.index[0]}.")

            # Descarga del archivo final
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                pdf.output(tmp_pdf.name)
                with open(tmp_pdf.name, "rb") as f:
                    st.download_button("Descargar Reporte Completo", data=f, file_name="Reporte_Certificado_JAVCAM_v6.5.pdf")
