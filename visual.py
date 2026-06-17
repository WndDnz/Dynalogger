#! /usr/bin/env python3
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Configuração
FILENAME = "dynalogger_dump.bin"
SAMPLE_RATE = 800 # Chute inicial (Hz). Ajuste conforme a config do seu sensor (ex: 1600, 3200)

def load_and_plot():
    if not os.path.exists(FILENAME):
        print(f"Arquivo {FILENAME} não encontrado!")
        return

    print("Lendo arquivo binário...")
    # Lê os dados brutos como Inteiros de 16 bits (Little Endian)
    # O DynaLogger envia int16. Se o gráfico parecer ruído puro, pode ser necessário ajustar.
    raw_data = np.fromfile(FILENAME, dtype=np.int16)

    print(f"Total de amostras brutas: {len(raw_data)}")

    # AJUSTE DE EIXOS (DEINTERLEAVING)
    # Geralmente os dados vêm: X, Y, Z, X, Y, Z...
    # Precisamos garantir que o total seja divisível por 3 para separar
    trim_size = len(raw_data) - (len(raw_data) % 3)
    data_trimmed = raw_data[:trim_size]
    
    # Remodela para 3 colunas [N, 3]
    # Coluna 0 = X, Coluna 1 = Y, Coluna 2 = Z
    data_matrix = data_trimmed.reshape(-1, 3)
    
    # Fator de conversão (G-Force)
    # Isso depende da sensibilidade configurada (2g, 4g, 8g, 16g).
    # Um valor int16 vai de -32768 a 32767.
    # Se a escala for 16G, então 32768 = 16G.
    SCALE_FACTOR = 16.0 / 32768.0 
    
    x_axis = data_matrix[:, 0] * SCALE_FACTOR
    y_axis = data_matrix[:, 1] * SCALE_FACTOR
    z_axis = data_matrix[:, 2] * SCALE_FACTOR

    # Cria eixo de tempo (segundos)
    time_axis = np.arange(len(x_axis)) / SAMPLE_RATE

    print("Gerando gráfico interativo (pode demorar alguns segundos)...")

    # Criação do Gráfico com Plotly (WebGL para performance)
    fig = go.Figure()

    # Adiciona Eixo X
    fig.add_trace(go.Scattergl(
        x=time_axis, y=x_axis,
        mode='lines',
        name='Eixo X',
        line=dict(color='red', width=1)
    ))

    # Adiciona Eixo Y
    fig.add_trace(go.Scattergl(
        x=time_axis, y=y_axis,
        mode='lines',
        name='Eixo Y',
        line=dict(color='green', width=1)
    ))

    # Adiciona Eixo Z
    fig.add_trace(go.Scattergl(
        x=time_axis, y=z_axis,
        mode='lines',
        name='Eixo Z',
        line=dict(color='blue', width=1)
    ))

    fig.update_layout(
        title=f'Análise de Vibração DynaLogger ({len(x_axis)} amostras)',
        xaxis_title='Tempo (s)',
        yaxis_title='Aceleração (g)',
        template='plotly_dark',
        hovermode='x unified'
    )

    # Adiciona slider para navegar no tempo
    fig.update_xaxes(rangeslider_visible=True)

    # Salva e abre
    fig.write_html("analise_vibracao.html")
    print("Sucesso! Abra o arquivo 'analise_vibracao.html' no seu navegador.")
    
    # Tenta abrir automaticamente (funciona em Windows/Mac/Linux com interface)
    try:
        import webbrowser
        webbrowser.open("analise_vibracao.html")
    except:
        pass

if __name__ == "__main__":
    load_and_plot()