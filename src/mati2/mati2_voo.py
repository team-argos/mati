import os
from datetime import datetime
from time import sleep
from picamera2 import Picamera2
from gpiozero import DigitalInputDevice

# --- Configuracao do GPIO ---
gpio_disparo = DigitalInputDevice(23)

# --- Diretorio das imagens e do log ---
diretorio_imagens = "/mnt/fotos"
ficheiro_log = os.path.join(diretorio_imagens, "registo_mati2.csv")
os.makedirs(diretorio_imagens, exist_ok=True)

# --- Inicializar log ---
if not os.path.exists(ficheiro_log):
    with open(ficheiro_log, "w") as f:
        f.write("timestamp,nome_ficheiro\n")

# --- Esperar pelo primeiro sinal para inicializar a camara ---
print("A espera do sinal de inicio no GPIO23...")
gpio_disparo.wait_for_active()
print("Sinal recebido! A inicializar a camara...")

# --- Inicializar camara ---
camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()
sleep(2)

# --- Contador de fotos ---
contador = 1
print("Sistema de captura (mati2) iniciado.")

try:
    while True:
        gpio_disparo.wait_for_active()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_ficheiro = f"mati2_{timestamp}.jpg"
        caminho_ficheiro = os.path.join(diretorio_imagens, nome_ficheiro)

        camera.capture_file(caminho_ficheiro)
        print(f"Fotografia capturada: {nome_ficheiro}")

        # --- Registar no log ---
        with open(ficheiro_log, "a") as f:
            f.write(f"{timestamp},{nome_ficheiro}\n")

        contador += 1
        sleep(1)

except KeyboardInterrupt:
    print("Programa terminado pelo utilizador.")

finally:
    camera.close()
