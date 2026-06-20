# Pilha Tecnológica (TECHSTACK.md)

Este documento especifica a pilha tecnológica utilizada no projeto DynaShell, incluindo gerenciamento de dependências, bibliotecas e requisitos de infraestrutura local.

---

## 🐍 Core do Projeto

* **Linguagem**: Python >= 3.10
* **Paradigma**: Programação Assíncrona (`asyncio` nativo)
* **Padrão de Execução**: CLI interativo (Terminal) e scripts utilitários.

---

## 📦 Gerenciamento de Dependências e Pacotes

O projeto adota o **[uv](https://github.com/astral-sh/uv)** para gerenciamento rápido e reprodutível do ambiente virtual e de suas dependências.

* **Arquivo de Configuração**: [pyproject.toml](file:///c:/Projetos/Dynalogger/pyproject.toml)
* **Arquivo de Lock**: [uv.lock](file:///c:/Projetos/Dynalogger/uv.lock)
* **Diretório do Ambiente**: `.venv/` (Ignorado pelo Git)

---

## 📚 Dependências do Ecossistema Python

As dependências são categorizadas pelas suas responsabilidades:

### 1. Comunicação Bluetooth (BLE)
* **[bleak](https://bleak.readthedocs.io/)** (versão recomendada: mais recente):
  Driver Bluetooth Low Energy (BLE) multiplataforma e assíncrono.
  * *Observação*: No Linux, necessita do `BlueZ` ativo. No Windows, consome APIs nativas do WinRT.

### 2. Interface do Usuário (CLI)
* **[tqdm](https://github.com/tqdm/tqdm)**:
  Gera a barra de progresso animada ao fazer download de páginas da memória Flash do sensor.

### 3. Processamento de Sinais e Matemática
* **[numpy](https://numpy.org/)**:
  Manipula buffers de arrays de bytes de forma eficiente. Usado para deinterpolar os tripletos de aceleração `[X, Y, Z]` e converter valores `int16` para unidades de gravidade ($g$).

### 4. Visualização de Dados
* **[plotly](https://plotly.com/python/)**:
  Gera relatórios gráficos de vibração (`analise_vibracao.html`) e de FFT (`analise_fft.html`) interativos no formato HTML usando WebGL para suportar alta densidade de pontos.
* **[matplotlib](https://matplotlib.org/)**:
  Utilizado em [visual2.py](file:///c:/Projetos/Dynalogger/visual2.py) especificamente por sua facilidade com animações em tempo real de frames deslizantes a 30 FPS (`matplotlib.animation.FuncAnimation`).

---

## 💻 Requisitos do Ambiente de Desenvolvimento

* **Bluetooth Físico**:
  Adaptador Bluetooth 4.0 (ou superior) compatível com Bluetooth Low Energy (BLE). Em computadores Desktop sem Bluetooth nativo, requer dongle USB BLE.
* **Permissões de Sistema**:
  * No **Linux**: A execução pode exigir privilégios de superusuário ou adição do usuário ao grupo de comunicação Bluetooth (`net_raw`, `net_admin` ou `bluetooth`).
  * No **Windows**: Habilite o Bluetooth nas configurações globais do sistema.
