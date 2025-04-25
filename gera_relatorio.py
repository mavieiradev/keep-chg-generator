import json
import datetime
import sys
import re
from collections import defaultdict

def formatar_periodo(data_personalizada=None):
    """
    Retorna o período no formato DD/MM/YYYY - 07h as 19h.
    
    Args:
        data_personalizada (datetime.date, opcional): Data personalizada para o relatório.
            Se None, usa a data atual.
    
    Returns:
        str: O período formatado.
    """
    if data_personalizada:
        # Se recebermos uma data específica, usamos ela
        if isinstance(data_personalizada, str):
            # Tenta converter string para data
            try:
                data_personalizada = datetime.datetime.strptime(data_personalizada, '%Y-%m-%d').date()
            except ValueError:
                # Se falhar, usa a data atual
                data_personalizada = datetime.datetime.now().date()
        
        # Se for um objeto date, converte para datetime para ter acesso aos atributos day, month, year
        if isinstance(data_personalizada, datetime.date) and not isinstance(data_personalizada, datetime.datetime):
            hoje = datetime.datetime.combine(data_personalizada, datetime.time())
        else:
            hoje = data_personalizada
    else:
        # Caso contrário, usa a data atual
        hoje = datetime.datetime.now()
    
    return f"{hoje.day:02d}/{hoje.month:02d}/{hoje.year} – 07h as 19h"

def extrair_funcionalidade(incident):
    """
    Extrai a funcionalidade do incidente a partir da short_description ou 
    da descrição detalhada. Tenta identificar o contexto principal do incidente.
    """
    funcionalidade = ""
    
    # Primeiro tenta usar short_description
    if "short_description" in incident and incident["short_description"]:
        funcionalidade = incident["short_description"]
    
    # Se não tiver short_description, busca na descrição
    elif "description" in incident and incident["description"]:
        # Busca por padrões comuns na descrição
        desc = incident["description"]
        # Procura por frases que começam com "Descrição:" ou "Detalhe da Falha:"
        match = re.search(r'Descrição:(.+?)(?:\r\n|\n|$)', desc)
        if match:
            funcionalidade = match.group(1).strip()
        else:
            # Pega as primeiras 70 caracteres da descrição
            funcionalidade = desc.split('\r\n', 1)[0] if '\r\n' in desc else desc[:70]
    
    return funcionalidade.strip() or "Não especificado"

def extrair_responsavel(incident):
    """
    Define o responsável como "QD Sustentação" conforme solicitado.
    """
    # Retorna o responsável fixo conforme solicitação
    return "QD Sustentação"

def processar_json(json_data):
    """
    Processa os dados JSON e retorna as informações agrupadas por tipo de incidente.
    Categoriza os incidentes de acordo com sua prioridade.
    """
    incidents = json_data.get("records", [])
    
    # Dicionários para armazenar dados por categoria
    criticos = []
    altos = []
    especificos = []
    vips = []
    
    # Categorizar incidentes
    for incident in incidents:
        priority = incident.get("priority")
        
        # Verifica se é um incidente VIP primeiro (independente da prioridade)
        is_vip = False
        if "vip" in incident.get("description", "").lower() or "vip" in incident.get("short_description", "").lower():
            vips.append(incident)
            is_vip = True
        
        # Se não for VIP, categoriza pela prioridade
        if not is_vip:
            if priority == "3":  # Incidentes Críticos
                criticos.append(incident)
            elif priority == "4":  # Incidentes Altos
                altos.append(incident)
            elif priority == "5":  # Incidentes Específicos
                especificos.append(incident)
    
    return {
        "criticos": criticos,
        "altos": altos,
        "especificos": especificos,
        "vips": vips
    }

def formatar_texto(texto, max_length=70):
    """
    Formata o texto para não exceder o comprimento máximo.
    Trunca textos longos e adiciona "..." no final.
    """
    texto = texto.replace('\r\n', ' ').replace('\n', ' ')
    if len(texto) <= max_length:
        return texto
    return texto[:max_length-3] + "..."

def formatar_lista_funcionalidades(incidentes, prefixo=""):
    """
    Formata a lista de funcionalidades incluindo o número do incidente.
    Cada incidente é mostrado em uma nova linha para maior clareza.
    """
    if not incidentes:
        return ""  # Retorna string vazia em vez de "N/A"
    
    # Formata cada incidente como "NÚMERO - FUNCIONALIDADE" em linhas separadas
    itens_formatados = []
    for incidente in incidentes:
        numero = incidente.get("number", "Número Desconhecido")
        funcionalidade = extrair_funcionalidade(incidente)
        item_formatado = f"{numero} - {formatar_texto(funcionalidade)}"
        itens_formatados.append(item_formatado)
    
    # Retorna todos os itens, um por linha
    return "\n    * " + "\n    * ".join(itens_formatados)

def formatar_lista_responsaveis(responsaveis, prefixo=""):
    """
    Formata uma lista de responsáveis para exibição.
    Como temos apenas um responsável fixo, esta função foi simplificada.
    """
    if not responsaveis:
        return ""  # Retorna string vazia em vez de "N/A"
    
    # Como todos os responsáveis são iguais, pegamos apenas o primeiro
    return responsaveis[0] if responsaveis else ""

def formatar_incidentes(incidentes):
    """
    Formata os detalhes dos incidentes para o relatório.
    Inclui quantidade, funcionalidades afetadas e responsáveis.
    """
    if not incidentes:
        return "* *Quantidade:* 0\n* *Funcionalidades:*\n* *Responsáveis:*"  # Remove "N/A"
    
    # Extrai responsáveis
    responsaveis = [extrair_responsavel(inc) for inc in incidentes]
    
    # Formata a saída
    quantidade = f"* *Quantidade:* {len(incidentes)}"
    funcs = f"* *Funcionalidades:* {formatar_lista_funcionalidades(incidentes)}"
    resps = f"* *Responsáveis:* {formatar_lista_responsaveis(responsaveis)}"
    
    return f"{quantidade}\n{funcs}\n{resps}"

def gerar_relatorio(json_data, data_personalizada=None):
    """
    Gera o relatório de incidentes no formato especificado.
    Inclui todas as categorias de incidentes no relatório.
    
    Args:
        json_data (dict): Dados JSON dos incidentes.
        data_personalizada (datetime.date, opcional): Data personalizada para o relatório.
            Se None, usa a data atual.
    
    Returns:
        str: O relatório formatado.
    """
    dados = processar_json(json_data)
    
    relatorio = f"""*Relatório de Incidentes QD APPs*

*Período:* {formatar_periodo(data_personalizada)}

*1. Incidentes Críticos*
{formatar_incidentes(dados["criticos"])}

*2. Incidentes Altos*
{formatar_incidentes(dados["altos"])}

*3. Incidentes Específicos*
{formatar_incidentes(dados["especificos"])}

*4- Incidentes VIPS*
{formatar_incidentes(dados["vips"])}

*Observações*

Att.
Qd Spread
"""
    return relatorio

def main():
    """
    Função principal que processa o arquivo JSON fornecido.
    Aceita o JSON como arquivo ou entrada direta.
    """
    if len(sys.argv) > 1:
        try:
            # Se um arquivo for fornecido como argumento
            with open(sys.argv[1], 'r', encoding='utf-8') as file:
                json_data = json.load(file)
                print(f"Arquivo carregado: {sys.argv[1]}")
        except FileNotFoundError:
            print(f"Erro: O arquivo '{sys.argv[1]}' não foi encontrado.")
            return
        except json.JSONDecodeError:
            print(f"Erro: O arquivo '{sys.argv[1]}' não contém um JSON válido.")
            return
    else:
        # Ler do stdin
        print("Cole o JSON de incidentes (pressione Enter e Ctrl+D quando terminar):")
        json_str = ""
        try:
            while True:
                line = input()
                json_str += line + "\n"
        except EOFError:
            pass
        except KeyboardInterrupt:
            print("\nOperação cancelada pelo usuário.")
            return
        
        try:
            json_data = json.loads(json_str)
        except json.JSONDecodeError:
            print("Erro: O JSON fornecido é inválido.")
            return
    
    # Gera e exibe o relatório
    relatorio = gerar_relatorio(json_data)
    print("\n" + relatorio)
    
    # Salva em um arquivo
    nome_arquivo = "relatorio_incidentes.txt"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(relatorio)
    
    print(f"Relatório salvo em '{nome_arquivo}'")

if __name__ == "__main__":
    main() 