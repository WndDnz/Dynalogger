#! /usr/bin/env python3
import asyncio
from bleak import BleakClient, BleakScanner

MAC = "DD:14:D1:67:83:E6"
UUID_WRITE  = "00005302-0000-0041-4c50-574953450000"
UUID_NOTIFY = "00005303-0000-0041-4c50-574953450000"

# --- CONFIGURAÇÃO CORRETA LEGACY ---
# PIN: A "Magic String" do Java (que manteve a conexão viva)
PIN = "oatne ogimoc mev"

# Comandos (Decimal -> Hex)
CMD_VALIDATE = b'\x43' # 67 -> 0x43
CMD_STATUS   = b'\x31' # 49 -> 0x31 (A CORREÇÃO!)
CMD_DOWNLOAD = b'\x35' # 53 -> 0x35

async def run():
    print(f"--- Tentativa de Download Legacy: {MAC} ---")
    
    device = await BleakScanner.find_device_by_address(MAC, timeout=20.0)
    if not device: 
        print("Passe o ímã.")
        return

    async with BleakClient(device, timeout=25.0) as client:
        print(f"Conectado.")

        def callback(sender, data):
            print(f"[RX] {len(data)} bytes | HEX: {data.hex().upper()}")
            # Se recebermos muitos dados, é o STATUS ou DOWNLOAD
            if len(data) > 5:
                print(">>> DADOS RECEBIDOS! O CANAL ESTÁ ABERTO!")

        await client.start_notify(UUID_NOTIFY, callback)
        
        # 1. DESBLOQUEIO
        print(f"1. Enviando Unlock ('{PIN}')...")
        payload = bytearray(PIN.encode('ascii')) + CMD_VALIDATE
        await client.write_gatt_char(UUID_WRITE, payload, response=False)
        await asyncio.sleep(1.5)
        
        # 2. STATUS (Agora com o comando certo 0x31)
        print("2. Pedindo Status (0x31)...")
        await client.write_gatt_char(UUID_WRITE, CMD_STATUS, response=False)
        await asyncio.sleep(2.0)
        
        # 3. DOWNLOAD
        # Legacy Download: [OFFSET LOW] [OFFSET HIGH] [CMD]
        # Offset 0 = 00 00
        print("3. Tentando Download (0x35)...")
        down_payload = bytes.fromhex("000035") 
        await client.write_gatt_char(UUID_WRITE, down_payload, response=False)
        
        # Monitora por 10 segundos
        print("   Aguardando stream de dados...")
        for i in range(10):
            await asyncio.sleep(1)
            print(f"   ... {i+1}s")

        await client.stop_notify(UUID_NOTIFY)

if __name__ == "__main__":
    asyncio.run(run())