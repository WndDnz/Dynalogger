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
CMD_DOWNLOAD = b'\x35' # 53

output_file = open("dynalogger_dump.bin", "wb")
current_page = 0
downloading = True

async def run():
    global current_page, downloading
    
    print(f"--- DynaLogger Dumper v1.0 ---")
    print(f"Alvo: {MAC}")
    
    device = await BleakScanner.find_device_by_address(MAC, timeout=20.0)
    if not device: 
        print("Dispositivo não encontrado.")
        return

    async with BleakClient(device, timeout=30.0) as client:
        print(f"Conectado.")

        # Callback de Dados
        def callback(sender, data):
            global current_page, downloading
            
            # O pacote tem 19 bytes? [16 Data] + [2 Page Index] + [1 Cmd]
            if len(data) == 19 and data[-1] == 0x35:
                # Extrai dados úteis
                raw_payload = data[0:16]
                page_idx_bytes = data[16:18]
                
                # Salva no arquivo
                output_file.write(raw_payload)
                output_file.flush()
                
                # Lê qual página veio (Little Endian)
                page_rec = int.from_bytes(page_idx_bytes, 'little')
                
                print(f"[RX] Página {page_rec} recebida ({len(raw_payload)} bytes).")
                
                # Se o pacote vier cheio de 0xFF ou 0x00, pode ser o fim da memória
                # Mas a lógica segura é continuar pedindo até dar erro ou o usuário parar
                
                # Prepara para pedir a próxima
                current_page = page_rec + 1
                asyncio.create_task(request_page(client, current_page))

            elif data[-1] == 0x43:
                print("[RX] Confirmação de Desbloqueio recebida.")

        await client.start_notify(UUID_NOTIFY, callback)

        # 1. DESBLOQUEIO
        print(f"Enviando Magic String...")
        payload_unlock = bytearray(PIN_MAGIC.encode('ascii')) + CMD_VALIDATE
        await client.write_gatt_char(UUID_WRITE, payload_unlock, response=False)
        await asyncio.sleep(1.0)

        # 2. INICIAR DOWNLOAD (Página 0)
        print("Iniciando Download em Loop...")
        await request_page(client, 0)

        # Mantém o script rodando enquanto baixamos
        # O loop é alimentado pelo callback (Pediu 0 -> Chegou 0 -> Pede 1 -> ...)
        while downloading:
            await asyncio.sleep(1)
            if current_page > 2000: # Limite de segurança (ex: 32KB)
                print("Limite de segurança atingido.")
                break

        await client.stop_notify(UUID_NOTIFY)
        output_file.close()
        print("Download finalizado. Arquivo salvo: dynalogger_dump.bin")

async def request_page(client, page_num):
    # Monta pacote: [Low Byte] [High Byte] [CMD 0x35]
    # Ex: Pagina 1 -> 01 00 35
    # Ex: Pagina 256 -> 00 01 35
    
    page_bytes = page_num.to_bytes(2, byteorder='little')
    payload = bytearray(page_bytes) + CMD_DOWNLOAD
    
    # print(f"   -> Pedindo Página {page_num}...")
    await client.write_gatt_char(UUID_WRITE, payload, response=False)

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nParando...")
        output_file.close()