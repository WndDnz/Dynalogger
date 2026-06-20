# DynaShell - Unofficial DynaLogger HF Tool

O **DynaShell** é um ecossistema interativo baseado em Python para comunicação, controle, extração e visualização de dados de sensores industriais proprietários **Dynamox DynaLogger HF** (modelos da linha **Legacy/DyP**).

A ferramenta foi desenvolvida através de engenharia reversa do protocolo Bluetooth Low Energy (BLE) proprietário, permitindo ler e decodificar dados físicos (vibração, temperatura, bateria e FFT) diretamente do sensor, sem depender do aplicativo oficial ou de gateways proprietários.

---

## 🚀 Funcionalidades

* **Shell Interativo (`dynashell.py`)**: Interface de linha de comando assíncrona com envio de comandos estruturados e brutos, respostas em tempo real e manutenção de conexão via heartbeat (Ping).
* **Autenticação Bypass**: Liberação automática do sensor utilizando a senha mágica de fábrica (`oatne ogimoc mev`).
* **Extração Paginada (Dumper)**: Algoritmo para download sequencial e seguro de páginas da memória Flash do dispositivo, com correção automática de endianness cruzada.
* **Leitura de Status Completa**: Decodificação avançada do registrador de status (estado de gravação, escala do acelerômetro, bateria, relógio interno, logs salvos, intervalos e triggers).
* **Processamento Espectral**: Disparo de aquisição acelerométrica para cálculo interno de FFT e leitura de magnitude de frequência.
* **Visualização de Dados**:
  * Geração de gráficos interativos com renderização WebGL em HTML dark (Plotly).
  * Animação dinâmica de osciloscópio deslizante a 30 FPS (Matplotlib) para simulação de reprodução de vibração.

---

## 🛠️ Pilha Tecnológica e Pré-requisitos

* **Linguagem**: Python >= 3.10
* **Bluetooth**: Adaptador físico BLE (interno ou dongle USB)
* **Gerenciador de Dependências**: **[uv](https://github.com/astral-sh/uv)**

### Instalação das Dependências
O projeto utiliza um ambiente virtual gerenciado por `uv`. Para sincronizar e instalar as dependências (`bleak`, `tqdm`, `numpy`, `matplotlib`, `plotly`), basta rodar:
```bash
uv sync
```

---

## ⚙️ Configuração Inicial

Antes de rodar a CLI ou os scripts utilitários, certifique-se de configurar o endereço MAC do seu sensor físico no início do arquivo [dynashell.py](file:///c:/Projetos/Dynalogger/dynashell.py):

```python
# No topo de dynashell.py (e nos outros scripts desejados)
TARGET_MAC = "DD:14:D1:67:83:E6"  # Substitua pelo endereço MAC real do seu sensor
```

> [!IMPORTANT]
> **Gotcha de Hardware**: O sensor entra em modo de dormência (Sleep Mode) para poupar bateria. Antes de iniciar qualquer conexão BLE, **passe um ímã físico próximo ao sensor** para acordá-lo.

---

## 🖥️ Como Usar o Shell Interativo

Para iniciar a interface interativa, execute:
```bash
uv run dynashell.py
```

O shell tentará se conectar ao dispositivo e começará a enviar heartbeats (Pings) em segundo plano a cada 5 segundos para manter a sessão ativa.

### 📋 Comandos Disponíveis no Shell

| Comando | Sintaxe | Descrição |
| :--- | :--- | :--- |
| `CONNECT` | `connect` | Tenta reestabelecer a conexão BLE caso tenha caído. |
| `AUTH` | `auth` | Envia a credencial mágica (`oatne ogimoc mev`) com o comando `0x43` para desbloquear o sensor. Obrigatório antes de qualquer leitura. |
| `DOWNLOAD` | `download [nome_arquivo]` | Baixa o conteúdo da memória. Se executado após o `spectral`, baixa o espectro para `spectral_<timestamp>.bin`. Caso contrário, baixa os logs de tendência para `dynalogger_dump.bin` (ou o nome fornecido). |
| `SPECTRAL` | `spectral [config] [eixo]` | Dispara a aquisição de FFT no sensor (comando `0x37`). Parâmetros: `config` (0-5, padrão 0) e `eixo` (0=X, 1=Y, 2=Z, 3=Triaxial, padrão 3). |
| `EXIT` | `exit` | Desconecta do dispositivo de forma segura e encerra o shell. |

#### Comandos Brutos de Protocolo (Enviados sem payload)
Você pode enviar comandos hexadecimais brutos diretamente digitando o nome associado definido no mapeamento do protocolo. O shell transmitirá o byte de comando sem payload:
* `GET_STATUS` (Envia `0x31`)
* `SNAPSHOT` (Envia `0x32`)
* `START_LOGGING` (Envia `0x33`)
* `STOP_LOGGING` (Envia `0x34`)
* `PING` (Envia `0x38`)
* `FW_VER` (Envia `0x3A`)
* `IS_LOCKED` (Envia `0x40` - retorna `0x50` de eco)

---

## 🔍 Visão Geral dos Scripts no Repositório

O projeto dispõe de vários scripts específicos para depuração, extração e análise de dados:

### 1. Conexão e Diagnóstico
* **[dynashell.py](file:///c:/Projetos/Dynalogger/dynashell.py)**: A interface interativa assíncrona principal.
* **[status_decoder.py](file:///c:/Projetos/Dynalogger/status_decoder.py)**: Conecta ao sensor, valida a autenticação, envia `0x31` e decodifica todos os parâmetros e estados do hardware.
* **[service.py](file:///c:/Projetos/Dynalogger/service.py)**: Escaneia e lista todos os serviços e características GATT expostos pelo dispositivo.
* **[explorer.py](file:///c:/Projetos/Dynalogger/explorer.py)**: Executa mapeamento detalhado comparando características com UUIDs conhecidos do ecossistema Dynamox.
* **[commands.py](file:///c:/Projetos/Dynalogger/commands.py)** / **[fuzzing.py](file:///c:/Projetos/Dynalogger/fuzzing.py)** / **[unlocker.py](file:///c:/Projetos/Dynalogger/unlocker.py)**: Scripts de laboratório para testes de comandos, sniffs de pacotes e depuração de bloqueio.

### 2. Download e Extração
* **[fulldump.py](file:///c:/Projetos/Dynalogger/fulldump.py)**: Script otimizado para download completo da memória Flash paginada. Corrige a endianness cruzada (solicitação em Big Endian, resposta em Little Endian).
* **[datadumper.py](file:///c:/Projetos/Dynalogger/datadumper.py)**: Protótipo inicial do dumper de Flash.
* **[spectrum.py](file:///c:/Projetos/Dynalogger/spectrum.py)**: Dispara a amostragem acelerométrica e aquisição espectral via comando `0x37`.

### 3. Decodificação e Visualização de Arquivos `.bin`
* **[parse_log.py](file:///c:/Projetos/Dynalogger/parse_log.py)**: Interpreta o dump de logs de tendência (`dynalogger_dump.bin`), convertendo os blocos de 16 bytes em data/hora, temperatura (°C) e aceleração RMS ($g$) nos eixos X, Y e Z.
* **[visual.py](file:///c:/Projetos/Dynalogger/visual.py)**: Lê o binário de aceleração de 3 eixos e gera o gráfico interativo `analise_vibracao.html` usando Plotly.
* **[visual2.py](file:///c:/Projetos/Dynalogger/visual2.py)**: Executa um osciloscópio animado deslizante em tempo real via Matplotlib para simular a vibração coletada.
* **[plot_fft.py](file:///c:/Projetos/Dynalogger/plot_fft.py)**: Lê as amplitudes espectrais baixadas e gera o gráfico interativo de frequências `analise_fft.html` em Plotly.

---

## 📖 Fluxo de Trabalho Exemplo

### Passo 1: Extrair Coleta do Sensor
1. Acorde o sensor com o ímã.
2. Inicie o shell:
   ```bash
   uv run dynashell.py
   ```
3. Autentique-se e baixe os dados da Flash:
   ```text
   DynaShell> auth
   [*] Autenticando...
   [RX] < VALIDATE_PIN | Data: 0143 (Desbloqueado com sucesso)

   DynaShell> download meus_dados
   [*] Checando memória de Log...
   [Status] Memória Log: 12040 bytes (~753 páginas)
   [*] Baixando para 'meus_dados.bin' (753 pág)...
   [*] Download finalizado.
   ```

### Passo 2: Analisar os Dados
Execute o visualizador para inspecionar os eixos de vibração:
```bash
uv run visual.py
# Abre automaticamente 'analise_vibracao.html' no navegador
```
Ou reproduza em formato de osciloscópio contínuo:
```bash
uv run visual2.py --filename meus_dados.bin
```

---

## ⚠️ Gotchas de Desenvolvimento e Segurança

* **Penalty Box**: Se o sensor sofrer conexões abruptas ou tentativas de comandos malformados repetidamente, ele rejeitará conexões temporariamente por **1 a 2 minutos**. Aguarde antes de tentar novamente.
* **Endianness**:
  * Ao solicitar páginas (comando `0x35`), envie o número da página formatado em **Big Endian**.
  * Ao receber as notificações das páginas, note que o índice da página na resposta vem formatado em **Little Endian**.

---

## ⚖️ Aviso Legal

Esta é uma ferramenta experimental não-oficial desenvolvida para fins de estudo e integração educacional. O uso indevido de comandos brutos pode corromper ou apagar a memória Flash do sensor físico. O autor não possui afiliação com a Dynamox S.A.
