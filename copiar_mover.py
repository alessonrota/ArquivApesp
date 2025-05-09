import csv
import datetime
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

def listar_arquivos(diretorio_origem):
    """Lista todos os arquivos em um diretório recursivamente."""
    diretorio_origem = Path(diretorio_origem)
    return [arquivo for arquivo in diretorio_origem.rglob('*') if arquivo.is_file()]

def salvar_csv(dados_csv, nome_csv):
    """Salva os dados no arquivo CSV."""
    with open(nome_csv, mode='w', newline='', encoding='utf-8') as arquivo:
        csv.writer(arquivo).writerows(dados_csv)

def salvar_erro(mensagem):
    """Salva os erros no arquivo erro.txt."""
    with open("erro.txt", mode='a', encoding='utf-8') as arquivo:
        arquivo.write(f"{mensagem} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def gerar_nomes_logs(dados):
    """
    Gera os nomes personalizados dos arquivos de log a partir do dicionário de dados.
    Exemplo de saída: 'parâmetro_br-spiiep_informar_A.csv'
    """
    # Extraindo e processando os valores do formulário
    pais = dados.get('BR', '').lower()[0:2]             # Ex: "Brasil" -> "br"
    uf = dados.get('SP', '').split()[0].lower()           # Espera-se que seja abreviação, ex: "sp"
    repo = dados.get('IIEP', '').split()[0].lower()         # Ex: "IIEP" -> "iiep"
    conjunto = dados.get('INF', '').split()[0].lower()      # Ex: "InFormar" -> "informar"
    # Para o campo "tipo", usaremos uma constante "A" (pode ser alterada conforme necessário)
    tipo = "A"
    
    identificador = f"{pais}-{uf}{repo}_{conjunto}_{tipo}"
    return {
        "parametro": f"parâmetro_{identificador}.csv",
        "log_parametro": f"logParâmetro_{identificador}.csv",
        "log_copy": f"logCopy_{identificador}.csv",
        "log_move": f"logMov_{identificador}.csv"
    }

def gerar_parametro_csv(arquivos, diretorio_destino, usuario, dados):
    """
    Gera os parâmetros da operação e salva arquivos CSV com logs.
    Os dados adicionais (país, lugar, etc.) são extraídos do dicionário 'dados'.
    """
    diretorio_destino = Path(diretorio_destino)
    dados_csv = [["ORIGEM", "NOME_ARQUIVO", "DESTINO"]]
    now = datetime.datetime.now()
    
    # Mapeamento dos campos para o log (ajuste conforme a necessidade)
    pais = dados.get('BR', '')
    lugar = dados.get('SP', '')
    acervo = dados.get('IIEP', '')
    suporte = dados.get('INF', '')
    caracteristica = dados.get('EDUPOP', '')
    original = "A"  # Valor fixo; você pode ajustar ou extrair de outro campo do dicionário
    
    log_csv = [["PGR_NOME", "CMD_INFO", "ARQ_FONTE", "LIN_ATUAL", "LIN_TOTAL", 
                "OBJ_TIPO", "OBJ_INFO", "CMD_DATA", "CMD_HORA", "RESP_NOME", 
                "PAIS", "LUGAR", "ACERVO", "SUPORTE", "CARACTERISTICA", "ORIGINAL"]]
    
    for idx, caminho_origem in enumerate(arquivos, start=1):
        nome_arquivo = caminho_origem.name
        caminho_destino = diretorio_destino / nome_arquivo
        dados_csv.append([str(caminho_origem.parent), nome_arquivo, str(diretorio_destino)])
        log_csv.append([
            "Programa PADA N020 v. 1.1", "Gerar Parâmetro", str(caminho_origem), idx, len(arquivos),
            "Arquivo", "Processado", now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), usuario,
            pais, lugar, acervo, suporte, caracteristica, original
        ])
    
    nomes_logs = gerar_nomes_logs(dados)
    salvar_csv(dados_csv, nomes_logs["parametro"])
    salvar_csv(log_csv, nomes_logs["log_parametro"])
    return nomes_logs["parametro"]

def copiar_arquivos(parametro_csv, log_copy):
    """Copia arquivos conforme os parâmetros definidos no CSV."""
    log_data = [["ORIGEM", "DESTINO", "DATA", "HORA", "STATUS"]]
    
    try:
        with open(parametro_csv, mode='r', encoding='utf-8') as arquivo:
            leitor_csv = csv.reader(arquivo)
            next(leitor_csv)
            for linha in leitor_csv:
                origem = Path(linha[0]) / linha[1]
                destino = Path(linha[2]) / linha[1]
                
                if origem.exists():
                    shutil.copy2(origem, destino)
                    log_data.append([
                        str(origem), str(destino),
                        datetime.datetime.now().strftime("%Y-%m-%d"),
                        datetime.datetime.now().strftime("%H:%M:%S"),
                        "Sucesso"
                    ])
                else:
                    salvar_erro(f"Erro: Arquivo não encontrado {origem}")
    except Exception as e:
        salvar_erro(f"Erro ao copiar arquivos: {e}")
    
    salvar_csv(log_data, log_copy)

def mover_arquivos(parametro_csv, log_move):
    """Move arquivos conforme os parâmetros definidos no CSV."""
    log_data = [["ORIGEM", "DESTINO", "DATA", "HORA", "STATUS"]]
    
    try:
        with open(parametro_csv, mode='r', encoding='utf-8') as arquivo:
            leitor_csv = csv.reader(arquivo)
            next(leitor_csv)
            for linha in leitor_csv:
                origem = Path(linha[0]) / linha[1]
                destino = Path(linha[2]) / linha[1]
                
                if origem.exists():
                    shutil.move(str(origem), str(destino))
                    log_data.append([
                        str(origem), str(destino),
                        datetime.datetime.now().strftime("%Y-%m-%d"),
                        datetime.datetime.now().strftime("%H:%M:%S"),
                        "Sucesso"
                    ])
                else:
                    salvar_erro(f"Erro: Arquivo não encontrado {origem}")
    except Exception as e:
        salvar_erro(f"Erro ao mover arquivos: {e}")
    
    salvar_csv(log_data, log_move)

def escolher_acao():
    """Cria uma janela para escolher entre Copiar, Mover ou Cancelar."""
    escolha = {"valor": None}  # Variável para armazenar a escolha do usuário
    
    def definir_escolha(valor):
        escolha["valor"] = valor
        dialog.destroy()

    dialog = tk.Toplevel()
    dialog.title("Escolha uma ação")
    dialog.geometry("350x180")
    dialog.resizable(False, False)
    dialog.grab_set()  # Bloqueia interação com a janela principal

    label = tk.Label(dialog, text="O que deseja fazer com os arquivos?", font=("Arial", 11, "bold"))
    label.pack(pady=10)

    btn_copiar = tk.Button(dialog, text="Copiar", width=12, bg="#28A745", fg="white", 
                           font=("Arial", 10, "bold"), command=lambda: definir_escolha("copiar"))
    btn_copiar.pack(pady=5)

    btn_mover = tk.Button(dialog, text="Mover", width=12, bg="#007BFF", fg="white", 
                          font=("Arial", 10, "bold"), command=lambda: definir_escolha("mover"))
    btn_mover.pack(pady=5)

    btn_cancelar = tk.Button(dialog, text="Cancelar", width=12, bg="#DC3545", fg="white", 
                             font=("Arial", 10, "bold"), command=lambda: definir_escolha("cancelar"))
    btn_cancelar.pack(pady=5)

    dialog.wait_window()  # Aguarda até que o usuário faça uma escolha
    return escolha["valor"]

def main(dados, diretorio_origem, diretorio_destino):
    """
    Permite escolher entre copiar ou mover os arquivos e gera logs.
    'dados' é um dicionário com as informações do formulário.
    """
    arquivos = listar_arquivos(diretorio_origem)
    
    if not arquivos:
        messagebox.showerror("Erro", "Nenhum arquivo encontrado no diretório de origem.")
        return
    
    nomes_logs = gerar_nomes_logs(dados)
    parametro_csv = gerar_parametro_csv(arquivos, diretorio_destino, dados.get('usuario', ''), dados)
    
    escolha = escolher_acao()

    if escolha == "cancelar":
        messagebox.showinfo("Cancelado", "Operação cancelada pelo usuário.")
        return
    elif escolha == "copiar":
        copiar_arquivos(parametro_csv, nomes_logs["log_copy"])
        messagebox.showinfo("Sucesso", "Arquivos copiados com sucesso!")
    elif escolha == "mover":
        mover_arquivos(parametro_csv, nomes_logs["log_move"])
        messagebox.showinfo("Sucesso", "Arquivos movidos com sucesso!")
