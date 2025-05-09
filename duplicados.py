# duplicados.py

import hashlib
import csv
import datetime
from pathlib import Path
from collections import defaultdict
import tkinter as tk
from tkinter import Toplevel, filedialog, messagebox, ttk

# -------------------------
# 1. Detecção de duplicados
# -------------------------

def hash_arquivo(path: Path, algoritmo: str = 'sha256', bloco: int = 65536) -> str:
    """
    Calcula e retorna o hash do arquivo dado pelo pathlib.Path `path`.
    Usa o algoritmo especificado (por padrão, sha256) e lê em blocos.
    """
    h = hashlib.new(algoritmo)
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(bloco), b''):
            h.update(chunk)
    return h.hexdigest()

def detectar_por_tamanho(arquivos: list[Path]) -> dict[int, list[Path]]:
    """
    Agrupa arquivos por tamanho em bytes e retorna só os grupos com mais de um item.
    """
    grupos = defaultdict(list)
    for f in arquivos:
        try:
            tamanho = f.stat().st_size
            grupos[tamanho].append(f)
        except Exception:
            continue
    return {t: lst for t, lst in grupos.items() if len(lst) > 1}

def detectar_por_hash(grupos_tamanho: dict[int, list[Path]]) -> dict[str, list[Path]]:
    """
    Para cada grupo de arquivos do mesmo tamanho, calcula hashes e
    retorna apenas os hashes com múltiplos arquivos.
    """
    duplicados = defaultdict(list)
    for lst in grupos_tamanho.values():
        hashes = defaultdict(list)
        for f in lst:
            try:
                h = hash_arquivo(f)
                hashes[h].append(f)
            except Exception:
                continue
        for h, files in hashes.items():
            if len(files) > 1:
                duplicados[h] = files
    return duplicados

def identificar_duplicados(diretorio_origem: str) -> dict[str, list[Path]]:
    """
    Retorna um dict {hash: [Path1, Path2, ...]} para arquivos duplicados.
    """
    base = Path(diretorio_origem)
    arquivos = [p for p in base.rglob('*') if p.is_file()]
    grupos_tam = detectar_por_tamanho(arquivos)
    return detectar_por_hash(grupos_tam)

# -------------------------
# 2. Geração de CSV Estruturado
# -------------------------

def exportar_csv(duplicados: dict[str, list[Path]], arquivo_csv: str):
    """
    Gera um CSV com colunas:
      hash, arquivo, tamanho_bytes, data_modificacao, data_criacao, anomalia
    """
    with open(arquivo_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Cabeçalho estruturado
        writer.writerow([
            "hash",
            "arquivo",
            "tamanho_bytes",
            "data_modificacao",
            "data_criacao",
            "anomalia"
        ])
        for h, paths in duplicados.items():
            for p in paths:
                try:
                    st = p.stat()
                    tamanho = st.st_size
                    mtime = datetime.datetime.fromtimestamp(st.st_mtime)
                    ctime = datetime.datetime.fromtimestamp(st.st_ctime)
                    anomalia = "SIM" if mtime < ctime else "NÃO"
                    mod_str = mtime.strftime("%Y-%m-%d %H:%M:%S")
                    cri_str = ctime.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    tamanho = ''
                    mod_str = ''
                    cri_str = ''
                    anomalia = ''
                writer.writerow([h, str(p), tamanho, mod_str, cri_str, anomalia])

# -------------------------
# 3. Interface Tkinter
# -------------------------

def exibir_duplicados(diretorio_origem: str, parent: tk.Tk | Toplevel = None):
    """
    Abre uma janela listando duplicados num Treeview e permite exportar CSV.
    """
    dup = identificar_duplicados(diretorio_origem)
    if not dup:
        messagebox.showinfo("Duplicados", "Nenhum arquivo duplicado encontrado.")
        return

    janela = Toplevel(parent)
    janela.title("Duplicados encontrados")
    janela.geometry("900x500")

    cols = ("hash", "arquivo", "tamanho", "modificacao", "criacao", "anomalia")
    tree = ttk.Treeview(janela, columns=cols, show="headings")
    tree.heading("hash",        text="Hash")
    tree.heading("arquivo",     text="Caminho do arquivo")
    tree.heading("tamanho",     text="Tamanho (bytes)")
    tree.heading("modificacao", text="Modificação")
    tree.heading("criacao",     text="Criação")
    tree.heading("anomalia",    text="Anômalo?")
    tree.column("hash",        width=200)
    tree.column("arquivo",     width=450)
    tree.column("tamanho",     width=100, anchor="e")
    tree.column("modificacao", width=120)
    tree.column("criacao",     width=120)
    tree.column("anomalia",    width=80, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=(10,0))

    # Popular Treeview
    for h, paths in dup.items():
        for p in paths:
            try:
                st = p.stat()
                tamanho = st.st_size
                mtime = datetime.datetime.fromtimestamp(st.st_mtime)
                ctime = datetime.datetime.fromtimestamp(st.st_ctime)
                anomalia = "SIM" if mtime < ctime else "NÃO"
                mod_str = mtime.strftime("%Y-%m-%d %H:%M:%S")
                cri_str = ctime.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                tamanho = ''
                mod_str = ''
                cri_str = ''
                anomalia = ''
            tree.insert("", "end", values=(h, str(p), tamanho, mod_str, cri_str, anomalia))

    # Botão de exportação
    frame_btn = tk.Frame(janela)
    frame_btn.pack(fill="x", pady=10, padx=10)

    def salvar():
        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Salvar relatório de duplicados"
        )
        if caminho:
            exportar_csv(dup, caminho)
            messagebox.showinfo("Exportado", f"Relatório salvo em:\n{caminho}")

    btn_export = tk.Button(frame_btn, text="Exportar para CSV", command=salvar)
    btn_export.pack(side="right")

    return janela

# -------------------------
# 4. Função principal
# -------------------------

def main(diretorio_origem: str, parent: tk.Tk | Toplevel = None):
    """
    Core: identifica e exibe duplicados. Pode ser chamada diretamente
    por formulário.py com:
        duplicados.main(origem, root)
    """
    exibir_duplicados(diretorio_origem, parent)
