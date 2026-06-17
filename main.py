#!/usr/bin/env python3
import asyncio
from bleak import BleakClient, BleakScanner

# Seus UUIDs descobertos
UART_RX_UUID = "00005301-0000-0041-4c50-574953450000" # Escrita (App -> Device)
UART_TX_UUID = "00007001-0000-0041-4c50-574953450000" # Leitura (Device -> App)

# Substitua pelo MAC Address do seu DynaLogger (descubra via nRF Connect)
# No Linux/Mac pode ser o endereço MAC. No Windows, as vezes é um GUID longo.
DEVICE_ADDRESS = "DD:14:D1:67:83:E6" 

def notification_handler(sender, data):
    """Callback para quando o dispositivo enviar dados."""
    print(f"[RESPOSTA] Recebido de {sender}: {data.hex()}")
    # Aqui você veria o header do pacote de resposta

async def run():
    print(f"Procurando pelo dispositivo {DEVICE_ADDRESS}...")
    device = await BleakScanner.find_device_by_address(DEVICE_ADDRESS, timeout=10.0)
    
    if not device:
        print("Dispositivo não encontrado. Verifique se está perto e não conectado ao celular.")
        return

    async with BleakClient(device) as client:
        print(f"Conectado: {client.is_connected}")

        # 1. Ativar notificações (Ouvir o que o sensor fala)
        await client.start_notify(UART_TX_UUID, notification_handler)
        print("Escutando respostas...")

        # 2. Enviar um comando (AQUI ESTÁ O SEGREDO)
        # Você precisa descobrir qual HEX enviar aqui.
        # Tente comandos simples que costumam ser padrão em firmwares, 
        # ou use o Wireshark para pegar o comando real de "Handshake".
        
        # Exemplo hipotético: enviar um byte 0x00 ou uma string de 'hello'
        # data_to_send = bytes.fromhex("00") 
        # print(f"Enviando comando: {data_to_send.hex()}")
        # await client.write_gatt_char(UART_RX_UUID, data_to_send)

        # Manter a conexão aberta por um tempo para receber dados
        await asyncio.sleep(15)

        await client.stop_notify(UART_TX_UUID)

if __name__ == "__main__":
    asyncio.run(run())