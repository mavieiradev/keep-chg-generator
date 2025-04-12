import pandas as pd
import tabula
import re
from logger import registrar_log

def extrair_tabelas_pdf(arquivo_pdf):
    """Extrai tabelas de PDF usando tabula-py"""
    try:
        dfs = tabula.read_pdf(
            arquivo_pdf,
            pages='all',
            multiple_tables=True,
            lattice=True,
            pandas_options={'header': None}
        )
        
        if not dfs:
            raise ValueError("Nenhuma tabela encontrada no PDF")
            
        # Processar tabelas
        dfs_processados = []
        for df in dfs:
            # Remover colunas vazias
            df = df.dropna(axis=1, how='all')
            
            # Identificar cabeçalho
            header_row = df.iloc[0].fillna('').astype(str).str.contains('Número', case=False)
            if header_row.any():
                df.columns = df.iloc[0]
                df = df[1:]
                
            dfs_processados.append(df)
        
        return pd.concat(dfs_processados, ignore_index=True)
        
    except Exception as e:
        registrar_log(f"Erro na extração do PDF: {str(e)}", "erro")
        raise

def limpar_numero_chg(numero):
    """Padroniza o formato do número da CHG"""
    if pd.isna(numero):
        return None
    return re.sub(r'\D', '', str(numero)).strip()

def comparar_chgs(arquivo_principal, arquivo_pdf):
    """
    Compara CHGs entre arquivo principal (XLSX) e PDF do email
    """
    try:
        # Processar arquivo principal
        df_principal = pd.read_excel(arquivo_principal)
        df_principal['Número'] = df_principal['Número'].apply(limpar_numero_chg)
        
        # Extrair dados do PDF
        df_email = extrair_tabelas_pdf(arquivo_pdf)
        df_email['Número'] = df_email['Número'].apply(limpar_numero_chg)
        
        # Validar colunas
        if 'Número' not in df_email.columns:
            raise ValueError("PDF não contém coluna 'Número'")
            
        # Identificar diferenças
        nums_principal = set(df_principal['Número'].dropna())
        nums_email = set(df_email['Número'].dropna())
        
        chgs_novas = df_email[~df_email['Número'].isin(nums_principal)]
        chgs_faltantes = df_principal[~df_principal['Número'].isin(nums_email)]
        chgs_comuns = df_principal[df_principal['Número'].isin(nums_email)]
        
        registrar_log(f"CHGs novas: {len(chgs_novas)}", "info")
        registrar_log(f"CHGs faltantes: {len(chgs_faltantes)}", "info")
        registrar_log(f"CHGs comuns: {len(chgs_comuns)}", "info")
        
        return chgs_novas, chgs_faltantes, chgs_comuns
        
    except Exception as e:
        registrar_log(f"Erro na comparação: {str(e)}", "erro")
        raise 