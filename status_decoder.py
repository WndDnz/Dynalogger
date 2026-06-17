#! /usr/bin/env python3
import asyncio
import struct
import datetime
from bleak import BleakClient, BleakScanner

MAC = "DD:14:D1:67:83:E6"

# UUIDs
UUID_WRITE  = "00005302-0000-0041-4c50-574953450000"
UUID_NOTIFY = "00005303-0000-0041-4c50-574953450000"

# Comandos
CMD_STATUS   = b'\x31' 
CMD_VALIDATE = b'\x43' 
PIN_MAGIC = "oatne ogimoc mev" 

# Mapeamento (Inferido do padrão Dyna)
LOGGING_STATUS = {
    0: "STOPPED (Parado)",
    1: "LOGGING (Gravando)",
    2: "SPECTRAL (FFT)",
    3: "SHOCK (Impacto)"
}

INTERVAL_UNIT = {
    0: "Minutos",
    1: "Segundos"
}

async def run():
    print(f"--- Leitor de Configuração: {MAC} ---")
    
    device = await BleakScanner.find_device_by_address(MAC, timeout=20.0)
    if not device: 
        print("Dispositivo não encontrado.")
        return

    async with BleakClient(device, timeout=30.0) as client:
        print(f"Conectado.")

        # Callback para decodificar o STATUS
        def callback(sender, data):
            # Verifica se é resposta de Status (termina com 0x31) e tem tamanho suficiente
            if data[-1] == 0x31 and len(data) >= 18:
                print("\n=== STATUS DO DISPOSITIVO ===")
                print(f"RAW HEX: {data.hex().upper()}")
                
                # --- DECODIFICAÇÃO (Baseada em parseUnifiedStatus) ---
                
                # Byte 0: Status de Gravação
                status_code = data[0]
                print(f"Estado Atual: {LOGGING_STATUS.get(status_code, f'Desconhecido ({status_code})')}")
                
                # Byte 1: Escala (Range)
                scale = data[1]
                print(f"Escala do Acelerômetro: ±{scale}g")
                
                # Bytes 2-5: Data de Início (Unix Timestamp - Little Endian)
                init_ts = int.from_bytes(data[2:6], 'little')
                try:
                    init_date = datetime.datetime.fromtimestamp(init_ts)
                    print(f"Início do Log: {init_date}")
                except:
                    print(f"Início do Log: Inválido ({init_ts})")

                # Bytes 6-9: Data Atual do Sensor
                curr_ts = int.from_bytes(data[6:10], 'little')
                try:
                    curr_date = datetime.datetime.fromtimestamp(curr_ts)
                    print(f"Relógio do Sensor: {curr_date}")
                except:
                    print(f"Relógio do Sensor: Inválido ({curr_ts})")

                # Bytes 10-11: Memória Ocupada (Bytes)
                mem_used = int.from_bytes(data[10:12], 'little')
                paginas = (mem_used + 15) // 16
                print(f"Memória Ocupada: {mem_used} bytes (~{paginas} páginas)")

                # Bytes 12-13: Bateria (Raw ADC)
                raw_bat = int.from_bytes(data[12:14], 'little')
                # Cálculo aproximado visto no Java: (raw * 100) / 65536
                bat_pct = (raw_bat * 100) // 65536
                # Ou lógica de recarregável: (raw - 2000) / 260
                # Vamos mostrar o raw para garantir
                print(f"Bateria: {bat_pct}% (Raw: {raw_bat})")

                # Byte 14: Sensor Ativo (Configuração de Eixos/Tipo)
                active_sensor = data[14]
                print(f"Config Sensor (Byte 14): 0x{active_sensor:02X}")

                # Byte 15: Unidade de Intervalo
                unit_code = data[15]
                unit_str = INTERVAL_UNIT.get(unit_code, "Desconhecido")
                
                # Byte 16: Valor do Intervalo
                interval_val = data[16]
                print(f"Intervalo de Coleta: A cada {interval_val} {unit_str}")
                
                # Byte 17: Threshold (Gatilho)
                threshold = data[17]
                print(f"Trigger (Threshold): {threshold}")

            elif data[-1] == 0x43:
                print("[Auth] Desbloqueado.")

        await client.start_notify(UUID_NOTIFY, callback)

        # 1. Autenticar
        print("Autenticando...")
        payload = bytearray(PIN_MAGIC.encode('ascii')) + CMD_VALIDATE
        await client.write_gatt_char(UUID_WRITE, payload, response=False)
        await asyncio.sleep(1.0)

        # 2. Pedir Status
        print("Lendo configurações (0x31)...")
        await client.write_gatt_char(UUID_WRITE, CMD_STATUS, response=False)
        
        # Espera a resposta chegar e ser printada
        await asyncio.sleep(3.0)
        await client.stop_notify(UUID_NOTIFY)

if __name__ == "__main__":
    asyncio.run(run())