import streamlit as st
import pandas as pd
from datetime import datetime
from pytz import timezone
from io import BytesIO
import traceback
from test_processor import processar_testes, STATUS_VALIDOS_FINAIS
from logger import registrar_log

def render_test_processor_page():
    """
    Renderiza a página de processamento de testes no Streamlit.
    
    Esta função é responsável por:
    1. Criar a interface para upload dos arquivos de teste
    2. Permitir a configuração da data para o relatório
    3. Processar os dados e gerar o arquivo de acompanhamento
    4. Disponibilizar o download do resultado
    """
    # Cabeçalho da página
    st.markdown("""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="color: #1f61d9; margin-bottom: 20px;">📋 Processador de Testes</h2>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        # Descrição da funcionalidade
        st.markdown("""
            <div style="background-color: white; padding: 15px; border-radius: 8px; border-left: 4px solid #1f61d9; margin-bottom: 20px;">
                <p style="margin: 0; font-size: 0.9em;">
                    Integre resultados de testes do caderno diário ao arquivo de acompanhamento. 
                    Esta ferramenta processa os resultados das abas "Caderno App Vivo" e "Caderno Web B2C" e os adiciona à aba "B2C" do arquivo diário.
                </p>
                <p style="margin-top: 10px; font-size: 0.9em;">
                    <strong>Importante:</strong> A ferramenta reconhece automaticamente colunas como "Status", "Status do Teste QD" e processa 
                    registros com status "Passed", "Not Executed" e "Failed" (incluindo variações de maiúsculas/minúsculas).
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Layout em duas colunas
        col1, col2 = st.columns([1, 1])
        
        # Coluna de configurações
        with col1:
            st.subheader("Configurações")
            
            # Opção para personalizar a data
            data_options = ["Usar data atual", "Especificar data"]
            data_selecionada = st.radio("Data para os registros:", data_options)
            
            data_manual = None
            if data_selecionada == "Especificar data":
                data_manual = st.date_input(
                    "Selecione a data:",
                    datetime.now(timezone('America/Sao_Paulo')).date()
                )
                # Converter para formato DD/MM/YYYY
                data_manual = data_manual.strftime('%d/%m/%Y') if data_manual else None
            
            # Exibir informações sobre status válidos
            with st.expander("ℹ️ Informações sobre Status Válidos"):
                st.info(f"""
                    O sistema processa APENAS os seguintes valores de status:
                    - ✅ Passed (aprovado)
                    - ⚠️ Not Executed (não executado)
                    - ❌ Failed (falhou)
                    
                    Outros status serão ignorados no processamento.
                """)
        
        # Coluna de upload
        with col2:
            st.subheader("Upload de Arquivos")
            
            # Upload do caderno de testes
            caderno_file = st.file_uploader(
                "Faça upload do Caderno de Testes (Excel)",
                type=["xlsx"],
                key="caderno_uploader",
                help="Arquivo Excel contendo os testes nas abas 'Caderno App Vivo' e 'Caderno Web B2C'"
            )
            
            # Upload do arquivo diário
            diario_file = st.file_uploader(
                "Faça upload do Arquivo Diário (Excel)",
                type=["xlsx"],
                key="diario_uploader",
                help="Arquivo Excel de acompanhamento diário com a aba 'B2C'"
            )
            
            # Exibir detalhes dos arquivos quando carregados
            if caderno_file and diario_file:
                st.markdown("### Arquivos carregados")
                file_details = {
                    "Caderno de Testes": {
                        "Nome": caderno_file.name, 
                        "Tipo": caderno_file.type, 
                        "Tamanho": f"{caderno_file.size/1024:.2f} KB"
                    },
                    "Arquivo Diário": {
                        "Nome": diario_file.name, 
                        "Tipo": diario_file.type, 
                        "Tamanho": f"{diario_file.size/1024:.2f} KB"
                    }
                }
                st.json(file_details)
        
        # Botão de processamento
        if caderno_file and diario_file:
            if st.button("Processar Arquivos", type="primary", use_container_width=True):
                try:
                    with st.spinner('Processando os arquivos de teste...'):
                        # Chamar a função de processamento
                        resultado, qtd_registros = processar_testes(
                            arquivo_caderno=caderno_file,
                            arquivo_diario=diario_file,
                            data_manual=data_manual
                        )
                        
                        # Feedback de sucesso
                        st.markdown(f"""
                            <div class="success-message">
                                ✅ Processamento concluído com sucesso! {qtd_registros} registro(s) adicionado(s).
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Visualização dos resultados
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.subheader("Resumo")
                            st.markdown(f"""
                                * **Registros processados:** {qtd_registros}
                                * **Abas processadas:** Caderno App Vivo, Caderno Web B2C
                                * **Aba de destino:** B2C
                                * **Data registrada:** {data_manual if data_manual else datetime.now(timezone('America/Sao_Paulo')).strftime('%d/%m/%Y')}
                            """)
                        
                        with col2:
                            # Botão para download do resultado
                            nome_arquivo = diario_file.name.split(".")[0] + "_atualizado.xlsx"
                            st.download_button(
                                "⬇️ Baixar Arquivo Processado",
                                resultado,
                                file_name=nome_arquivo,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                            
                            st.markdown("""
                                <div style="background-color: #e7f3e7; padding: 10px; border-radius: 5px; margin-top: 15px;">
                                    <p style="margin: 0; font-size: 0.9em;">
                                        ℹ️ O arquivo atualizado contém os registros originais mais os novos testes processados.
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"Erro ao processar os arquivos: {str(e)}")
                    registrar_log(f"Erro no processamento de testes: {str(e)}", "erro")
                    registrar_log(f"Detalhes do erro: {traceback.format_exc()}", "erro")
                    
                    # Mostrar mais informações sobre o erro
                    with st.expander("Detalhes do erro"):
                        st.code(traceback.format_exc()) 