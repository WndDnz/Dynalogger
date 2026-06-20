# Instruções para Agentes de IA (AGENTS.md)

Este documento contém diretrizes, fluxos de trabalho comuns e avisos críticos para qualquer agente de IA que atue neste repositório.

## 📌 Visão Geral do Workspace
O **DynaShell** é uma ferramenta não-oficial baseada em Python para engenharia reversa, comunicação, controle e extração de dados dos sensores proprietários **Dynamox DynaLogger HF** (especificamente modelos da linha **Legacy/DyP**). A comunicação ocorre via **Bluetooth Low Energy (BLE)**.

---

## ⚠️ Gotchas e Detalhes Críticos de Hardware

### 1. Estado de Dormência (Sleep Mode)
* **Comportamento**: O sensor desativa o rádio BLE após um tempo de inatividade para poupar bateria.
* **Solução**: Para acordá-lo, o usuário deve **passar um ímã** próximo ao sensor físico antes de tentar iniciar qualquer script de conexão.

### 2. Penalty Box (Bloqueio de Conexão)
* **Comportamento**: Se o sensor receber pacotes malformados repetidamente ou sofrer conexões consecutivas abruptas, ele ativa um mecanismo de segurança e rejeita novas conexões ("Penalty Box").
* **Sintoma**: Erros frequentes de `Connection Abort` ou falha ao localizar o dispositivo.
* **Solução**: Aguarde cerca de **1 a 2 minutos** em silêncio de rádio para o sensor liberar novas conexões.

### 3. Autenticação Obrigatória
* **Comportamento**: O sensor **não aceita** comandos de alteração de estado ou leitura de memória sem desbloqueio prévio.
* **Solução**: Sempre envie o comando de autenticação (Magic String) logo após conectar. Veja as regras detalhadas em [BRULES.md](file:///c:/Projetos/Dynalogger/.agents/BRULES.md).

### 4. Endianness Cruzada no Download
* Ao solicitar uma página de memória (comando `0x35`), o **número da página deve ser enviado em Big Endian**.
* Ao receber a página na notificação, o **número da página na resposta vem em Little Endian**.

---

## 🛠️ Fluxos de Trabalho Recomendados para Desenvolvimento

### A. Para testar comandos no Sensor
1. Edite o `TARGET_MAC` no arquivo [dynashell.py](file:///c:/Projetos/Dynalogger/dynashell.py) com o MAC do dispositivo físico.
2. Execute o shell interativo:
   ```bash
   uv run dynashell.py
   ```
3. Digite `auth` para desbloquear.
4. Experimente comandos como `get_date`, `set_date`, `spectral` ou envie comandos brutos em hexadecimal.

### B. Para analisar arquivos binários de dump
* **Logs de Tendência**:
  Execute [parse_log.py](file:///c:/Projetos/Dynalogger/parse_log.py) para interpretar os blocos de dados contidos em `dynalogger_dump.bin`.
* **Gráfico de Aceleração 3D**:
  Rode [visual.py](file:///c:/Projetos/Dynalogger/visual.py) (Plotly estático) ou [visual2.py](file:///c:/Projetos/Dynalogger/visual2.py) (Osciloscópio dinâmico com Matplotlib).
* **Análise FFT**:
  Rode [plot_fft.py](file:///c:/Projetos/Dynalogger/plot_fft.py) para renderizar o espectro obtido em `espectro.bin`.

---

## 🔍 Onde olhar no código
* **Lógica CLI interativa e loop de eventos**: [dynashell.py](file:///c:/Projetos/Dynalogger/dynashell.py)
* **Decodificador dos bytes de Status**: [status_decoder.py](file:///c:/Projetos/Dynalogger/status_decoder.py)
* **Extração de logs da memória Flash**: [fulldump.py](file:///c:/Projetos/Dynalogger/fulldump.py)
* **Trigger e plot de espectro**: [spectrum.py](file:///c:/Projetos/Dynalogger/spectrum.py) e [plot_fft.py](file:///c:/Projetos/Dynalogger/plot_fft.py)
