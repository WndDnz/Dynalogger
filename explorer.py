#!/usr/bin/env python3
import asyncio
from bleak import BleakClient, BleakScanner

MAC = "DD:14:D1:67:83:E6"

# --- MAPA DO TESOURO (Extraído do seu Java) ---
# Normalizei tudo para minúsculas para garantir o 'match'
KNOWN_UUIDS = {
    "00005b02-0000-0041-4c50-574953450000": "ACCELERATION_VECTOR_CURRENT",
    "00005b01-0000-0041-4c50-574953450000": "ACCELERATION_VECTOR_SERVICE",
    "00002a06-0000-1000-8000-00805f9b34fb": "ALERT_LEVEL",
    "00001811-0000-1000-8000-00805f9b34fb": "ALERT_NOTIFICATION_SERVICE",
    "00002a19-0000-1000-8000-00805f9b34fb": "BATTERY_LEVEL",
    "0000180f-0000-1000-8000-00805f9b34fb": "BATTERY_SERVICE",
    "00002a49-0000-1000-8000-00805f9b34fb": "BLOOD_PRESSURE_FEATURE",
    "00002a35-0000-1000-8000-00805f9b34fb": "BLOOD_PRESSURE_MEASUREMENT",
    "00001810-0000-1000-8000-00805f9b34fb": "BLOOD_PRESSURE_SERVICE",
    "00002902-0000-1000-8000-00805f9b34fb": "CLIENT_CHARACTERISTIC_CONFIG",
    "00002a2b-0000-1000-8000-00805f9b34fb": "CURRENT_TIME",
    "00001805-0000-1000-8000-00805f9b34fb": "CURRENT_TIME_SERVICE",
    "00001818-0000-1000-8000-00805f9b34fb": "CYCLING_POWER_SERVICE",
    "00001816-0000-1000-8000-00805f9b34fb": "CYCLING_SPEED_AND_CADENCE_SERVICE",
    "00005302-0000-0041-4c50-574953450000": "DATA_EXCHANGE_RX (Escrever Comandos)",
    "00005301-0000-0041-4c50-574953450000": "DATA_EXCHANGE_SERVICE",
    "00005303-0000-0041-4c50-574953450000": "DATA_EXCHANGE_TX (Receber Dados)",
    "0000180a-0000-1000-8000-00805f9b34fb": "DEVICE_INFORMATION_SERVICE",
    "00005502-0000-0041-4c50-574953450000": "BAROMETRIC_PRESSURE_CURRENT",
    "00005501-0000-0041-4c50-574953450000": "BAROMETRIC_PRESSURE_SERVICE",
    "00005605-0000-0041-4c50-574953450000": "HUMIDITY_CONTROL_POINT",
    "00005602-0000-0041-4c50-574953450000": "HUMIDITY_CURRENT",
    "00005603-0000-0041-4c50-574953450000": "HUMIDITY_MAX",
    "00005604-0000-0041-4c50-574953450000": "HUMIDITY_MIN",
    "00005601-0000-0041-4c50-574953450000": "HUMIDITY_SERVICE",
    "00005405-0000-0041-4c50-574953450000": "TEMPERATURE_CONTROL_POINT",
    "00005402-0000-0041-4c50-574953450000": "TEMPERATURE_CURRENT",
    "00005403-0000-0041-4c50-574953450000": "TEMPERATURE_MAX",
    "00005404-0000-0041-4c50-574953450000": "TEMPERATURE_MIN",
    "00005401-0000-0041-4c50-574953450000": "TEMPERATURE_SERVICE",
    "00005c05-0000-0041-4c50-574953450000": "FLASH_ACCESS_CONTROL",
    "00005c04-0000-0041-4c50-574953450000": "FLASH_CONTENT",
    "00005c06-0000-0041-4c50-574953450000": "FOTA_MODE",
    "00005c01-0000-0041-4c50-574953450000": "FOTA_SERVICE",
    "00005902-0000-0041-4c50-574953450000": "FREE_FALL_STATE",
    "00005901-0000-0041-4c50-574953450000": "FREE_FALL_SERVICE",
    "00001800-0000-1000-8000-00805f9b34fb": "GENERIC_ACCESS_SERVICE",
    "00001801-0000-1000-8000-00805f9b34fb": "GENERIC_ATTRIBUTE_SERVICE",
    "00001808-0000-1000-8000-00805f9b34fb": "GLUCOSE_SERVICE",
    "00002a1c-0000-1000-8000-00805f9b34fb": "HEALTH_THERMOMETER_MEASUREMENT",
    "00001809-0000-1000-8000-00805f9b34fb": "HEALTH_THERMOMETER_SERVICE",
    "00002a37-0000-1000-8000-00805f9b34fb": "HEART_RATE_MEASUREMENT",
    "0000180d-0000-1000-8000-00805f9b34fb": "HEART_RATE_SERVICE",
    "00001812-0000-1000-8000-00805f9b34fb": "HUMAN_INTERFACE_DEVICE_SERVICE",
    "00001802-0000-1000-8000-00805f9b34fb": "IMMEDIATE_ALERT_SERVICE",
    "00005702-0000-0041-4c50-574953450000": "LIGHT_CURRENT_LEVEL",
    "00005703-0000-0041-4c50-574953450000": "LIGHT_PULSE_EVENT",
    "00005701-0000-0041-4c50-574953450000": "LIGHT_SERVICE",
    "00005802-0000-0041-4c50-574953450000": "LIGHT_SWITCH_STATE",
    "00005803-0000-0041-4c50-574953450000": "LIGHT_SWITCH_PULSE_EVENT",
    "00005801-0000-0041-4c50-574953450000": "LIGHT_SWITCH_SERVICE",
    "00001803-0000-1000-8000-00805f9b34fb": "LINK_LOSS_SERVICE",
    "00001819-0000-1000-8000-00805f9b34fb": "LOCATION_AND_NAVIGATION_SERVICE",
    "00005c03-0000-0041-4c50-574953450000": "MICROCONTROLLER",
    "00001807-0000-1000-8000-00805f9b34fb": "NEXT_DST_CHANGE_SERVICE",
    "00005c02-0000-0041-4c50-574953450000": "PACKET_CHARACTERISTIC",
    "0000180e-0000-1000-8000-00805f9b34fb": "PHONE_ALERT_STATUS_SERVICE",
    "00001806-0000-1000-8000-00805f9b34fb": "REFERENCE_TIME_UPDATE_SERVICE",
    "00001814-0000-1000-8000-00805f9b34fb": "RUNNING_SPEED_AND_CADENCE_SERVICE",
    "00001813-0000-1000-8000-00805f9b34fb": "SCAN_PARAMETER_SERVICE",
    "00002a07-0000-1000-8000-00805f9b34fb": "TX_POWER_LEVEL",
    "00001804-0000-1000-8000-00805f9b34fb": "TX_POWER_SERVICE",
    "00005c07-0000-0041-4c50-574953450000": "VENDOR_SPECIFIC",
}

async def run():
    print(f"--- Explorador de Comandos DynaLogger ({MAC}) ---")
    print("Buscando dispositivo...")
    
    device = await BleakScanner.find_device_by_address(MAC, timeout=20.0)
    if not device:
        print("Dispositivo não encontrado. (Passe o ímã?)")
        return

    async with BleakClient(device, timeout=30.0) as client:
        print(f"Conectado: {client.is_connected}")
        print("\n=== Mapeamento de Serviços e Características ===")
        
        found_features = []

        for service in client.services:
            # Identifica o Serviço
            s_uuid = str(service.uuid).lower()
            s_name = KNOWN_UUIDS.get(s_uuid, "SERVIÇO DESCONHECIDO")
            
            print(f"\n[S] {s_uuid} -> {s_name}")
            
            for char in service.characteristics:
                # Identifica a Característica
                c_uuid = str(char.uuid).lower()
                c_name = KNOWN_UUIDS.get(c_uuid, "CARACTERÍSTICA DESCONHECIDA")
                props = ", ".join(char.properties)
                
                print(f"   └── [C] {c_uuid} -> {c_name}")
                print(f"       Props: [{props}]")
                
                if c_name != "CARACTERÍSTICA DESCONHECIDA":
                    found_features.append(c_name)

                # Se for legível, tenta ler o valor
                if "read" in char.properties:
                    try:
                        value = await client.read_gatt_char(char.uuid)
                        print(f"       >>> LEITURA (Hex): {value.hex().upper()}")
                        
                        # Tenta decodificar Int (Little Endian)
                        if len(value) <= 4:
                            val_int = int.from_bytes(value, 'little')
                            print(f"       >>> LEITURA (Int): {val_int}")
                        
                        # Tenta decodificar String
                        try:
                            val_str = value.decode('utf-8')
                            # Filtra caracteres estranhos
                            if val_str.isprintable():
                                print(f"       >>> LEITURA (Str): '{val_str}'")
                        except:
                            pass
                            
                    except Exception as e:
                        print(f"       >>> ERRO AO LER: {e}")

        print("\n=== Resumo das Descobertas ===")
        print("Funcionalidades Confirmadas no seu Hardware:")
        for feature in sorted(list(set(found_features))):
            print(f" - {feature}")

if __name__ == "__main__":
    asyncio.run(run())