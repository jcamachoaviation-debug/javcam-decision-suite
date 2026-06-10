import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import itertools

# 1. CONFIGURACIÓN DE IDENTIDAD Y SEGURIDAD (DISEÑO ORIENTADO A MÓVIL)
st.set_page_config(
    page_title="JAVCAM Decision Suite", 
    page_icon="🛡️", 
    layout="centered"
)

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

# LOGIN OBLIGATORIO - COMPACTO PARA PANTALLAS TÁCTILES
if not st.session_state.autenticado:
    st.title("🛡️ Acceso JAVCAM Suite")
    st.subheader("Infraestructura SaaS Móvil v7.6")
    
    usuario = st.text_input("Usuario Corporativo:")
    contrasena = st.text_input("Contraseña:", type="password")
    
    if st.button("Autenticar Sistema", use_container_width=True):
        if usuario == ADMIN_USER and contrasena == ADMIN_PASSWORD:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Acceso Denegado.")
    st.stop()

# 2. CONTROL DE LICENCIA Y CONFIGURACIÓN EN BARRA LATERAL
st.sidebar.title("🛸 Panel Móvil v7.6")
token_ingresado = st.sidebar.text_input("🔑 Token de Licencia:", value="", type="password")

if token_ingresado == TOKEN_VALIDO:
    ES_ENTERPRISE = True
    st.sidebar.success("👑 LICENCIA ENTERPRISE: ACTIVA")
    limite_max = 10
else:
    ES_ENTERPRISE = False
    st.sidebar.warning("⚠️ MODO LIMITADO (FREE)")
    limite_max = 3

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Entorno de Operación")
entorno = st.sidebar.radio(
    "Seleccione el módulo:",
    ["Gestión de Activos Físicos (Ingeniería)", "Optimización de Presupuesto (Marketing Growth)"]
)
st.sidebar.markdown("---")

# 3. CONFIGURACIÓN DINÁMICA SEGÚN EL ENTORNO
if "Marketing" in entorno:
    st.title("📈 JAVCAM Growth Suite")
    st.write("Optimización móvil de presupuesto de marketing y maximización de ROI.")
    label_alt = "Canales de Adquisición:"
    label_crit = "Métricas de Crecimiento (Growth):"
    default_criterios = ["CAC (Costo Adquisición)", "LTV (Valor del Cliente)", "Tasa Conversión (%)"]
    default_alternativas = ["Google Ads", "Meta Ads", "SEO Orgánico"]
else:
    st.title("📈 JAVCAM Decision Suite")
    st.write("Optimización multicriterio para ingeniería de confiabilidad y ciclo de vida.")
    label_alt = "Alternativas de Activos a Evaluar:"
    label_crit = "Criterios de Ingeniería:"
    default_criterios = ["Criterio 1", "Criterio 2", "Criterio 3"]
    default_alternativas = ["Alt 1", "Alt 2", "Alt 3"]

num_alternativas = st.slider(label_alt, 2, limite_max, 3)
num_criterios = st.slider(label_crit, 2, limite_max, 3)

st.markdown("---")

# 4. CRITERIOS Y DIRECCIÓN
st.subheader("🎯 1. Configuración de Variables")
criterios_lista = []
direcciones_lista = []

for i in range(int(num_criterios)):
    st.markdown(f"**Variable V{i+1}**")
    def_name = default_criterios[i] if i < len(default_criterios) else f"Variable {i+1}"
    def_opt = "Min (-)" if "CAC" in def_name or "Costo" in def_name or "Velocidad" in def_name else "Max (+)"
    
    col_n, col_d = st.columns([2, 1])
    with col_n:
        nombre = st.text_input(f"Nombre:", def_name, key=f"nc_{i}")
    with col_d:
        opt_index = 0 if def_opt == "Max (+)" else 1
        direccion = st.selectbox(f"Impacto:", ["Max (+)", "Min (-)"], index=opt_index, key=f"dc_{i}")
        
    criterios_lista.append(nombre)
    direcciones_lista.append(True if "Max" in direccion else False)

st.markdown("---")

# 5. MOTOR DE SAATY CON AJUSTE TÁCTIL
st.subheader("📐 2. Ponderación de Importancia (Saaty)")
combinaciones = list(itertools.combinations(range(int(num_criterios)), 2))
A = np.ones((int(num_criterios), int(num_criterios)))

if len(combinaciones) > 0:
    st.info("💡 Deslice para establecer la importancia relativa entre variables:")
    for idx, (c_i, c_j) in enumerate(combinaciones):
        v = st.slider(f"¿{criterios_lista[c_i]} frente a {criterios_lista[c_j]}?", 0.1, 9.0, 1.0, key=f"s_{c_i}_{c_j}")
        A[c_i, c_j] = v
        A[c_j, c_i] = 1.0 / v

suma_columnas = A.sum(axis=0)
A_normalizada = A / suma_columnas
pesos_saaty = A_normalizada.mean(axis=1)

λ_max = np.sum(suma_columnas * pesos_saaty)
CI = (λ_max - num_criterios) / (num_criterios - 1) if num_criterios > 1 else 0
RI_dict = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
RI = RI_dict.get(int(num_criterios), 1.49)
CR = CI / RI if RI > 0 else 0

st.write("**Pesos e Índices de Consistencia Computados:**")
df_pesos = pd.DataFrame({"Variable": criterios_lista, "Peso": pesos_saaty})
st.dataframe(df_pesos.set_index("Variable"), use_container_width=True)

col_m1, col_m2 = st.columns(2)
with col_m1: st.metric("Índice Consistencia (CI)", f"{CI:.4f}")
with col_m2: st.metric("Razón Consistencia (CR)", f"{CR*100:.1f}%")

if CR < 0.10: st.success("✅ Matriz Consistente.")
else: st.warning("⚠️ Ajuste las comparaciones para mejorar consistencia.")

st.markdown("---")

# 6. ENTRADA DE DATOS Y NORMALIZACIÓN
st.subheader("📊 3. Matriz de Desempeño")
n_alt = [default_alternativas[i] if i < len(default_alternativas) else f"Opción {i+1}" for i in range(int(num_alternativas))]
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
df_res = pd.DataFrame({"Score Global": scores}, index=n_alt).sort_values("Score Global", ascending=False)

st.write("**Ranking del Entorno:**")
st.dataframe(df_res, use_container_width=True)

st.markdown("---")

# 7. COMPARATIVA RADIAL (CORREGIDO DE FORMA DEFINITIVA)
st.subheader("🕸️ 4. Mapa Radial de Desempeño")
categories = criterios_lista
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

fig_radar, ax_radar = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
for i, alt_name in enumerate(n_alt):
    values = matriz_norm[i].tolist()
    values += values[:1]
    ax_radar.plot(angles, values, linewidth=1.5, linestyle='solid', label=alt_name)
    ax_radar.fill(angles, values, alpha=0.02)

ax_radar.set_theta_offset(np.pi / 2)
ax_radar.set_theta_direction(-1)
plt.xticks(angles[:-1], categories, size=9)
plt.yticks(size=8)
# CORRECCIÓN DE PARÁMETRO DE FUENTE: 'fontsize' en lugar de 'size'
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=9)
st.pyplot(fig_radar)

st.markdown("---")

# 8. ANÁLISIS PROSPECTIVO DE ESCENARIOS
st.subheader("🔮 5. Análisis Prospectivo")
fig_scen, ax_scen = plt.subplots(figsize=(6, 3.5))

if not ES_ENTERPRISE:
    st.info("🔒 Ingrese Token Enterprise para desbloquear simulación prospectiva.")
else:
    p_pes = np.array([0.8 if not d else 0.2 for d in direcciones_lista])
    p_pes /= p_pes.sum()
    p_opt = np.array([0.8 if d else 0.2 for d in direcciones_lista])
    p_opt /= p_opt.sum()
    
    df_pros = pd.DataFrame({
        "Riesgo": np.dot(matriz_norm, p_pes),
        "Base": scores,
        "Expansión": np.dot(matriz_norm, p_opt)
    }, index=n_alt)
    
    st.dataframe(df_pros, use_container_width=True)
    df_pros.T.plot(kind="line", marker="o", ax=ax_scen, linewidth=2)
    plt.xticks(size=9)
    plt.yticks(size=9)
    # Corrección preventiva de leyenda para consistencia interna
    plt.legend(fontsize=9)
    plt.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig_scen)

# 9. REPORTE PDF MULTIGRÁFICO CONFIGURABLE
st.markdown("---")
if st.button("📥 Generar Reporte Certificado (PDF)", use_container_width=True):
    if not ES_ENTERPRISE:
        st.error("Función exclusiva de la Licencia Enterprise.")
    else:
        with st.spinner("Compilando gráficos..."):
            pdf = FPDF()
            
            # PÁGINA 1
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, f"JAVCAM SUITE v7.6 - REPORTE", ln=True, align='C')
            pdf.set_font("Arial", '', 12)
            pdf.cell(200, 10, f"Entorno: {entorno} | Operario: {ADMIN_USER}", ln=True, align='C')
            pdf.ln(10)
            
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, "1. Jerarquia de Seleccion Optima", ln=True)
            pdf.set_font("Arial", '', 11)
            for i, row in df_res.iterrows():
                pdf.cell(200, 8, f"{i}: {row['Score Global']:.4f}", ln=True)
            pdf.ln(5)
            
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, "2. Metricas de Consistencia (AHP)", ln=True)
            pdf.set_font("Arial", '', 11)
            pdf.cell(200, 8, f"Lambda Max: {λ_max:.4f}", ln=True)
            pdf.cell(200, 8, f"Indice de Consistencia (CI): {CI:.4f}", ln=True)
            pdf.cell(200, 8, f"Razon de Consistencia (CR): {CR*100:.2f}%", ln=True)
            
            # PÁGINA 2
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_radar:
                fig_radar.savefig(tmp_radar.name, bbox_inches='tight')
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, "3. Grafica Radial de Desempeño", ln=True)
                pdf.image(tmp_radar.name, x=15, w=160)
            
            # PÁGINA 3
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_scen:
                fig_scen.savefig(tmp_scen.name, bbox_inches='tight')
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, "4. Tendencia Prospectiva", ln=True)
                pdf.image(tmp_scen.name, x=15, w=160)
                pdf.ln(10)
                pdf.set_font("Arial", 'I', 11)
                pdf.multi_cell(0, 10, f"Conclusion: El analisis multicriterio certifica que la opcion recomendada bajo el entorno operativo actual es: {df_res.index[0]}.")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                pdf.output(tmp_pdf.name)
                with open(tmp_pdf.name, "rb") as f:
                    st.download_button("Descargar Reporte Completo", data=f, file_name="Reporte_Master_JAVCAM_v7.6.pdf")
