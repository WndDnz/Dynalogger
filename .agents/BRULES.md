# Regras de Negócio e Protocolo (BRULES.md)

Este documento especifica as regras de negócio de comunicação com os sensores DynaLogger HF (Legacy/DyP), as estruturas dos pacotes de dados e as fórmulas de conversão física.

---

## 🔒 1. Regra de Segurança e Desbloqueio (Auth)

* **Restrição**: O dispositivo se conecta em modo restrito. Tentar ler memória ou modificar parâmetros sem autenticação resulta em recusa ou encerramento da conexão pelo firmware do sensor.
* **Procedimento de Desbloqueio**:
  1. O host deve enviar a string mágica: `oatne ogimoc mev` (15 caracteres ASCII).
  2. Logo após, deve enviar o byte de comando `0x43` (`VALIDATE_PIN`).
  3. No baixo nível, o pacote enviado à característica de escrita (`UUID_WRITE`) é:
     `[6F 61 74 6E 65 20 6F 67 69 6D 6F 63 20 6D 65 76 43]`
  4. O sensor responde na característica de notificação (`UUID_NOTIFY`) com uma confirmação contendo o comando ecoado `0x43` e o código de sucesso `01` no payload (ex: `0143`).

---

## 📟 2. Tabela de Comandos do Protocolo (Legacy/DyP)

Estes são os comandos reconhecidos enviados como o **último byte** do pacote de escrita:

| Nome do Comando | Byte (Hex) | Descrição |
| :--- | :--- | :--- |
| `SET_DYID` | `0x30` | Configura ID interno do dispositivo |
| `GET_STATUS` | `0x31` | Lê status unificado do sensor |
| `SNAPSHOT` | `0x32` | Dispara amostragem instantânea de sensores |
| `START_LOGGING` | `0x33` | Inicia sessões de gravação agendadas |
| `STOP_LOGGING` | `0x34` | Para imediatamente a gravação ativa |
| `DOWNLOAD` | `0x35` | Solicita página específica da memória Flash |
| `ACC_ACQUIRE` | `0x37` | Dispara aquisição espectral (FFT) |
| `PING` | `0x38` | Mantém conexão ativa (Heartbeat) |
| `START_SHOCK` | `0x39` | Configura/Inicia modo de impacto (Shock) |
| `FW_VER` | `0x3A` | Retorna versão do firmware |
| `GET_ALERT` | `0x3B` | Obtém limites de alerta do acelerômetro |
| `SET_ALERT` | `0x3C` | Grava limites de alerta no sensor |
| `IS_LOCKED` | `0x40` | Retorna se o dispositivo está bloqueado (`0x50` de resposta) |
| `VALIDATE_PIN` | `0x43` | Valida PIN de desbloqueio de escrita |

---

## 💾 3. Protocolo de Download de Flash (Paginado)

A extração de dados brutos da memória Flash segue uma lógica estrita de paginação assíncrona:

1. **Pedido do Host**:
   * O payload deve conter o número da página desejada formatada em **2 bytes Big Endian** seguido do byte de comando `0x35`.
   * Exemplo (Pedir Página 1): `[00 01 35]` (Big Endian).
2. **Resposta do Sensor**:
   * O sensor envia um pacote de **19 bytes** por notificação.
   * Estrutura: `[16 bytes de dados úteis] + [2 bytes de índice da página em Little Endian] + [1 byte de eco de comando 0x35]`.
   * Exemplo (Receber Página 1): `[Dados... (16 bytes)] [01 00] [35]`.

---

## 📊 4. Estruturas de Dados e Decodificações

### A. Pacote de Status (`GET_STATUS - 0x31`)
O pacote de status retornado pelo comando `0x31` possui tamanho mínimo de 18 bytes e é parseado da seguinte forma:

* **Byte 0**: Estado de Gravação (`0: STOPPED`, `1: LOGGING`, `2: SPECTRAL (FFT)`, `3: SHOCK`).
* **Byte 1**: Escala do acelerômetro em G (Ex: `16` = ±16g).
* **Bytes 2 a 5**: Timestamp de início de logs (Unix Epoch - `uint32 Little Endian`).
* **Bytes 6 a 9**: Relógio atual do sensor (Unix Epoch - `uint32 Little Endian`).
* **Bytes 10 a 11**: Memória ocupada em bytes (`uint16 Little Endian`).
* **Bytes 12 a 13**: Leitura ADC da Bateria (`uint16 Little Endian`).
* **Byte 14**: Configuração do sensor ativo (Eixos habilitados).
* **Byte 15**: Unidade do intervalo (`0: Minutos`, `1: Segundos`).
* **Byte 16**: Valor do intervalo de amostragem.
* **Byte 17**: Limiar (Threshold) do acelerômetro.

### B. Registros de Logs de Tendência
Os blocos de dados de 16 bytes na memória Flash contêm logs de tendência históricos quando o sensor está no modo `LOGGING`:

```
[Timestamp (4B - LE)] [Temp (2B - LE)] [RMS X (2B - LE)] [RMS Y (2B - LE)] [RMS Z (2B - LE)] [Reservado/Resto (4B)]
```

---

## 🧮 5. Fórmulas de Conversão Física

### Bateria
A percentagem da bateria é calculada dividindo a leitura crua do ADC (`raw_bat`) pela resolução do registrador interno:
$$\text{Bateria (\%)} = \frac{\text{raw\_bat} \times 100}{65536}$$

### Temperatura
A temperatura interna é armazenada como `int16` com fator multiplicador de 100:
$$\text{Temperatura (°C)} = \frac{\text{raw\_temp}}{100.0}$$

### Aceleração (G-Force)
O sinal de vibração é coletado nos 3 eixos e deinterpolado em coordenadas de 16 bits (`int16`). A aceleração física correspondente em unidades de gravidade ($g$) é:
$$\text{Aceleração (g)} = \text{raw\_sample} \times \frac{\text{ESCALA}}{32768.0}$$
*Onde a ESCALA padrão no firmware costuma ser `16.0` (±16g), conforme informado pelo byte de status.*
