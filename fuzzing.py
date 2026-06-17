#!/usr/bin/env python3
import asyncio
from bleak import BleakClient, BleakScanner

MAC = "DD:14:D1:67:83:E6"
UUID_WRITE  = "00005302-0000-0041-4c50-574953450000"
UUID_NOTIFY = "00005303-0000-0041-4c50-574953450000"

async def run():
    print(f"--- Teste de Ping Pong em {MAC} ---")
    device = await BleakScanner.find_device_by_address(MAC, timeout=20.0)
    if not device: return

    async with BleakClient(device, timeout=20.0) as client:
        print(f"Conectado: {client.is_connected}")
        
        def callback(sender, data):
            # Mostra como chegou (RAW) e invertido (REV)
            print(f"\n[!!!] RECEBIDO: {data.hex().upper()}")
            print(f"      INVERTIDO: {data[::-1].hex().upper()}")

        await client.start_notify(UUID_NOTIFY, callback)
        
        # Minha teoria: O Ping é apenas o byte 0x01 ou a letra 'A' (0x41)
        # Vamos testar os dois isoladamente.
        
        print("Enviando Ping 1: 0x01 (Invertido é igual)")
        await client.write_gatt_char(UUID_WRITE, b'\x01', response=False)
        await asyncio.sleep(2)

        print("Enviando Ping 2: 0x41 ('A')")
        await client.write_gatt_char(UUID_WRITE, b'\x41', response=False)
        await asyncio.sleep(2)
        
        print("Enviando Ping 3: 0x01 0x00 (Enable invertido para 00 01)")
        # Lembre-se: O Java inverte. Se o comando lógico é 01 00, enviamos 00 01
        await client.write_gatt_char(UUID_WRITE, b'\x00\x01', response=False) 
        await asyncio.sleep(5)

        await client.stop_notify(UUID_NOTIFY)

if __name__ == "__main__":
    asyncio.run(run())