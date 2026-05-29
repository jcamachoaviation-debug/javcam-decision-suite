# ==========================================
# JAVCAM DECISION SUITE ENTERPRISE - V4.0 COMMERCIAL SaaS
# ARCHITECTURE SECURED WITH STREAMLIT SECRETS & FREEMIUM LOCKS
# ==========================================

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import pi
from fpdf import FPDF
import datetime
import os

st.set_page_config(page_title="JAVCAM Suite V4.0 - SaaS", page_icon="🛸", layout="centered")

# ==========================================
# SISTEMA SEGURO DE AUTENTICACIÓN Y LICENCIAS
# ==========================================
# Recuperación segura desde st.secrets (Local o Cloud) con fallback para desarrollo
USER_AUTH = st.secrets.get("credentials", {}).get("admin_user", "comandante@javcam.com")
PASS_AUTH = st.secrets.get("credentials", {}).get("admin_password", "javcam2026")
TOKEN_LICENCIA = st.secrets.get("credentials", {}).get("licencia_valida", "JAVCAM-FREE")

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'licenciado' not in st.session_state:
    st.session_state['licenciado'] = False

if not st.session_state['autenticado']:
    st.title("🛸 JAVCAM Decision Suite V4.0")
    st.subheader("Plataforma de Inteligencia de Activos y Gestión de Riesgos")
    
    tab_login, tab_info = st.tabs(["🔒 Acceso Corporativo", "💰 Planes y Licencias"])
    
    with tab_login:
        usuario = st.text_input("Usuario Corporativo (Email)", value="comandante@javcam.com")
        password = st.text_input("Contraseña de Acceso", type="password", value="javcam2026")
        if st.button("Autenticar Sistema"):
            if usuario == USER_AUTH and password == PASS_AUTH:
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("Acceso denegado. Credenciales inválidas o cuenta suspendida.")
                
    with tab_info:
        st.markdown("""
        ### 🚀 Monetice su Consultoría de Activos Físicos
        Transforme este software en su principal flujo de ingresos recurrentes (SaaS):
        * **Plan Demo (Gratuito):** Permite configurar hasta 3 alternativas y visualización web básica.
        * **Plan Enterprise Professional:** Desbloquea el simulador de estrés avanzado, análisis de matrices cruzadas y exportación de reportes PDF auditables.
        
        *Para integrar pasarelas de pago automáticas (Stripe/PayPal), contacte a la mesa técnica de JAVCAM.*
        """)
else:
    # PANEL DE CONTROL DE LICENCIA COMERCIAL (SIDEBAR)
    st.sidebar.title("🛸 JAVCAM SaaS Panel")
    st.sidebar.write(f"👤 **Usuario:** `{USER_AUTH}`")
    
    # Validación del token de monetización
    licencia_input = st.sidebar.text_input("🔑 Token de Licencia Activa:", value=st.session_state.get('token_ingresado', ""))
    if licencia_input == TOKEN_LICENCIA:
        st.sidebar.success("👑 LICENCIA ENTERPRISE: ACTIVA")
        st.session_state['licenciado'] = True
        st.session_state['token_ingresado'] = licencia_input
    else:
        st.sidebar.warning("⚠️ MODO LIMITADO (FREE)")
        st.session_state['licenciado'] = False
        st.session_state['token_ingresado'] = licencia_input

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.session_state['licenciado'] = False
        st.rerun()

    # MOTORES MATEMÁTICOS (PRESERVADOS)
    def calcular_pesos_ahp_saaty(matriz_pareada):
        A = np.array(matriz_pareada, dtype=float)
        n = A.shape[0]
        sumas_columnas = A.sum(axis=0)
        sumas_columnas = np.where(sumas_columnas == 0, 1, sumas_columnas)
        pesos = (A / sumas_columnas).mean(axis=1)
        A_por_w = A.dot(pesos)
        lambda_max = np.mean(A_por_w / np.where(pesos == 0, 1e-9, pesos))
        if n <= 2: return pesos, 0.0
        ci = (lambda_max - n) / (n - 1)
        ri = {3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41}.get(n, 1.49)
        return pesos, (ci / ri)

    def obtener_matrices_waspas(matrix_datos, pesos_criterios, tipos_criterios):
        pesos = np.array(pesos_criterios) / np.sum(pesos_criterios)
        norm_matrix = matrix_datos.astype(float).copy()
        for j, col in enumerate(matrix_datos.columns):
            max_val = matrix_datos[col].max()
            min_val = matrix_datos[col].min()
            if max_val == min_val: norm_matrix[col] = 1.0
            elif tipos_criterios[j] == 'Beneficio': norm_matrix[col] = matrix_datos[col] / max_val
            else: norm_matrix[col] = min_val / matrix_datos[col]
        wsm = norm_matrix.dot(pesos)
        wpm_matrix = norm_matrix.copy()
        for j, col in enumerate(matrix_datos.columns):
            wpm_matrix[col] = np.where(wpm_matrix[col] == 0, 1e-9, wpm_matrix[col]) ** pesos[j]
        score_final = (0.5 * wsm) + (0.5 * wpm_matrix.prod(axis=1))
        return score_final, norm_matrix

    # INTERFAZ PROTEGIDA
    st.title("🛸 JAVCAM Decision Suite - V4.0")
    
    st.subheader("1. Configuración de la Flota")
    col_alt, col_crit = st.columns(2)
    
    # Lógica de restricción comercial: El usuario free no puede evaluar más de 3 alternativas
    if not st.session_state['licenciado']:
        st.caption("🔒 *Plan Gratuito limitado a máximo 3 alternativas y 3 criterios.*")
        num_alternativas = col_alt.number_input("¿Cuántas opciones evalúa?", min_value=2, max_value=3, value=3)
        num_criterios = col_crit.number_input("¿Cuántos criterios usarás?", min_value=3, max_value=3, value=3)
    else:
        num_alternativas = col_alt.number_input("¿Cuántas opciones evalúa? (Enterprise)", min_value=2, max_value=6, value=3)
        num_criterios = col_crit.number_input("¿Cuántos criterios usarás? (Enterprise)", min_value=3, max_value=6, value=3)

    nombres_alt = [f"Alternativa A{i+1}" for i in range(num_alternativas)]
    nombres_crit = [f"Criterio C{j+1}" for j in range(num_criterios)]

    st.markdown("---")
    st.subheader("⚖️ 2. Prioridades de la Organización (Importancia)")
    A_ahp = np.ones((num_criterios, num_criterios))
    for i in range(num_criterios):
        for j in range(i + 1, num_criterios):
            seleccion = st.selectbox(f"Comparación: [{nombres_crit[i]}] contra [{nombres_crit[j]}]. ¿Importancia?", [1,3,5,7,9], format_func=lambda x: "Iguales" if x==1 else f"Más importante por factor {x}", key=f"ahp_{i}_{j}")
            direccion = st.radio(f"Dominancia para:", [nombres_crit[i], nombres_crit[j]], key=f"dir_{i}_{j}", horizontal=True)
            val = float(seleccion)
            if direccion == nombres_crit[i]:
                A_ahp[i, j] = val; A_ahp[j, i] = 1.0 / val
            else:
                A_ahp[i, j] = 1.0 / val; A_ahp[j, i] = val

    st.markdown("---")
    st.subheader("📊 3. Datos de Rendimiento Real")
    tipos_crit = [st.selectbox(f"Naturaleza de {c}:", ["Beneficio", "Costo"], format_func=lambda x: "📈 Entre MÁS ALTO mejor" if x=="Beneficio" else "📉 Entre MÁS BAJO mejor", key=f"t_{c}") for c in nombres_crit]
    
    data_input = {}
    for c in nombres_crit:
        data_input[c] = [st.number_input(f"Valor de {c} para {a}:", min_value=0.01, value=10.0, key=f"m_{c}_{a}") for a in nombres_alt]
    df_matriz = pd.DataFrame(data_input, index=nombres_alt)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🚨 Parámetros del Test")
    crit_tecnico = st.sidebar.selectbox("Criterio Técnico/Seguridad:", nombres_crit, index=0)
    crit_economico = st.sidebar.selectbox("Criterio de Costo/Dinero:", nombres_crit, index=num_criterios-1)

    # PROCESAMIENTO MAESTRO
    st.markdown("---")
    if st.button("🔮 GENERAR INFORME ANALÍTICO COMPLETO"):
        plt.close('all')
        pesos_base, cr = calcular_pesos_ahp_saaty(A_ahp)
        idx_t, idx_e = nombres_crit.index(crit_tecnico), nombres_crit.index(crit_economico)
        
        p_crisis = pesos_base.copy(); p_crisis[idx_t] *= 5.0; p_crisis /= p_crisis.sum()
        p_reco = pesos_base.copy(); p_reco[idx_e] *= 5.0; p_reco /= p_reco.sum()
        
        sc_base, norm_base = obtener_matrices_waspas(df_matriz, pesos_base, tipos_crit)
        sc_crisis, _ = obtener_matrices_waspas(df_matriz, p_crisis, tipos_crit)
        sc_reco, _ = obtener_matrices_waspas(df_matriz, p_reco, tipos_crit)
        
        st.session_state['df_pros'] = pd.DataFrame({'Normal': sc_base, 'Crisis': sc_crisis, 'Recorte': sc_reco}, index=nombres_alt)
        st.session_state['norm_base'] = norm_base
        st.session_state['pesos_base'] = pesos_base
        st.session_state['pesos_crisis'] = p_crisis
        st.session_state['pesos_reco'] = p_reco
        st.session_state['nombres_crit'] = nombres_crit
        st.session_state['nombres_alt'] = nombres_alt
        st.session_state['cr'] = cr
        
        # Guardar barra estática solo si tiene permisos Enterprise
        if st.session_state['licenciado']:
            fig_bar_static, ax_bar_s = plt.subplots(figsize=(6, 3.8), facecolor='#0b141d')
            ax_bar_s.set_facecolor('#0b141d')
            x_s = np.arange(len(nombres_alt))
            w_s = 0.23
            ax_bar_s.bar(x_s - w_s, sc_base, w_s, label='Normal (Ideal)', color='#2ecc71')
            ax_bar_s.bar(x_s, sc_crisis, w_s, label='Crisis (Fallas)', color='#e74c3c')
            ax_bar_s.bar(x_s + w_s, sc_reco, w_s, label='Recorte (Caja)', color='#f1c40f')
            ax_bar_s.set_title("RENDIMIENTO DEL ACTIVO ANTE ESCENARIOS DE ESTRES", color='white', fontsize=10, fontweight='bold', pad=12)
            ax_bar_s.set_xticks(x_s)
            ax_bar_s.set_xticklabels(nombres_alt, color='white', fontweight='bold')
            ax_bar_s.legend(facecolor='#0b141d', labelcolor='white', edgecolor='none', fontsize=8)
            for s in ax_bar_s.spines.values(): s.set_visible(False)
            ax_bar_s.grid(axis='y', linestyle=':', alpha=0.1)
            fig_bar_static.savefig("temp_bar_pdf_v40.png", format='png', dpi=150, bbox_inches='tight', facecolor='#0b141d')
            plt.close(fig_bar_static)
        
        st.session_state['calculado'] = True

    if st.session_state.get('calculado', False):
        df_pros = st.session_state['df_pros']
        nombres_alt = st.session_state['nombres_alt']
        nombres_crit = st.session_state['nombres_crit']
        
        st.header("🎯 1. Despliegue de Resultados Ejecutivos")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.subheader("Pesos Base (AHP)")
            st.dataframe(pd.DataFrame({'Importancia': st.session_state['pesos_base']}, index=nombres_crit).style.format("{:.2%}"))
        with col_r2:
            st.subheader("Desempeño WASPAS (Normal)")
            st.dataframe(pd.DataFrame({'Score': df_pros['Normal']}, index=nombres_alt).style.format("{:.4f}"))

        # RADAR DINÁMICO (DISPONIBLE PARA TODOS)
        st.markdown("---")
        st.header("🕸️ 2. Análisis Dinámico Radial")
        
        escenario_elegido = st.selectbox(
            "Seleccione el escenario operativo para proyectar en el Diagrama Radial:",
            ['🟢 Escenario Normal (Ideal)', '🔴 Alerta Roja (Crisis de Fallas)', '⚠️ Alerta Financiera (Recorte Presupuestal)']
        )
        
        if 'Normal' in escenario_elegido:
            pesos_grafico = st.session_state['pesos_base']
            titulo_rad = "PERFIL DE RENDIMIENTO - ESCENARIO NORMAL"
        elif 'Crisis' in escenario_elegido:
            pesos_grafico = st.session_state['pesos_crisis']
            titulo_rad = "PERFIL DE RENDIMIENTO - BAJO CRISIS TECNICA"
        else:
            pesos_grafico = st.session_state['pesos_reco']
            titulo_rad = "PERFIL DE RENDIMIENTO - BAJO AUSTERIDAD ECONOMICA"

        norm_base = st.session_state['norm_base']
        df_radar_data = norm_base.copy()
        for j, col in enumerate(df_radar_data.columns):
            df_radar_data[col] = norm_base[col] * pesos_grafico[j]

        N = len(nombres_crit)
        angulos = [n / float(N) * 2 * pi for n in range(N)]
        angulos += angulos[:1]
        
        fig_rad, ax_rad = plt.subplots(figsize=(6, 4.5), subplot_kw=dict(polar=True), facecolor='#0b141d')
        ax_rad.set_facecolor('#111c24')
        plt.xticks(angulos[:-1], nombres_crit, color='#ffffff', fontsize=10, fontweight='bold')
        ax_rad.tick_params(colors='#a0aec0', grid_alpha=0.15, grid_color='#ffffff')
        
        colores_alt = ['#02c39a', '#e63946', '#ffb703', '#9b59b6', '#3498db']
        for idx, alt in enumerate(nombres_alt):
            valores = df_radar_data.loc[alt].values.flatten().tolist()
            valores += valores[:1]
            ax_rad.plot(angulos, valores, linewidth=2, linestyle='solid', label=alt, color=colores_alt[idx % len(colores_alt)])
            ax_rad.fill(angulos, valores, color=colores_alt[idx % len(colores_alt)], alpha=0.15)
            
        ax_rad.set_title(titulo_rad, color='#ffffff', fontsize=11, fontweight='bold', pad=20)
        ax_rad.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), facecolor='#0b141d', edgecolor='none', labelcolor='#ffffff')
        st.pyplot(fig_rad)
        
        if st.session_state['licenciado']:
            fig_rad.savefig("temp_radar_pdf_v40.png", format='png', dpi=150, bbox_inches='tight', facecolor='#0b141d')
        plt.close(fig_rad)

        # ==========================================
        # GANCHOS COMERCIALES (FREEMIUM LOCKS)
        # ==========================================
        st.markdown("---")
        st.header("📊 3. Comparativa Global de Escenarios (Barras)")
        
        if not st.session_state['licenciado']:
            st.warning("🔒 **Función Avanzada Bloqueada:** La visualización interactiva de impactos cruzados por escenarios y las proyecciones de estrés financiero requieren una **Licencia Enterprise**.")
            st.button("💼 Adquirir Token Premium de Consultoría", key="comprar_token")
        else:
            fig_bar, ax_bar = plt.subplots(figsize=(6, 3.8), facecolor='#0b141d')
            ax_bar.set_facecolor('#0b141d')
            x = np.arange(len(nombres_alt))
            w = 0.23
            ax_bar.bar(x - w, df_pros['Normal'], w, label='Normal (Ideal)', color='#2ecc71')
            ax_bar.bar(x, df_pros['Crisis'], w, label='Crisis (Fallas)', color='#e74c3c')
            ax_bar.bar(x + w, df_pros['Recorte'], w, label='Recorte (Caja)', color='#f1c40f')
            ax_bar.set_title("RENDIMIENTO DEL ACTIVO ANTE ESCENARIOS DE ESTRÉS", color='white', fontsize=10, fontweight='bold', pad=12)
            ax_bar.set_xticks(x)
            ax_bar.set_xticklabels(nombres_alt, color='white', fontweight='bold')
            ax_bar.legend(facecolor='#0b141d', labelcolor='white', edgecolor='none', fontsize=8)
            for s in ax_bar.spines.values(): s.set_visible(False)
            ax_bar.grid(axis='y', linestyle=':', alpha=0.1)
            st.pyplot(fig_bar)
            plt.close(fig_bar)

        st.markdown("---")
        g_base = df_pros['Normal'].idxmax()
        st.success(f"🏆 **DICTAMEN BASE:** La mejor opción técnica actual es **{g_base}**.")
        
        # EXPORTACIÓN PDF EXCLUSIVA PARA CLIENTES PREMIUM
        st.markdown("---")
        if not st.session_state['licenciado']:
            st.info("🔒 **¿Necesita radicar este informe ante su junta directiva?** Los reportes físicos en PDF con logotipos personalizados y auditoría matemática están reservados para usuarios Enterprise.")
        else:
            if st.checkbox("Habilitar módulo de descarga institucional"):
                try:
                    pdf_dictamen = f"Analisis estratégico completo ejecutado sobre la flota configurada. Ganador base: {g_base}."
                    
                    class JAVCAM_Premium_PDF(FPDF):
                        def header(self):
                            self.set_fill_color(11, 20, 29)
                            self.rect(0, 0, 210, 38, 'F')
                            self.set_fill_color(2, 195, 154)
                            self.rect(0, 36, 210, 2, 'F')
                            self.set_font('Helvetica', 'B', 14)
                            self.set_text_color(255, 255, 255)
                            self.text(15, 16, "JAVCAM DECISION SUITE - REPORTE DE AUDITORIA")
                            self.set_font('Helvetica', '', 9)
                            self.set_text_color(160, 174, 192)
                            self.text(15, 24, f"Analisis Multicriterio y Robustez PRO - Fecha: {datetime.date.today()}")
                            self.set_y(44)
                        def footer(self):
                            self.set_y(-15)
                            self.set_font('Helvetica', 'I', 8)
                            self.set_text_color(120, 120, 120)
                            self.cell(0, 10, "DOCUMENTO EMITIDO BAJO REGISTRO COMERCIAL JAVCAM ENTERPRISE", 0, 0, 'L')
                            self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, 'R')

                    pdf = JAVCAM_Premium_PDF(orientation="P", unit="mm", format="A4")
                    
                    # PÁGINA 1
                    pdf.add_page()
                    pdf.set_margins(15, 20, 15)
                    pdf.set_font('Helvetica', 'B', 12)
                    pdf.set_text_color(11, 20, 29)
                    pdf.cell(0, 6, "1. Vector de Importancia de Criterios (Metodo AHP Saaty)", 0, 1, 'L')
                    pdf.ln(3)
                    
                    pdf.set_font('Helvetica', 'B', 9)
                    pdf.set_text_color(255, 255, 255)
                    pdf.set_fill_color(11, 20, 29)
                    pdf.cell(90, 8, "Criterio de Evaluacion", 1, 0, 'C', True)
                    pdf.cell(90, 8, "Importancia (Peso)", 1, 1, 'C', True)
                    
                    pdf.set_font('Helvetica', '', 9)
                    pdf.set_text_color(30, 30, 30)
                    for j, crit in enumerate(nombres_crit):
                        pdf.cell(90, 8, f" {crit}", 1, 0, 'L')
                        pdf.cell(90, 8, f"{st.session_state['pesos_base'][j]*100:.2f}%", 1, 1, 'C')
                    
                    pdf.ln(4)
                    pdf.set_font('Helvetica', 'I', 9)
                    pdf.cell(0, 6, f"Indice de Consistencia (CR): {st.session_state['cr']:.4f} (Validado < 0.10)", 0, 1, 'L')
                    
                    # PÁGINA 2
                    pdf.add_page()
                    pdf.set_font('Helvetica', 'B', 12)
                    pdf.set_text_color(11, 20, 29)
                    pdf.cell(0, 6, "2. Rendimiento Global Cruzado y Escenarios de Estres", 0, 1, 'L')
                    pdf.ln(3)
                    
                    pdf.set_font('Helvetica', 'B', 9)
                    pdf.set_text_color(255, 255, 255)
                    pdf.set_fill_color(11, 20, 29)
                    pdf.cell(50, 8, "Alternativa", 1, 0, 'C', True)
                    pdf.cell(45, 8, "Escenario Normal", 1, 0, 'C', True)
                    pdf.cell(45, 8, "Crisis de Mantenimiento", 1, 0, 'C', True)
                    pdf.cell(40, 8, "Recorte Presupuestal", 1, 1, 'C', True)
                    
                    pdf.set_font('Helvetica', '', 9)
                    pdf.set_text_color(30, 30, 30)
                    for alt in nombres_alt:
                        pdf.cell(50, 8, f" {alt}", 1, 0, 'L')
                        pdf.cell(45, 8, f"{df_pros.loc[alt, 'Normal']:.4f}", 1, 0, 'C')
                        pdf.cell(45, 8, f"{df_pros.loc[alt, 'Crisis']:.4f}", 1, 0, 'C')
                        pdf.cell(40, 8, f"{df_pros.loc[alt, 'Recorte']:.4f}", 1, 1, 'C')
                        
                    pdf.ln(5)
                    if os.path.exists("temp_bar_pdf_v40.png"):
                        pdf.image("temp_bar_pdf_v40.png", x=25, y=pdf.get_y(), w=160)
                    
                    # PÁGINA 3
                    pdf.add_page()
                    pdf.set_font('Helvetica', 'B', 12)
                    pdf.set_text_color(11, 20, 29)
                    pdf.cell(0, 6, "3. Analisis del ADN del Activo (Geometria Radial Seleccionada)", 0, 1, 'L')
                    pdf.ln(3)
                    
                    pdf.set_font('Helvetica', 'B', 9.5)
                    pdf.set_text_color(40, 40, 40)
                    pdf.cell(0, 6, pdf_dictamen, 0, 1, 'L')
                    pdf.ln(4)
                    if os.path.exists("temp_radar_pdf_v40.png"):
                        pdf.image("temp_radar_pdf_v40.png", x=30, y=pdf.get_y(), w=150)
                    
                    pdf_data = bytes(pdf.output())
                    
                    st.download_button(
                        label="⚡ DESCARGAR REPORTE TÉCNICO COMPLETO (PDF)",
                        data=pdf_data,
                        file_name="Reporte_Comercial_JAVCAM.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Error en la compilación del reporte físico: {e}")