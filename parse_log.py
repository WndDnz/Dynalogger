#! /usr/bin/env python3
import struct
import datetime
import os

FILENAME = "dynalogger_dump.bin"

def parse_legacy_log():
    if not os.path.exists(FILENAME):
        print("Arquivo não encontrado.")
        return

    print(f"--- Decodificando Log de Tendência: {FILENAME} ---")
    
    with open(FILENAME, "rb") as f:
        page_count = 0
        while True:
            # Lê 16 bytes (tamanho do payload de download do protocolo Legacy)
            chunk = f.read(16)
            if len(chunk) < 16: break
            
            # Tenta interpretar como registro de Log:
            # [Time 4B] [Temp 2B] [RMS X 2B] [RMS Y 2B] [RMS Z 2B] [Resto 4B]
            try:
                # Little Endian (<)
                # I = Uint32 (Time), h = int16 (Temp/Acc), 4x = Pula 4 bytes
                ts_raw, temp_raw, acc_x, acc_y, acc_z = struct.unpack('<Ihhhh', chunk[:12])
                
                # Filtra blocos vazios (memória apagada é FF ou 00)
                if ts_raw == 0xFFFFFFFF or ts_raw == 0:
                    continue

                # Converte Timestamp
                try:
                    dt = datetime.datetime.fromtimestamp(ts_raw)
                except:
                    dt = f"Erro TS({ts_raw})"

                # Conversão de Unidades (Baseado no Datasheet)
                # Temp: 0.01°C -> /100
                temp_c = temp_raw / 100.0
                
                # Aceleração: A escala varia, mas geralmente raw/1000 ou raw/scale_factor
                # Assumindo milig (mg) -> /1000 = g
                gx = acc_x / 1000.0
                gy = acc_y / 1000.0
                gz = acc_z / 1000.0

                print(f"[{page_count:04d}] {dt} | Temp: {temp_c:5.2f}°C | Vib(g): X={gx:5.3f} Y={gy:5.3f} Z={gz:5.3f}")
                
            except Exception as e:
                print(f"Erro no bloco {page_count}: {e}")
            
            page_count += 1

if __name__ == "__main__":
    parse_legacy_log()