import streamlit as st
import json
import traceback
from datetime import datetime
from pytz import timezone
import pandas as pd
from gera_relatorio import gerar_relatorio, processar_json
from logger import registrar_log

def render_incident_report_page():
    """
    Renderiza a página de relatório de incidentes no Streamlit.
    
    Esta função é responsável por:
    1. Criar a interface para upload de arquivos JSON
    2. Permitir a configuração de período para o relatório
    3. Processar os dados e exibir o relatório formatado
    4. Mostrar estatísticas e detalhes dos dados processados
    
    É chamada diretamente do arquivo principal generate_chg_report.py
    """
    # Cabeçalho da página
    st.markdown("""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="color: #1f61d9; margin-bottom: 20px;">📊 Relatório de Incidentes</h2>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        # Descrição da funcionalidade
        st.markdown("""
            <div style="background-color: white; padding: 15px; border-radius: 8px; border-left: 4px solid #1f61d9; margin-bottom: 20px;">
                <p style="margin: 0; font-size: 0.9em;">
                    Gere relatórios de incidentes formatados para o Keep. Faça upload de um arquivo JSON com os dados dos incidentes.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Layout em duas colunas para opções e upload
        col1, col2 = st.columns([1, 1])
        
        # Coluna de configurações
        with col1:
            # Opções de período
            st.subheader("Configurações do Relatório")
            periodo_options = ["Usar data atual", "Especificar data"]
            periodo_selecionado = st.radio("Período do relatório:", periodo_options)
            
            data_customizada = None
            if periodo_selecionado == "Especificar data":
                data_customizada = st.date_input(
                    "Selecione a data:",
                    datetime.now(timezone('America/Sao_Paulo'))
                )
        
        # Coluna de upload
        with col2:
            st.subheader("Upload de Dados")
            uploaded_json = st.file_uploader(
                "Faça upload do arquivo JSON de incidentes",
                type=["json"],
                key="json_uploader",
                help="Selecione o arquivo JSON contendo os dados de incidentes"
            )
            
            # Exibir detalhes do arquivo quando carregado
            if uploaded_json:
                file_details = {"Filename": uploaded_json.name, "FileType": uploaded_json.type, "FileSize": f"{uploaded_json.size/1024:.2f} KB"}
                st.json(file_details)

        # Botão para processar o JSON
        if uploaded_json:
            if st.button("Processar JSON e Gerar Relatório", type="primary", use_container_width=True):
                try:
                    with st.spinner('Processando arquivo JSON...'):
                        # Carregar e processar o JSON
                        json_content = uploaded_json.getvalue().decode('utf-8')
                        json_data = json.loads(json_content)
                        
                        # Preparar a data para o relatório
                        data_para_relatorio = None
                        if periodo_selecionado == "Especificar data":
                            data_para_relatorio = data_customizada
                        
                        # Gerar o relatório usando as funções do gera_relatorio.py
                        relatorio = gerar_relatorio(json_data, data_para_relatorio)
                        
                        # Feedback de sucesso
                        st.markdown(f"""
                            <div class="success-message">
                                ✅ Relatório de incidentes gerado com sucesso!
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Abas para visualização dos resultados
                        preview_tabs = st.tabs(["Relatório para Copiar", "Dados Processados"])
                        
                        # Aba do relatório formatado
                        with preview_tabs[0]:
                            # Exibir o relatório em uma caixa de código para facilitar a cópia
                            st.code(relatorio, language=None)
                            
                            # Instruções para cópia
                            st.markdown("""
                                <div style="background-color: #e7f3e7; padding: 10px; border-radius: 5px; margin-top: 15px;">
                                    <p style="margin: 0; font-size: 0.9em;">
                                        ℹ️ Selecione o texto acima e use Ctrl+C (ou Cmd+C) para copiar o relatório.
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # Aba de estatísticas e detalhes
                        with preview_tabs[1]:
                            # Processar os dados para estatísticas
                            dados_processados = processar_json(json_data)
                            
                            # Calcular estatísticas
                            st.subheader("Contagem de Incidentes")
                            estatisticas = {
                                "Incidentes Críticos": len(dados_processados["criticos"]),
                                "Incidentes Altos": len(dados_processados["altos"]),
                                "Incidentes Específicos": len(dados_processados["especificos"]),
                                "Incidentes VIPS": len(dados_processados["vips"]),
                                "Total": len(dados_processados["criticos"]) + 
                                        len(dados_processados["altos"]) + 
                                        len(dados_processados["especificos"]) + 
                                        len(dados_processados["vips"])
                            }
                            
                            # Exibir estatísticas como tabela
                            st.table(pd.DataFrame(list(estatisticas.items()), 
                                                 columns=["Categoria", "Quantidade"]).set_index("Categoria"))
                            
                            # Mostrar exemplos de cada categoria
                            if dados_processados["criticos"]:
                                with st.expander("Ver detalhes dos Incidentes Críticos"):
                                    st.json(dados_processados["criticos"][0])
                            
                            if dados_processados["especificos"]:
                                with st.expander("Ver detalhes dos Incidentes Específicos"):
                                    st.json(dados_processados["especificos"][0])
                
                # Tratamento de erros
                except Exception as e:
                    st.error(f"Erro ao processar o arquivo JSON: {str(e)}")
                    registrar_log(f"Erro no processamento do JSON: {str(e)}", "erro")
                    registrar_log(f"Detalhes do erro: {traceback.format_exc()}", "erro") 