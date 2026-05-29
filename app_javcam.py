import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile

# 1. IDENTIDAD Y NAVEGACIÓN
st.set_page_config(page_title="JAVCAM Decision Suite", page_icon="📈", layout="wide")

st.sidebar.title("🛸 JAVCAM Enterprise v4.5")
st.sidebar.write("🟢 **Estado del Motor:** Operacional (Alta Disponibilidad)")
st.sidebar.markdown("---")

# 2. ENTORNO CORE: CONFIGURACIÓN MULTICRITERIO
st.title("📈 JAVCAM Decision Suite - Gestión de Activos Físicos")
st.write("Plataforma avanzada de toma de decisiones e ingeniería de confiabilidad bajo metodologías analíticas.")

st.subheader("⚙️ Configuración del Modelo de Decisión")

col1, col2 = st.columns(2)

with col1:
    # Sin límites restrictivos: el comandante decide cuántas alternativas evaluar
    num_alternativas = st.number_input("Número de Alternativas a Evaluar:", min_value=2, max_value=20, value=4, step=1)

with col2:
    # Configuración dinámica de criterios
    num_criterios = st.number_input("Número de Criterios de Evaluación:", min_value=2, max_value=10, value=3, step=1)

st.markdown("---")

# 3. DINÁMICA: CALIFICACIÓN DE CRITERIOS (PONDERACIÓN AHP)
st.subheader("🎯 Calificación y Ponderación de Criterios")
st.write("Asigne la importancia/peso a cada criterio de evaluación. La suma total debe ser igual al 100% (1.0).")

pesos = []
cols_criterios = st.columns(int(num_criterios))

for i in range(int(num_criterios)):
    with cols_criterios[i]:
        nombre_crit = st.text_input(f"Nombre Criterio {i+1}:", f"Criterio C{i+1}")
        peso_crit = st.slider(f"Peso de {nombre_crit}:", min_value=0.0, max_value=1.0, value=1.0/num_criterios, step=0.05, key=f"peso_{i}")
        pesos.append((nombre_crit, peso_crit))

# Verificación matemática de pesos
total_peso = sum([p[1] for p in pesos])
st.info(f"**Suma total de ponderaciones:** {total_peso:.2f} / 1.00")

if not np.isclose(total_peso, 1.0):
    st.warning("⚠️ Nota: Para mantener la consistencia matemática estricta del modelo, se recomienda que la suma de los pesos sea exactamente 1.0.")

st.markdown("---")

# 4. MATRIZ DE RENDIMIENTO Y CALIFICACIÓN DE ALTERNATIVAS
st.subheader("📊 Matriz de Calificación del Operador")
st.write("Introduzca los puntajes de rendimiento para cada alternativa frente a los criterios definidos (Escala 1 - 100):")

nombres_alternativas = [f"Alternativa {i+1}" for i in range(int(num_alternativas))]
nombres_criterios = [p[0] for p in pesos]

# Crear un diccionario para armar el DataFrame interactivo
datos_iniciales = {}
for n_crit in nombres_criterios:
    datos_iniciales[n_crit] = [80.0] * int(num_alternativas)

df_matriz = pd.DataFrame(datos_iniciales, index=nombres_alternativas)

# Matriz editable en tiempo real por el usuario
matriz_evaluada = st.data_editor(df_matriz, use_container_width=True)

st.markdown("---")

# 5. MOTOR DE PROCESAMIENTO ANALÍTICO (WASPAS / scoring)
st.subheader("🏆 Resultados del Análisis y Ranking Óptimo")

# Cálculo del puntaje ponderado
pesos_vector = np.array([p[1] for p in pesos])
matriz_np = matriz_evaluada.to_numpy()

# Operación matricial de optimización
scores_totales = np.dot(matriz_np, pesos_vector)
df_resultados = pd.DataFrame({"Puntaje de Optimización": scores_totales}, index=nombres_alternativas)
df_resultados = df_resultados.sort_values(by="Puntaje de Optimización", ascending=False)

# Despliegue de Resultados Primarios
col_res1, col_res2 = st.columns([1, 2])

with col_res1:
    st.write("**Ranking de Selección:**")
    st.dataframe(df_resultados, use_container_width=True)
    st.success(f"🥇 **Opción Recomendada:** {df_resultados.index[0]}")

with col_res2:
    # 6. MOTOR GRÁFICO EMPRESARIAL
    fig, ax = plt.subplots(figsize=(7, 4))
    df_resultados.plot(kind='bar', color='#008080', ax=ax, legend=False)
    plt.title("Análisis Comparativo de Estrés y Rendimiento de Activos")
    plt.ylabel("Puntaje Consolidado")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

st.markdown("---")

# 7. GENERACIÓN DE REPORTES EJECUTIVOS (PDF)
st.subheader("📥 Exportación de Auditoría Técnica")

if st.button("Generar Reporte de Auditoría Matemática (PDF)", use_container_width=True):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="JAVCAM DECISION SUITE - INFORME MÁSTER", ln=1, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    pdf.cell(200, 10, txt=f"Reporte de Optimización de Activos Físicos.", ln=1, align="L")
    pdf.cell(200, 10, txt=f"Ganador Estratégico: {df_resultados.index[0]} con {df_resultados.iloc[0,0]:.2f} pts.", ln=1, align="L")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            st.download_button("Descargar Reporte PDF Certificado", data=f, file_name="Reporte_Master_JAVCAM.pdf", mime="application/pdf")
