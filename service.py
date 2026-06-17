#!/usr/bin/env python3
import asyncio
from bleak import BleakClient, BleakScanner

MAC = "DD:14:D1:67:83:E6"

async def run():
    print(f"--- Explorando o dispositivo {MAC} ---")
    print("DICA: Passe o ímã para acordar o sensor antes de iniciar.")
    
    # 1. Localizar (Scan)
    device = await BleakScanner.find_device_by_address(MAC, timeout=20.0)
    
    if not device:
        print("Dispositivo não encontrado. Ele voltou a dormir?")
        return

    print(f"Encontrado: {device.name}. Conectando para mapeamento...")

    try:
        # 2. Conectar
        async with BleakClient(device, timeout=20.0) as client:
            print(f"CONECTADO: {client.is_connected}")
            
            print("\n================ MAPA DE SERVIÇOS ================")
            
            # Itera sobre todos os serviços encontrados
            for service in client.services:
                print(f"\n[S] Serviço: {service.uuid} ({service.description})")
                
                # Itera sobre as características dentro do serviço
                for char in service.characteristics:
                    # Formata as propriedades para ficar legível
                    props = ", ".join(char.properties)
                    
                    # Decora a saída para destacar o que procuramos
                    marker = "   "
                    if "write" in props:
                        marker = "-> " # Seta indicando entrada
                    if "notify" in props or "indicate" in props:
                        marker = "<- " # Seta indicando saída
                        
                    print(f"{marker} [C] Char: {char.uuid}")
                    print(f"       Props: [{props}]")
                    print(f"       Handle: {char.handle}")

            print("\n==================================================")
            print("Mapeamento concluído.")

    except Exception as e:
        print(f"Erro durante o mapeamento: {e}")

if __name__ == "__main__":
    asyncio.run(run())