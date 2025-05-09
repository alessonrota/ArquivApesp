import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import datetime
import copiar_mover
import renomeacao
import conversao
import verificacao_integridade
from pathlib import Path
import duplicados

# =========================================
# 1. Função para registrar ações do usuário (log global)
# =========================================
def registrar_evento_global(descricao):
    """
    Registra eventos de interface (cliques, escolhas) em um CSV geral.
    Exemplo de linha: Data, Hora, Ação
    """
    log_path = Path("logGeralSistema.csv")
    existe = log_path.exists()

    with log_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["Data", "Hora", "Ação"])
        agora = datetime.datetime.now()
        writer.writerow([
            agora.strftime("%Y-%m-%d"),
            agora.strftime("%H:%M:%S"),
            descricao
        ])

# =========================================
# 2. Campos do formulário
# =========================================
FORM_FIELDS = [
    {
        "section": "Área de identificação do repositório",
        "fields": [
            {"code": "BR",            "label": "País",           "default": "Br"},
            {"code": "SP",            "label": "UF",              "default": "Sp"},
            {"code": "Repositório",   "label": "Repositório",    "default": "DIG"},
        ],
    },
    {
        "section": "Área de identificação do conjunto documental",
        "fields": [
            {"code": "Fundo",        "label": "Fundo",          "default": "Imigrantes"},
            {"code": "Subconjunto",  "label": "Subconjunto",    "default": "Subconjunto"},
        ],
    },
    {
        "section": "Área de caracterização da unidade de descrição",
        "fields": [
            {"code": "Gênero",        "label": "Gênero documental", "default": "ICO"},
            {"code": "Espécie/Tipo",  "label": "Espécie/Tipo",       "default": "FOT"},
            {"code": "Dispositivo",   "label": "Técnica de registro","default": "FOT"},
            {"code": "Ação",          "label": "Forma documental",   "default": "Copia"},
        ],
    },
    {
        "section": "Dados do usuário",
        "fields": [
            {"code": "USR", "label": "Usuário", "default": "Fulano"}
        ]
    },
]

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ArquivAPESP")
        self.root.geometry("650x600")
        self.root.configure(bg="#f0f0f0")
        self.entradas = {}
        self.criar_formulario()

    def criar_formulario(self):
        """Cria o formulário inicial com base em FORM_FIELDS."""
        self.frame_formulario = tk.Frame(
            self.root, bg="#ffffff", padx=10, pady=10, relief="ridge", bd=2
        )
        self.frame_formulario.pack(pady=10, padx=10, fill="both", expand=True)

        tk.Label(
            self.frame_formulario,
            text="Preencha os dados do formulário:",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
        ).pack(pady=5)

        for section in FORM_FIELDS:
            frame_sec = tk.Frame(self.frame_formulario, bg="#dddddd", padx=5, pady=5)
            frame_sec.pack(fill="x", pady=(10,5))
            tk.Label(
                frame_sec,
                text=section["section"],
                font=("Arial", 11, "bold"),
                bg="#dddddd",
            ).pack(anchor="w")
            for field in section["fields"]:
                code = field["code"]
                label = field["label"]
                default = field["default"]
                fr = tk.Frame(frame_sec, bg="#ffffff")
                fr.pack(fill="x", padx=5, pady=3)
                tk.Label(fr, text=code, width=10, anchor="w", bg="#ffffff").pack(side="left")
                tk.Label(fr, text=label, width=35, anchor="w", bg="#ffffff").pack(side="left")
                ent = tk.Entry(fr, width=30)
                ent.insert(0, default)
                ent.pack(side="left")
                self.entradas[code] = ent

        tk.Button(
            self.frame_formulario,
            text="Prosseguir",
            font=("Arial", 10, "bold"),
            bg="#007BFF",
            fg="white",
            command=self.mostrar_menu
        ).pack(pady=10)

    def mostrar_menu(self):
        """Exibe o menu principal e oculta o formulário."""
        self.frame_formulario.pack_forget()
        self.frame_menu = tk.Frame(
            self.root, bg="#ffffff", padx=10, pady=10, relief="ridge", bd=2
        )
        self.frame_menu.pack(pady=10, padx=10, fill="both", expand=True)

        tk.Label(
            self.frame_menu,
            text="Escolha uma opção:",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
        ).pack(pady=5)

        opcoes = [
            ("1 - Cópia/Mover Arquivos", self.executar_copiar),
            ("2 - Conversão", self.executar_conversao),
            ("3 - Renomeação", self.executar_renomeacao),
            ("4 - Verificação de Integridade", self.executar_verificacao_integridade),
            ("5 - Verificar Duplicados", self.executar_duplicados),
        ]

        for texto, cmd in opcoes:
            tk.Button(
                self.frame_menu,
                text=texto,
                font=("Arial",10),
                width=30,
                bg="#28A745",
                fg="white",
                command=cmd
            ).pack(pady=5)

        tk.Button(
            self.frame_menu,
            text="Voltar ao Formulário",
            font=("Arial",10),
            bg="#FFC107",
            command=self.reiniciar_interface
        ).pack(pady=5)

        tk.Button(
            self.frame_menu,
            text="Sair",
            font=("Arial",10,"bold"),
            bg="#DC3545",
            fg="white",
            command=self.root.quit
        ).pack(pady=10)

    def reiniciar_interface(self):
        """Retorna ao formulário inicial."""
        self.frame_menu.pack_forget()
        self.criar_formulario()

    def obter_dados_formulario(self):
        """Coleta e valida os dados do formulário."""
        dados = {}
        for code, widget in self.entradas.items():
            val = widget.get().strip()
            if not val:
                messagebox.showwarning("Aviso", f"O campo {code} não pode ficar vazio.")
                return None
            dados[code] = val
        return dados

    def executar_copiar(self):
        dados = self.obter_dados_formulario()
        if not dados:
            return
        registrar_evento_global("Usuário clicou em 'Cópia/Mover Arquivos'")
        copiar_mover.main(dados)

    def executar_conversao(self):
        dados = self.obter_dados_formulario()
        if not dados:
            return
        registrar_evento_global("Usuário clicou em 'Conversão'")
        conversao.main(dados)

    def executar_renomeacao(self):
        dados = self.obter_dados_formulario()
        if not dados:
            return
        registrar_evento_global("Usuário clicou em 'Renomeação'")
        renomeacao.main(dados)

    def executar_verificacao_integridade(self):
        dados = self.obter_dados_formulario()
        if not dados:
            return
        registrar_evento_global("Usuário clicou em 'Verificação de Integridade'")
        verificacao_integridade.executar_verificacao(dados)

    def executar_duplicados(self):
        """Executa detecção de arquivos duplicados."""
        dados = self.obter_dados_formulario()
        if not dados:
            return
        registrar_evento_global("Usuário clicou em 'Verificar Duplicados'")
        origem = filedialog.askdirectory(
            title="Selecione o diretório para verificar duplicados"
        )
        if not origem:
            messagebox.showwarning("Aviso", "Selecione o diretório corretamente.")
            return
        # Chama o módulo duplicados, passando a janela pai
        duplicados.main(origem, self.root)


def iniciar_interface():
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()

if __name__ == "__main__":
    iniciar_interface()
