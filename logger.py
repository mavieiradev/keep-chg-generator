import logging
from datetime import datetime
import os

LOG_FILE = "chg_logs.log"

def configurar_logs():
    """Configura o sistema de logs"""
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='a'  # Modo append
    )

def registrar_log(mensagem, nivel="info"):
    """Registra uma entrada de log sem dependências do Streamlit"""
    niveis = {
        "info": logging.INFO,
        "erro": logging.ERROR,
        "alerta": logging.WARNING
    }
    
    logger = logging.getLogger(__name__)
    logger.log(niveis.get(nivel.lower(), logging.INFO), mensagem)