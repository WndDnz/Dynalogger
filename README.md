DynaShell - Unofficial DynaLogger HF ToolDynaShell é uma interface de linha de comando (CLI) interativa baseada em Python para comunicação, controle e extração de dados de sensores Dynamox DynaLogger HF (especificamente modelos Legacy/DyP).Esta ferramenta foi desenvolvida através de engenharia reversa do protocolo BLE proprietário, permitindo acesso total aos dados brutos do sensor sem a necessidade do aplicativo oficial ou gateway proprietário.🚀 FuncionalidadesShell Interativo: Envie comandos e receba respostas hexadecimais/ASCII em tempo real.Autenticação "Magic String": Desbloqueio automático usando a credencial de fábrica descoberta (oatne ogimoc mev).Extração de Dados (Dumper): Download completo da memória Flash com:Gestão automática de paginação.Barra de progresso visual (tqdm).Correção de Endianness (Big Endian no pedido, Little Endian na resposta).Sincronização de Relógio: Ajuste preciso da hora do sensor baseado no relógio do sistema (Linux/Windows) utilizando técnica de Start/Stop.Controle de Logging: Configuração de intervalo de amostragem e início/parada de gravação.Análise Técnica: Decodificação do pacote de Status baseada no Datasheet oficial (Bateria, Memória, Configuração).🛠️ Pré-requisitosPython 3.8 ou superior.Hardware Bluetooth Low Energy (BLE) compatível (adaptador interno ou dongle USB).Sistema Operacional: Linux (testado no Ubuntu com BlueZ) ou Windows.Instalação das Dependênciaspip install bleak tqdm
⚙️ Configuração InicialAntes de rodar, abra o arquivo dynashell.py e edite a variável TARGET_MAC com o endereço do seu dispositivo:# No início do arquivo dynashell.py
TARGET_MAC = "DD:14:D1:67:83:E6" # Substitua pelo seu MAC Address
🖥️ Como UsarExecute o script no terminal:python3 dynashell.py
Ao iniciar, o shell tentará conectar automaticamente e manterá a conexão ativa enviando heartbeats (Pings) a cada 5 segundos.Comandos DisponíveisComandoDescriçãoconnectTenta reconectar ao dispositivo caso a conexão caia.authEssencial. Envia a senha mágica para liberar o acesso aos dados.get_dateLê o status e exibe a data interna, bateria e uso de memória.set_dateSincroniza o relógio do sensor com o horário atual do seu PC.start_log [int] [unit] [sensor]Inicia uma sessão de gravação. int: Intervalo (ex: 1). unit: 0=Minutos, 1=Segundos. sensor: 0=Padrão.stop_logPara a gravação imediatamente.download [nome_arquivo]Baixa toda a memória para um arquivo .bin. Se o nome for omitido, salva em dynalogger_dump.bin.listLista todos os comandos hexadecimais conhecidos (Legacy e DyL).exitDesconecta e sai do shell.Além dos comandos acima, você pode enviar comandos brutos do protocolo pelo nome:Exemplo: GET_STATUS (Envia 0x31)Exemplo: SNAPSHOT (Envia 0x32)📖 Exemplos de Fluxo de Trabalho1. Extração de Dados (Dump)Este é o fluxo padrão para baixar dados após uma coleta.DynaShell> auth
[*] Autenticando com Magic String...
[RX] < VALIDATE_PIN | Data: 0143 <-- Sucesso (01)

DynaShell> download meus_dados
[*] Obtendo tamanho da memória...
[Status] Memória Ocupada: 12040 bytes (~753 páginas)
[*] Iniciando download para 'meus_dados.bin'...
[*] Baixando: 100%|██████████| 753/753 [00:12<00:00, 60.20pag/s]
[*] Download finalizado. 2. Configurar Nova ColetaPara limpar o sensor e configurar uma coleta de alta frequência (1 segundo).DynaShell> auth
DynaShell> set_date
[*] Sincronizando data para: 2023-10-27 15:30:00
[*] Feito!

DynaShell> start_log 1 1 0
[*] Configurando Log: Int=1, Unit=1 (Segundos), Sens=0
[*] Enviando Comando...
[RX] < START_LOGGING | Data: ... <-- Confirmação

(O LED do sensor deve começar a piscar)
🧠 Detalhes Técnicos (Engenharia Reversa)Este driver implementa o protocolo Legacy (Alpwise) detectado no hardware DyP.UUID de Escrita: 00005302-0000-0041-4c50-574953450000UUID de Leitura: 00005303-0000-0041-4c50-574953450000Estrutura do Pacote: [PAYLOAD] + [CMD_BYTE] (Sem cabeçalhos extras e sem inversão de array).Endianness:O dispositivo não inverte bytes no payload (diferente dos modelos DyL mais novos com driver BluetoothManagerNew).Contudo, no comando de Download (0x35), o pedido de página deve ser Big Endian, enquanto a resposta do índice de página chega em Little Endian.Segurança: O dispositivo bloqueia conexões externas se receber pacotes malformados repetidamente ("Penalty Box" de ~1 minuto). Se receber erros de "Connection Abort", aguarde antes de tentar novamente.⚠️ Aviso LegalEsta é uma ferramenta não oficial, desenvolvida para fins educacionais e de pesquisa. O uso indevido pode causar perda de dados armazenados no sensor. O autor não tem afiliação com a Dynamox. Use por sua conta e risco.
