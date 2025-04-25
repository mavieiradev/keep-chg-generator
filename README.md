# Gerador de Relatório de Incidentes QD APPs

Este script Python processa dados JSON de incidentes e gera um relatório formatado seguindo um padrão específico de "keep".

## Funcionalidades

- Processa dados JSON com registros de incidentes
- Categoriza os incidentes por prioridade
- Extrai informações de funcionalidades e responsáveis
- Gera um relatório no formato solicitado
- Salva o relatório em um arquivo texto

## Requisitos

- Python 3.6 ou superior

## Como Usar

### Passando um arquivo JSON como argumento

```bash
python gera_relatorio.py exemplo.json
```

### Inserindo o JSON manualmente

```bash
python gera_relatorio.py
```
O script solicitará que você cole o JSON de incidentes.

## Formato do Relatório

O relatório gerado segue o seguinte formato:

```
*Relatório de Incidentes QD APPs*

*Período:* xx/xx/xxxx – 07h as 19h

*1. Incidentes Críticos*
* *Quantidade:* X
* *Funcionalidade:* Lista de funcionalidades
* *Responsáveis:* Lista de responsáveis

*2. Incidentes Altos*
...

*3. Incidentes Específicos*
...

*4- Incidentes VIPS*
...

*Observações*

Att.
Qd Spread
```

## Categorização de Incidentes

- **Incidentes Críticos**: Prioridade 3
- **Incidentes Altos**: Prioridade 4 (assumido)
- **Incidentes Específicos**: Prioridade 5
- **Incidentes VIPS**: Identificados por menção a "VIP" na descrição (assumido)

## Exemplo

Um exemplo de JSON está disponível no arquivo `exemplo.json`.
