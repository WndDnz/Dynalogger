#! /usr/bin/env python3
import numpy as np
import plotly.graph_objects as go
import os

# --- CONFIGURAÇÕES ---
FILENAME = "espectro.bin" # O arquivo que você vai baixar agora
MAX_FREQ = 800.0          # Frequência máxima do sensor (Hz) - Chute inicial
# Se você configurou 0x00 no trigger, ele deve ter usado o padrão (ex: 800Hz ou 1600Hz)

def plot_fft():
    if not os.path.exists(FILENAME):
        print(f"Arquivo {FILENAME} não encontrado! Rode o dumper primeiro.")
        return

    print("Lendo dados espectrais...")
    
    # Tenta ler como UInt16 (Magnitude sem sinal)
    # FFTs geralmente retornam a 'força' da vibração, que é sempre positiva.
    data = np.fromfile(FILENAME, dtype=np.uint16)
    
    # Se o gráfico ficar estranho, tente mudar para np.uint32 ou np.float32
    # data = np.fromfile(FILENAME, dtype=np.uint32)

    num_bins = len(data)
    print(f"Total de linhas (bins) da FFT: {num_bins}")

    # Cria o eixo X (Frequência)
    # Cada 'bin' representa um passo de frequência
    freq_step = MAX_FREQ / num_bins
    freq_axis = np.arange(num_bins) * freq_step

    # Cria o eixo Y (Amplitude)
    # A escala exata (g ou mm/s) depende de um fator de calibração do firmware.
    # Vamos plotar 'Raw Units' por enquanto.
    amplitude = data

    print("Gerando gráfico de espectro...")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=freq_axis, 
        y=amplitude,
        mode='lines', # ou 'bars' para ver as barras individuais
        name='Espectro de Vibração',
        line=dict(color='cyan'),
        fill='tozeroy' # Preenche a área abaixo da linha
    ))

    fig.update_layout(
        title=f'Análise Espectral (FFT) - {num_bins} Linhas',
        xaxis_title='Frequência (Hz)',
        yaxis_title='Magnitude (Unidades Brutas)',
        template='plotly_dark',
        hovermode='x unified'
    )

    fig.write_html("analise_fft.html")
    print("Sucesso! Abra 'analise_fft.html'.")
    
    try:
        import webbrowser
        webbrowser.open("analise_fft.html")
    except:
        pass

if __name__ == "__main__":
    plot_fft()