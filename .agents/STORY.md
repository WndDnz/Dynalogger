# Histórico de Desenvolvimento (STORY.md)

Este documento resume a jornada de engenharia reversa e a evolução das soluções desenvolvidas para interagir com o sensor DynaLogger HF.

---

## 🔍 Fases do Projeto

### Fase 1: Engenharia Reversa e Mapeamento de Serviços
* **Desafio**: Descobrir os serviços e as características Bluetooth do DynaLogger HF, já que o fabricante usa um protocolo BLE proprietário.
* **Ações**: 
  * Desenvolvimento do script [service.py](file:///c:/Projetos/Dynalogger/service.py) e [explorer.py](file:///c:/Projetos/Dynalogger/explorer.py) para escanear a tabela GATT do dispositivo.
  * Análise do aplicativo Android oficial decompilado (código Java) para identificar o serviço de transferência de dados Alpwise e seus UUIDs correspondentes (`00005301...`).
  * Descoberta da característica de Escrita `UUID_WRITE` (`00005302...`) e Notificação `UUID_NOTIFY` (`00005303...`).

### Fase 2: O Segredo do Desbloqueio (PIN)
* **Desafio**: O sensor recusava comandos de status e download.
* **Ações**:
  * Análise do fluxo de handshake no código Java.
  * Descoberta da credencial mágica de bypass de fábrica (Magic PIN): `"oatne ogimoc mev"` (lido de trás para frente: *"vem comigo entao"*).
  * Criação do script [unlocker.py](file:///c:/Projetos/Dynalogger/unlocker.py) para validar o PIN enviando o byte de comando `0x43` e abrindo o canal de dados.

### Fase 3: Decodificação do Status e Limites da Memória
* **Desafio**: Obter metadados do sensor (tamanho de memória ocupada, bateria, intervalo de amostragem) antes de iniciar downloads pesados.
* **Ações**:
  * Implementação do [status_decoder.py](file:///c:/Projetos/Dynalogger/status_decoder.py) com base no comando `0x31` (`GET_STATUS`).
  * Mapeamento dos bytes do status unificado (como conversão do ADC de bateria e o cálculo de páginas ocupadas com base no total de bytes na Flash).

### Fase 4: O Enigma da Endianness Paginada
* **Desafio**: Falhas e travamentos nas primeiras versões do dumper (`datadumper.py`).
* **Ações**:
  * Descobriu-se uma peculiaridade no firmware: **o pedido de página deve ser Big Endian** (ex: página 256 é `[01 00]`), mas **o retorno do índice no cabeçalho do pacote da notificação chega em Little Endian** (ex: `[00 01]`).
  * Correção definitiva aplicada no script [fulldump.py](file:///c:/Projetos/Dynalogger/fulldump.py) que permitiu baixar milhares de páginas sem erros de dessincronização ou pulos.

### Fase 5: Análise Espectral (FFT)
* **Desafio**: Acionar aquisição espectral dinâmica.
* **Ações**:
  * Mapeamento do comando `0x37` (`ACC_ACQUIRE`) no script [spectrum.py](file:///c:/Projetos/Dynalogger/spectrum.py) para calcular a transformada de Fourier no próprio chip.
  * Correção do cálculo do tamanho da FFT no shell interativo (extraindo os bytes da notificação pós-trigger) e geração do [plot_fft.py](file:///c:/Projetos/Dynalogger/plot_fft.py) para visualizar o espectro em magnitude de frequência.

### Fase 6: Visualização Amigável e Fluida
* **Desafio**: Plotar centenas de milhares de amostras de aceleração de forma dinâmica e interativa.
* **Ações**:
  * Criação de [visual.py](file:///c:/Projetos/Dynalogger/visual.py) gerando gráficos em Plotly com renderização WebGL.
  * Criação de [visual2.py](file:///c:/Projetos/Dynalogger/visual2.py) gerando uma animação de osciloscópio deslizante a 30 FPS via Matplotlib para simular uma reprodução contínua da vibração.

### Fase 7: Consolidação do Projeto e Sanitização
* **Desafio**: Manter o repositório organizado e com ambiente reprodutível.
* **Ações**:
  * Configuração do gerenciador `uv` (`pyproject.toml` e `uv.lock`).
  * Sanitização do histórico do Git removendo o ambiente virtual `venv/` antigo e arquivos `.bin`/`.html` pesados gerados localmente.
  * Criação das instruções de agente de IA na pasta `.agents/`.
