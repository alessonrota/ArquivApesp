  # ArquivAPESP – Documentação Técnica e de Uso

> **Versão:** 0.2  |  **Data:** 9 mai 2025  |  **Autor:** Alesson Ramon Rota e colaboradores

---

## Índice
1. [Introdução](#introducao)
2. [Visão Geral do Sistema](#visao-geral)
3. [Instalação e Requisitos](#instalacao)
4. [Estrutura de Pastas do Projeto](#estrutura)
5. [Fluxo de Execução](#fluxo)
6. [Interface Gráfica (Tkinter)](#gui)
7. [Campos do Formulário Modular](#campos)
8. [Convenção de Nomes](#convencao)
9. [Módulos e Funções](#modulos)
10. [Arquivos de Log e Relatórios CSV](#logs)
11. [Tratamento de Erros](#erros)
12. [Empacotamento com PyInstaller](#pyinstaller)
13. [Extensibilidade | Como adicionar novas operações](#extensibilidade)
14. [Roadmap & TODO](#roadmap)
15. [Licença](#licenca)
16. [Agradecimentos](#agradecimentos)

---
<a name="introducao"></a>
## 1. Introdução
O **ArquivAPESP** é uma aplicação desktop (Python 3) orientada à gestão de acervos digitais. Ela executa operações recorrentes no fluxo de preservação: **cópia/movimentação**, **conversão** de formatos, **renomeação** institucional e **verificação de integridade**.  
O usuário preenche um formulário modular inspirado em normas arquivísticas (ICA‑ATOM/ISAD‑G), que alimenta os padrões de nomenclatura dos arquivos processados e dos logs gerados.

> **Objetivo principal**: reduzir erros humanos, garantir rastreabilidade e manter coerência na estrutura de pastas/nomeação de objetos digitais.

<a name="visao-geral"></a>
## 2. Visão Geral do Sistema
![Diagrama de Alto Nível](diagrama_alto_nivel.png)

| Camada | Responsabilidade | Módulos |
|--------|------------------|---------|
| **Apresentação** | Interface Tkinter; coleta de parâmetros | `formulario.py` |
| **Aplicação** | Lógica de cada operação | `copiar_mover.py`, `conversao.py`, `renomeacao.py`, `verificacao_integridade.py` |
| **Persistência** | Geração de CSV, logs, gravação de erros | Funções utilitárias em cada módulo |

<a name="instalacao"></a>
## 3. Instalação e Requisitos
### 3.1. Dependências
```bash
Python >= 3.9
pip install -r requirements.txt
```
`requirements.txt`
```text
tkinter              # GUI (já incluso em CPython padrão)
pillow               # manipulação de imagens (conversão)
pikepdf              # se a verificação de PDF for utilizada
```
### 3.2. Clonar e executar
```bash
git clone https://github.com/apesp/arquivapesp.git
cd arquivapesp
python formulario.py
```

<a name="estrutura"></a>
## 4. Estrutura de Pastas do Projeto
```text
arquivapesp/
│  formulario.py          # GUI principal
│  copiar_mover.py        # Operações de cópia/mover
│  renomeacao.py          # Renomeação baseada no formulário
│  conversao.py           # Conversão de formatos (ex.: JPG → PDF)
│  verificacao_integridade.py # Checksums, tamanho, etc.
│  utils.py               # Auxiliares (opcional)
│
├─ logs/                  # Armazena CSVs e .txt de erro
├─ docs/                  # Esta documentação, diagramas, tutoriais
└─ dist/                  # Binários gerados pelo PyInstaller
```

<a name="fluxo"></a>
## 5. Fluxo de Execução
1. **Usuário inicia** `formulario.py`.
2. Preenche **formulário modular** com metadados arquivísticos.
3. Escolhe a operação (cópia, conversão, renomeação, verificação).
4. O módulo correspondente recebe o **dicionário `dados`** com todos os campos.
5. O módulo gera **CSV de parâmetros** e executa a tarefa.
6. Logs são salvos em `logs/` (nomes derivados de `dados`).
7. Mensagens de sucesso/erro são exibidas via `messagebox`.

<a name="gui"></a>
## 6. Interface Gráfica (Tkinter)
### 6.1. Janela de Formulário
- Cada **Área** da ISAD‑G está agrupada em um `LabelFrame`.
- Os campos já vêm com **valores padrão** (podem ser sobrescritos).
- Botão **Prosseguir** guarda os dados e avança para o menu.

### 6.2. Menu Principal
- **Cópia/Mover Arquivos**
- **Conversão** (imagens → PDF)
- **Renomeação** (padrão institucional)
- **Verificação de Integridade** (checksums)

<a name="campos"></a>
## 7. Campos do Formulário Modular (baseado na ISAD(G))
| Área | Cód. | Campo/Subcampo | Exemplo (padrão) |
|------|------|----------------|------------------|
| Identificação do repositório | `BR` | País | *Brasil* |
| | `SP` | Estado (UF) | *São Paulo* |
| | `IIEP` | Repositório | *IIEP* |
| Conjunto documental | `INF` | Fundo | *InFormar* |
| | `EDUPOP` | Subfundo / Grupo funcional | *Educação popular* |
| Caracterização | `ICO` | Gênero documental | *Iconográfico* |
| | `DPS` | Espécie | *Diapositivo* |
| | `FOT` | Técnica | *Exposição fotográfica* |
| | `DT1` | Forma | *Derivada* |
| Unidade de descrição | `CID` | Assunto | *Cidades* |
| | `002` | Dossiê | *002* |
| | `001` | Item | *001* |
| Extensão | `ext` | Extensão de arquivo | *jpg* |

<a name="convencao"></a>
## 8. Convenção de Nomes
A função `gerar_nomes_logs()` concatena os valores para formar um **identificador** padronizado.  
**Exemplo de arquivo final:**
```
br-spiiep_informar_A-00014.jpg
```
*Onde:*
- `br` → país (duas letras)
- `sp` → UF (duas letras)
- `iiep` → repositório
- `informar` → fundo
- `A` → tipo (constante ou derivada de outro campo)
- `00014` → sequencial acrescentado pelo módulo (renomeação)

Arquivos de log seguem a mesma raiz:
```
parâmetro_br-spiiep_informar_A.csv
logCopy_br-spiiep_informar_A.csv
```

<a name="modulos"></a>
## 9. Módulos e Funções
### 9.1. `formulario.py`
| Função/Método | Descrição |
|---------------|-----------|
| `AppGUI.create_field()` | Cria `Label + Entry` com valor padrão |
| `obter_dados_formulario()` | Retorna `dict` com todos os campos |
| `executar_copiar()` | Chama `copiar_mover.main(dados, origem, destino)` |
| `executar_conversao()` | idem para `conversao` |
| `executar_renomeacao()` | idem para `renomeacao` |
| `executar_verificacao_integridade()` | idem para `verificacao_integridade` |

### 9.2. `copiar_mover.py`
| Função | Descrição |
|--------|-----------|
| `listar_arquivos()` | Recursivo; retorna lista de `Path` |
| `gerar_nomes_logs(dados)` | Monta nomes de logs a partir do formulário |
| `gerar_parametro_csv()` | Gera CSV de parâmetros + log de geração |
| `copiar_arquivos()` | Executa `shutil.copy2` conforme CSV |
| `mover_arquivos()` | Executa `shutil.move` conforme CSV |
| `escolher_acao()` | Caixinha Tk para selecionar Copiar/Mover |
| `main(dados, origem, destino)` | Orquestra o fluxo |

<a name="logs"></a>
## 10. Arquivos de Log e Relatórios CSV
Cada operação gera três elementos principais:
1. **CSV de parâmetros** – descreve *o que* será feito.
2. **Log de parâmetros** – metadados da geração (data, operador, total de linhas).
3. **Log de execução** – resultado linha a linha (Sucesso/Erro).

Todos são gravados na pasta de trabalho ou em `logs/` (configurável).

<a name="erros"></a>
## 11. Tratamento de Erros
- Função `salvar_erro()` concatena exceções em `erro.txt`.
- GUI exibe `messagebox.showerror` para falhas críticas (ex.: diretório vazio).
- Operações continuam mesmo se um arquivo individual falhar (log registra a ocorrência).

<a name="pyinstaller"></a>
## 12. Empacotamento com PyInstaller
```bash
pyinstaller --onefile --noconsole --name ArquivAPESP formulario.py
```
- `--onefile` embute dependências em executável único.
- `--noconsole` oculta prompt Windows.
- Artefato final: `dist/ArquivAPESP.exe`.

<a name="extensibilidade"></a>
## 13. Extensibilidade | Como adicionar novas operações
1. **Criar** `novo_modulo.py` seguindo contrato:
   ```python
def main(dados, origem, destino):
    pass  # sua lógica
   ```
2. **Importar** no topo de `formulario.py`.
3. **Adicionar** uma tupla em `opcoes = [("Título", callback), …]`.
4. **Implementar** `callback` equivalente aos demais`.
```
<a name="roadmap"></a>
## 14. Roadmap & TODO
- [ ] Finalizar refatoração de `conversao.py`, `renomeacao.py`, `verificacao_integridade.py` para aceitar `dados`.
- [ ] Implementar sequenciamento automático no padrão `A-00001`.
- [ ] Adicionar suporte a **hash SHA‑256** na verificação.
- [ ] Criação de exportação PDF da presente documentação.
- [ ] Testes unitários com `pytest`.

<a name="licenca"></a>
## 15

<a name="agradecimentos"></a>
## 16. Agradecimentos
- Arquivo Público do Estado de São Paulo (APESP)
- Comunidade Python


| Funcionalidade                         | Status       |
|----------------------------------------|--------------|
| Indicador de fluxo de trabalho         | Pendente     |
| Módulo para comparação de arquivos     | Pendente     |
| Conversor de formatos                  | Pendente     |
| Conversor de imagens                   | Implementado |
