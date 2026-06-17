#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import argparse
from typing import Optional

# --- CONFIGURAÇÕES ---
FILENAME = "dynalogger_dump.bin"  # Valor padrão (pode ser sobrescrito via --filename)
SAMPLE_RATE = 800       # Taxa de amostragem (Hz) - Ajuste se souber o valor exato
WINDOW_SECONDS = 2.0    # Quantos segundos mostrar na tela (Janela deslizante)
PLAYBACK_SPEED = 1      # 1 = Tempo real, 2 = 2x mais rápido, etc.
Y_SCALE = 16.0          # Escala do sensor (±16g)

# Configurações de visualização
COLORS = ['#ff0000', '#00ff00', '#0000ff'] # R, G, B
LABELS = ['Eixo X', 'Eixo Y', 'Eixo Z']

def run_scope(filename: Optional[str] = None):
    """Executa o osciloscópio de vibração lendo arquivo binário.

    Parâmetros
    ----------
    filename : str | None
        Caminho para o arquivo binário contendo amostras int16 em triplet (X,Y,Z).
        Se None, usa o valor padrão definido em FILENAME.
    """
    if filename is None:
        filename = FILENAME

    if not os.path.exists(filename):
        print(f"Arquivo '{filename}' não encontrado! Use --filename para especificar outro.")
        return

    print("Carregando dados...")
    # Lê todos os dados do arquivo
    # Importante: dtype=np.int16 (Little Endian é padrão em PC)
    raw_data = np.fromfile(filename, dtype=np.int16)
    
    # Garante que o tamanho é múltiplo de 3 (X, Y, Z)
    trim = len(raw_data) % 3
    if trim > 0:
        raw_data = raw_data[:-trim]
    
    # Separa os canais
    data = raw_data.reshape(-1, 3)
    
    # Converte para força G
    # int16 max = 32768. Se escala for 16g -> fator = 16/32768
    factor = Y_SCALE / 32768.0
    data_g = data * factor

    total_samples = len(data_g)
    print(f"Total de amostras: {total_samples}")
    print(f"Duração total: {total_samples / SAMPLE_RATE:.2f} segundos")

    # --- CONFIGURAÇÃO DO GRÁFICO ---
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='#1e1e1e')
    ax.set_facecolor('#1e1e1e')
    ax.grid(True, color='#444444', linestyle='--')
    
    # Título e Labels
    ax.set_title(f"Monitor de Vibração - Reprodução ({filename})", color='white')
    ax.set_ylabel("Aceleração (g)", color='white')
    ax.set_xlabel("Tempo (s)", color='white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    # Limites iniciais
    window_samples = int(WINDOW_SECONDS * SAMPLE_RATE)
    ax.set_ylim(-Y_SCALE, Y_SCALE) # Fixo na escala máxima para não pular
    # Se quiser zoom automático, comente a linha acima e descomente a lógica no 'update'

    # Cria as 3 linhas vazias
    lines = []
    for i in range(3):
        line, = ax.plot([], [], lw=1.5, color=COLORS[i], label=LABELS[i])
        lines.append(line)
    
    ax.legend(loc='upper right', facecolor='#333333', labelcolor='white')

    # Texto de tempo
    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, color='white')

    # --- FUNÇÃO DE ANIMAÇÃO ---
    # Esta função é chamada repetidamente pelo Matplotlib
    def update(frame):
        # 'frame' é o índice atual da animação.
        # Calculamos o índice real baseado na velocidade
        current_idx = int(frame * PLAYBACK_SPEED)
        
        if current_idx >= total_samples:
            return lines # Fim do arquivo

        # Define a janela de visualização (Start -> End)
        end = current_idx
        start = max(0, end - window_samples)
        
        # Extrai o pedaço dos dados para plotar
        chunk = data_g[start:end]
        
        # Cria eixo de tempo relativo para esse chunk
        # Para efeito de "rolagem", o tempo X vai mudando
        t = np.arange(start, end) / SAMPLE_RATE

        # Atualiza as linhas
        for i in range(3):
            lines[i].set_data(t, chunk[:, i])

        # Atualiza os limites do eixo X para seguir os dados (Efeito Scroll)
        if end > window_samples:
            ax.set_xlim(t[0], t[-1])
        else:
            ax.set_xlim(0, WINDOW_SECONDS)

        time_text.set_text(f"Tempo: {end/SAMPLE_RATE:.2f}s")
        
        return lines + [time_text]

    # Calcula intervalo entre frames para bater com o Sample Rate
    # Intervalo em milissegundos.
    # Ex: Se temos 800Hz, cada amostra dura 1.25ms.
    # Se atualizarmos a cada 40ms (25fps), precisamos pular amostras ou plotar em blocos.
    # O FuncAnimation incrementa 'frame' em 1 a cada 'interval'.
    # Vamos atualizar a 30 FPS (aprox 33ms)
    fps = 30
    interval_ms = 1000 / fps
    
    # Quantos samples avançamos por frame para manter tempo real?
    # Samples por segundo / FPS
    step_size = SAMPLE_RATE / fps
    
    # Configura a animação
    # frames = total generator
    ani = animation.FuncAnimation(
        fig, 
        update, 
        frames=np.arange(0, total_samples, step_size), # Gera índices pulando 'step_size'
        interval=interval_ms, 
        blit=False, # Blit=True é mais rápido, mas as vezes buga eixos dinâmicos
        repeat=True
    )

    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualizador dinâmico de dados de vibração (3 eixos).")
    parser.add_argument("--filename", "-f", help="Arquivo binário com dados (padrão: dynalogger_dump.bin)", default=None)
    args = parser.parse_args()

    run_scope(args.filename)