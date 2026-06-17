#! /usr/bin/env python3
import asyncio
import struct
from bleak import BleakClient, BleakScanner

MAC = "DD:14:D1:67:83:E6"

# UUIDs
UUID_WRITE  = "00005302-0000-0041-4c50-574953450000"
UUID_NOTIFY = "00005303-0000-0041-4c50-574953450000"

# Configurações
PIN_MAGIC = "oatne ogimoc mev"
CMD_VALIDATE = b'\x43' # 67
CMD_ACC_ACQUIRE = b'\x37' # 55 (O comando de FFT!)

async def run():
    print(f"--- DynaLogger Spectral Trigger: {MAC} ---")
    
    device = await BleakScanner.find_device_by_address(MAC, timeout=20.0)
    if not device: 
        print("Dispositivo não encontrado.")
        return

    async with BleakClient(device, timeout=30.0) as client:
        print(f"Conectado.")

        def callback(sender, data):
            print(f"[RX] {len(data)} bytes | HEX: {data.hex().upper()}")
            
            # Se recebermos resposta do 0x37
            if data[-1] == 0x37:
                print(">>> SUCESSO! O dispositivo aceitou o comando de FFT.")
                print(">>> Analise os bytes acima para ver a configuração retornada.")

        await client.start_notify(UUID_NOTIFY, callback)

        # 1. DESBLOQUEIO (Obrigatório)
        print(f"1. Desbloqueando...")
        payload_unlock = bytearray(PIN_MAGIC.encode('ascii')) + CMD_VALIDATE
        await client.write_gatt_char(UUID_WRITE, payload_unlock, response=False)
        await asyncio.sleep(1.5)

        # 2. DISPARAR FFT (ACC_ACQUIRE)
        print("2. Disparando Aquisição Espectral (0x37)...")
        
        # Montagem do Payload (Tentativa baseada no Java getAccAcquireMsg)
        # [Timestamp 4B] [Config 1B] [Eixo 1B] [Cmd 1B]
        # Vamos tentar tudo ZERO, exceto o comando.
        # Timestamp = 0, Config = 0 (Default), Eixo = 0 (X ou Geral)
        
        payload_fft = bytearray([
            0x00, 0x00, 0x00, 0x00, # Time (Little Endian)
            0x00,                   # Config/Duration
            0x00,                   # Axis (0 = X?)
            0x37                    # CMD
        ])
        
        print(f"   Enviando: {payload_fft.hex().upper()}")
        await client.write_gatt_char(UUID_WRITE, payload_fft, response=False)
        
        print("   Aguardando resposta por 10 segundos...")
        # A FFT demora para calcular (o chip tem que processar matemática)
        for i in range(10):
            await asyncio.sleep(1)
            print(f"   ... {i+1}s")

        await client.stop_notify(UUID_NOTIFY)

if __name__ == "__main__":
    asyncio.run(run())