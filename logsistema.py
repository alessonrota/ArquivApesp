import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import datetime
import copiar_mover
import renomeacao
import conversao
import verificacao_integridade
from pathlib import Path

# =========================================
# 1. Função para registrar ações do usuário (log global)
#    -> Se tiver um arquivo logsistema.py, você pode mover esta função para lá
#       e importar aqui em vez de defini-la localmente.
# =========================================
def registrar_evento_global(descricao):
    """
    Registra eventos de interface (cliques, escolhas) em um CSV geral.
    Exemplo de linha: Data, Hora, DescriçãoDaAção
    """
    log_path = Path("logGeralSistema.csv")
    existe = log_path.exists()

    # Abre em modo append para continuar escrevendo no final do arquivo
    with log_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Se o arquivo ainda não existia, escreve o cabeçalho
        if not existe:
            writer.writerow(["Data", "Hora", "Ação"])

        data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
        hora_atual = datetime.datetime.now().strftime("%H:%M:%S")
        writer.writerow([data_atual, hora_atual, descricao])

# =========================================
# 2. Campos do formulário
# =========================================
FORM_FIELDS = [
    {
        "section": "Área de identificação do repositório",
        "fields": [
            {"code": "BR", "label": "Campo de localização do repositório (país)", "default": "Br"},
            {"code": "SP", "label": "Campo de localização do repositório (UF)",   "default": "Sp"},
            {"code": "Repositório", "label": "Campo de designação do repositório", "default": "DIG"},
        ],
    },
    {
        "section": "Área de identificação do conjunto documental",
        "fields": [
            {"code": "Fundo",       "label": "Campo de id. do conjunto documental",    "default": "Imigrantes"},
            {"code": "Subconjunto", "label": "Campo de id. do subconjunto documental", "default": "Subconjunto"},
        ],
    },
    {
        "section": "Área de caracterização da unid. de descrição",
        "fields": [
            {"code": "Gênero",       "label": "Campo de caract. de gênero documental",  "default": "ICO"},
            {"code": "Espécie/Tipo", "label": "Campo de caract. de espécie documental", "default": "FOT"},
            {"code": "Dispositivo",  "label": "Campo de caract. de técnica de registro","default": "FOT"},
            {"code": "Ação",         "label": "Campo de caract. de forma documental",   "default": "Copia"},
        ],
    },
    # Nova seção para "Dados do usuário"
    {
        "section": "Dados do usuário",
        "fields": [
            {"code": "USR", "label": "Digite seu nome de usuário", "default": "Fulano"}
        ]
    },
]

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ArquivAPESP")
        self.root.geometry("650x600")
        self.root.configure(bg="#f0f0f0")

        # Dicionário que guardará as entradas dos campos (tk.Entry)
        self.entradas = {}

        self.criar_formulario()

    def criar_formulario(self):
        """Cria e organiza o formulário inicial com base em FORM_FIELDS."""
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

        # Monta cada seção
        for section_data in FORM_FIELDS:
            section_label = section_data["section"]
            frame_section = tk.Frame(self.frame_formulario, bg="#dddddd", padx=5, pady=5)
            frame_section.pack(fill="x", pady=(10, 5))

            tk.Label(
                frame_section,
                text=section_label,
                font=("Arial", 11, "bold"),
                bg="#dddddd",
            ).pack(anchor="w")

            # Para cada campo dentro da seção
            for field_info in section_data["fields"]:
                code = field_info["code"]
                label = field_info["label"]
                default_val = field_info["default"]

                field_frame = tk.Frame(frame_section, bg="#ffffff")
                field_frame.pack(fill="x", padx=5, pady=3)

                tk.Label(field_frame, text=code, bg="#ffffff", width=5, anchor="w").pack(side="left", padx=(0, 5))
                tk.Label(field_frame, text=label, bg="#ffffff", width=40, anchor="w").pack(side="left", padx=(0, 5))

                entry_val = tk.Entry(field_frame, width=40)
                entry_val.insert(0, default_val)
                entry_val.pack(side="left", padx=(0, 5))

                self.entradas[code] = entry_val

        # Botão para prosseguir ao menu
        tk.Button(
            self.frame_formulario,
            text="Prosseguir",
            font=("Arial", 10, "bold"),
            bg="#007BFF",
            fg="white",
            command=self.mostrar_menu
        ).pack(pady=10)

    def mostrar_menu(self):
        """Exibe o menu principal e oculta o formulário inicial."""
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
        ]

        for texto, comando in opcoes:
            tk.Button(
                self.frame_menu,
                text=texto,
                font=("Arial", 10),
                width=30,
                bg="#28A745",
                fg="white",
                command=comando
            ).pack(pady=5)

        tk.Button(
            self.frame_menu,
            text="Voltar ao Formulário",
            font=("Arial", 10),
            bg="#FFC107",
            command=self.reiniciar_interface
        ).pack(pady=5)

        tk.Button(
            self.frame_menu,
            text="Sair",
            font=("Arial", 10, "bold"),
            bg="#DC3545",
            fg="white",
            command=self.root.quit
        ).pack(pady=10)

    def reiniciar_interface(self):
        """Reinicia a interface para o formulário inicial."""
        self.frame_menu.pack_forget()
        self.criar_formulario()

    def obter_dados_formulario(self):
        """
        Lê cada campo do dicionário self.entradas e retorna um dicionário
        no formato { "BR": "...", "SP": "...", "USR": "...", etc. }.
        """
        dados = {}
        for code, entry_widget in self.entradas.items():
            valor = entry_widget.get().strip()
            if not valor:
                messagebox.showwarning("Aviso", f"O campo {code} não pode ficar vazio.")
                return None
            dados[code] = valor
        return dados

    # ================================================
    # 3. Métodos que chamam os módulos + registram log
    # ================================================
    def executar_copiar(self):
        """Executa a função de cópia/movimentação de arquivos."""
        dados = self.obter_dados_formulario()
        if not dados:
            return

        # Log no CSV Geral de interface
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
        """Chama a verificação de integridade, passando os dados do formulário."""
        dados = self.obter_dados_formulario()
        if not dados:
            return

        registrar_evento_global("Usuário clicou em 'Verificação de Integridade'")
        verificacao_integridade.executar_verificacao(dados)

def iniciar_interface():
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()

if __name__ == "__main__":
    iniciar_interface()
