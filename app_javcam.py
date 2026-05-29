import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile

# 1. CONFIGURACIÓN DE SEGURIDAD Y SECRETOS (NIVEL INMUEBLE)
if "credentials" in st.secrets:
    ADMIN_USER = st.secrets["credentials"]["admin_user"]
    ADMIN_PASSWORD = st.secrets["credentials"]["admin_password"]
    TOKEN_VALIDO = st.secrets["credentials"]["licencia_valida"]
else:
    # Respaldos tácticos en caso de falla de comunicación con el servidor
    ADMIN_USER = "comandante@javcam.com"
    ADMIN_PASSWORD = "PremiumPassword2026"
    TOKEN_VALIDO = "JAVCAM-ENTERPRISE-2026-X9"

# 2. GESTIÓN DE ESTADO DE SESIÓN
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# 3. INTERFAZ DE CONTROL DE ACCESO (LOGIN)
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
# SI EL USUARIO ESTÁ AUTENTICADO, SE DESPLEGARÁ EL SOFTWARE ADELANTE
# =========================================================================

# 4. CONTROL DE LICENCIAMIENTO EN LA BARRA LATERAL
st.sidebar.title("🛸 Panel de Control Operativo")
st.sidebar.write(f"**Operario:** {ADMIN_USER}")

# Caja para digitar el Token Comercial
token_ingresado = st.sidebar.text_input("🔑 Token de Licencia Activa:", value="", type="password")

# Validación dinámica del nivel de acceso
if token_ingresado == TOKEN_VALIDO:
    ES_ENTERPRISE = True
    st.sidebar.success("👑 LICENCIA ENTERPRISE: ACTIVA")
    max_alternativas = 6
else:
    ES_ENTERPRISE = False
    st.sidebar.warning("⚠️ MODO LIMITADO (FREE)")
    st.sidebar.info("Para evaluar más de 3 alternativas, ver gráficos de estrés y descargar reportes PDF, ingrese su Token Corporativo corporativo.")
    max_alternativas = 3

st.sidebar.markdown("---")

# 5. ENTORNO CORE DEL SOFTWARE DE TOMA DE DECISIONES
st.title("📈 JAVCAM Decision Suite - Motor Analítico")
st.write("Bienvenido al entorno de evaluación multicriterio para la gestión de activos.")

# Selección de alternativas basada en el nivel de licencia
num_alternativas = st.slider("Número de Alternativas a Evaluar:", min_value=2, max_value=max_alternativas, value=2)

if not ES_ENTERPRISE and num_alternativas > 3:
    st.error("El Modo Limitado solo permite hasta 3 alternativas. Ingrese un Token Enterprise válido en la barra lateral.")
else:
    st.success(f"Evaluando {num_alternativas} alternativas en entorno seguro.")
    
    # Datos de prueba rápidos para demostrar el funcionamiento gráfico
    criterios = ['C1 (Técnico)', 'C2 (Operaciones)', 'C3 (Costos)']
    valores = np.random.randint(50, 100, size=(num_alternativas, len(criterios)))
    df = pd.DataFrame(valores, columns=criterios, index=[f'Alternativa {i+1}' for i in range(num_alternativas)])
    
    st.write("### 📊 Matriz de Rendimiento de Activos", df)
    
    # 6. SECCIÓN BLOQUEADA PARA MONETIZACIÓN (SOLO ENTERPRISE)
    if ES_ENTERPRISE:
        st.write("---")
        st.write("### 👑 Gráficos Avanzados de Estrés Financiero e Industrial")
        
        # Generar gráfica de barras empresarial
        fig, ax = plt.subplots()
        df.plot(kind='bar', ax=ax)
        plt.title("Análisis de Estrés Comparativo - JAVCAM Enterprise")
        plt.ylabel("Puntaje de Eficiencia")
        st.pyplot(fig)
        
        # Botón de exportación en PDF institucional
        if st.button("📥 Descargar Reporte de Auditoría Matemática (PDF)"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="JAVCAM DECISION SUITE V4.0 - REPORT", ln=1, align="C")
            pdf.cell(200, 10, txt="Licencia Corporativa Enterprise Certificada.", ln=2, align="L")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf.output(tmp.name)
                with open(tmp.name, "rb") as f:
                    st.download_button("Click aquí para guardar PDF", data=f, file_name="Reporte_JAVCAM_Enterprise.pdf", mime="application/pdf")
    else:
        st.write("---")
        st.write("### 🔒 Funciones Enterprise Bloqueadas")
        st.info("Los gráficos de barras avanzados y la exportación de informes en PDF ejecutivo se desbloquearán inmediatamente al ingresar el Token en la barra lateral.")
