#! /usr/bin/env python3
import asyncio
from bleak import BleakClient, BleakScanner

MAC = "DD:14:D1:67:83:E6"

# UUIDs Principais
UUID_WRITE  = "00005302-0000-0041-4c50-574953450000"
UUID_NOTIFY = "00005303-0000-0041-4c50-574953450000"

# UUID Oculto de Temperatura (Visto no código Java)
UUID_TEMP   = "00005402-0000-0041-4c50-574953450000"

async def run():
    print(f"--- Diagnóstico de Bloqueio: {MAC} ---")
    
    device = await BleakScanner.find_device_by_address(MAC, timeout=20.0)
    if not device: return

    async with BleakClient(device, timeout=20.0) as client:
        print(f"Conectado: {client.is_connected}")

        def callback(sender, data):
            # Decodificação inteligente
            raw = data.hex().upper()
            cmd_echo = raw[-2:] # O último byte geralmente é o eco do comando (pela inversão)
            print(f"\n[RX] {len(data)} bytes | HEX: {raw}")
            
            if len(data) == 2:
                val = data[0] # O primeiro byte costuma ser o valor
                print(f"   -> Interpretação: Valor={val} | CmdEcho={data[1]:02X}")
                if data[1] == 0x50:
                    status = "BLOQUEADO" if val != 0 else "DESBLOQUEADO"
                    print(f"   -> STATUS DE BLOQUEIO: {status}")

        await client.start_notify(UUID_NOTIFY, callback)
        print("Escuta ativa.\n")

        # 1. PERGUNTA: ESTÁ BLOQUEADO? (IS_LOCKED = 80 = 0x50)
        print(">>> Enviando IS_LOCKED (0x50)...")
        # Invertido: 50
        await client.write_gatt_char(UUID_WRITE, b'\x50', response=False)
        await asyncio.sleep(2)

        # 2. TENTATIVA: STATUS LEGADO (GET_STATUS_CMD = 49 = 0x31)
        # Vai que ele responde o status completo pelo comando antigo?
        print(">>> Enviando STATUS LEGADO (0x31)...")
        await client.write_gatt_char(UUID_WRITE, b'\x31', response=False)
        await asyncio.sleep(2)

        # 3. TENTATIVA: LEITURA DIRETA DE TEMPERATURA
        # Tenta ler a característica 5402 direto, sem pedir permissão
        print(">>> Tentando ler Temperatura diretamente (UUID ...5402)...")
        try:
            val = await client.read_gatt_char(UUID_TEMP)
            # Geralmente é int16 (2 bytes) em Little Endian
            temp_int = int.from_bytes(val, byteorder='little')
            # No código Java: divide por 100 ou 10 dependendo da versão. 
            # Vamos chutar dividido por 100.
            print(f"!!! SUCESSO TEMPERATURA: {temp_int / 100.0} °C (Raw: {val.hex()})")
        except Exception as e:
            print(f"   Leitura direta falhou: {e}")

        await client.stop_notify(UUID_NOTIFY)

if __name__ == "__main__":
    asyncio.run(run())