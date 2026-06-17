#! /usr/bin/env python3
import asyncio
from bleak import BleakClient, BleakScanner

MAC = "DD:14:D1:67:83:E6"
UUID_WRITE  = "00005302-0000-0041-4c50-574953450000"
UUID_NOTIFY = "00005303-0000-0041-4c50-574953450000"

async def run():
    print(f"--- Identificando Firmware: {MAC} ---")
    device = await BleakScanner.find_device_by_address(MAC, timeout=20.0)
    if not device: return

    async with BleakClient(device, timeout=20.0) as client:
        print(f"Conectado.")

        def callback(sender, data):
            print(f"\n[RX RAW]: {data.hex().upper()}")
            try:
                # Tenta limpar nulos e decodificar texto
                txt = data.replace(b'\x00', b'').decode('ascii', errors='ignore')
                print(f"[RX ASCII]: {txt}")
            except:
                pass

        await client.start_notify(UUID_NOTIFY, callback)
        
        # 1. Tenta comando FW Version do protocolo NOVO (0x47)
        print("Enviando 0x47 (Get Version DyL)...")
        await client.write_gatt_char(UUID_WRITE, b'\x47', response=False)
        await asyncio.sleep(2.0)

        # 2. Tenta comando FW Version do protocolo VELHO (0x3A = 58 decimal)
        # No seu enum Commands, FW_VER_CMD = 58
        print("Enviando 0x3A (Get Version Legacy)...")
        await client.write_gatt_char(UUID_WRITE, b'\x3A', response=False)
        await asyncio.sleep(2.0)

        await client.stop_notify(UUID_NOTIFY)

if __name__ == "__main__":
    asyncio.run(run())