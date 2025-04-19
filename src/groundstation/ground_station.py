import serial
import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import webbrowser
import time
import csv
import signal
import sys
from datetime import datetime

# CONFIGURACOES
PORTA_COM = "COM5"
BAUD_RATE = 9600

# Gerar nome do ficheiro de log no momento do arranque
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
FICHEIRO_LOG = f"registo_ground_station_{timestamp}.csv"

# Inicializar ficheiro de log
f_log = open(FICHEIRO_LOG, "w", newline="")
log_writer = csv.writer(f_log)
log_writer.writerow(["tempo (min)", "timestamp", "temperatura", "pressao", "alt_bmp", "alt_gps", "latitude", "longitude"])

# Dados para os graficos
tempos = []
temperaturas = []
pressoes = []
altitudes_bmp = []
altitudes_gps = []
coordenadas = []

t0 = time.time()

# Inicializar porta serial
try:
    ser = serial.Serial(PORTA_COM, BAUD_RATE, timeout=1)
    print(f"[SERIAL] Ligado à porta {PORTA_COM} a {BAUD_RATE} baud.")
except serial.SerialException:
    print(f"[ERRO] Porta {PORTA_COM} nao encontrada.")
    sys.exit()

# Encerramento gracioso
def terminar(signal_received, frame):
    print("\n[ENCERRAR] Ctrl+C detetado. A fechar ficheiro e terminar programa.")
    f_log.close()
    ser.close()
    plt.close('all')
    sys.exit(0)

signal.signal(signal.SIGINT, terminar)

# Inicializar figura
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(10, 8), tight_layout=True)

def atualizar(frame):
    try:
        linha = ser.readline().decode("utf-8").strip()
        if linha:
            dados = json.loads(linha)

            tempo_min = (time.time() - t0) / 60
            tempo_min_arredondado = round(tempo_min, 2)

            print(f"[JSON] {json.dumps(dados)}")

            temperaturas.append(dados["t"])
            pressoes.append(dados["p"])
            altitudes_bmp.append(dados["h"])
            altitudes_gps.append(dados["hG"])
            tempos.append(tempo_min_arredondado)

            log_writer.writerow([
                f"{tempo_min_arredondado:.2f}", dados["d"], dados["t"], dados["p"], dados["h"], dados["hG"],
                dados.get("la"), dados.get("lo")
            ])
            f_log.flush()

            ax1.clear()
            ax2.clear()
            ax3.clear()
            ax4.clear()

            ax1.plot(tempos, temperaturas, label="Temperatura (°C)")
            ax2.plot(tempos, pressoes, label="Pressao (Pa)")
            ax3.plot(tempos, altitudes_bmp, label="Altitude BMP (m)")
            ax4.plot(tempos, altitudes_gps, label="Altitude GPS (m)")

            ax1.set_ylabel("Temperatura")
            ax2.set_ylabel("Pressao")
            ax3.set_ylabel("Alt. BMP")
            ax4.set_ylabel("Alt. GPS")
            ax4.set_xlabel("Tempo (min)")

            for ax in (ax1, ax2, ax3, ax4):
                ax.legend()
                ax.grid(True)

            lat = dados.get("la")
            lon = dados.get("lo")
            if lat and lon and (lat, lon) != coordenadas[-1:] if coordenadas else (None, None):
                coordenadas.append((lat, lon))
                url = f"https://www.google.com/maps?q={lat},{lon}"
                #print(f"[MAPA] Posicao atual: {lat}, {lon}")
                print(f"[MAPA] Posicao atual: https://www.google.com/maps?q={lat},{lon}")
                #webbrowser.open(url, new=0, autoraise=False)

    except (json.JSONDecodeError, KeyError, UnicodeDecodeError) as e:
        print("[ERRO] Linha invalida ou dados incompletos:", linha)

ani = FuncAnimation(fig, atualizar, interval=1000)
plt.show()
