# ********************* Cansat 2024/2025 ***********************
# *********************** Equipa Argos *************************
# ***** Programa de controlo de voo do cansat Máti *************
import time
import board
import busio
import adafruit_bmp280
from time import sleep, strftime, localtime
from threading import Thread
from json import dumps
from csv import writer
from os import makedirs
from os.path import exists
from serial import Serial
from pigpio import pi, INPUT, OUTPUT
from picamera2 import Picamera2
import pynmea2
from math import pow

PORTA_UART = "/dev/ttyAMA0"
GPS_GPIO = 5
GPIO_BUZZER = 12
GPIO_SINAL = 17
CAMINHO_FOTOS = "/mnt/fotos"
FICHEIRO_CSV = CAMINHO_FOTOS + "/registo_mati1.csv"
ALTITUDE_FOTOS = 30.0 # Alterar dependendo do teste para 10.0 ou mais
INTERVALO_FOTOS = 4 # em segundos
TEMPO_VERIFICACAO_SOLO = 20 # em segundos

camera = Picamera2()
camera_inicializada = False

def inicializar_camera():
    global camera_inicializada
    if not camera_inicializada:
        camera.configure(camera.create_still_configuration())
        camera.start()
        camera_inicializada = True
        print("[CAMARA] Inicializada")

def tirar_foto(timestamp):
    nome_foto = f"{CAMINHO_FOTOS}/mati1_{timestamp}.jpg"
    camera.capture_file(nome_foto)
    print(f"[CAMARA] Fotografia tirada: {nome_foto}")

def buzzer(pig):
    print("[BUZZER] Ativar buzzer indefinidamente")
    while True:
        pig.write(GPIO_BUZZER, 1)
        sleep(0.5)
        pig.write(GPIO_BUZZER, 0)
        sleep(0.5)

def sinal_mati2(pig):
    pig.write(GPIO_SINAL, 1)
    sleep(0.1)
    pig.write(GPIO_SINAL, 0)

def calcular_altura(pressao, pressao_nivel_mar):
    return 44330 * (1.0 - pow(pressao / pressao_nivel_mar, 1 / 5.255))

def iniciar_gps(gpio, callback):
    pig = pi()
    pig.set_mode(gpio, INPUT)
    pig.bb_serial_read_open(gpio, 9600, 8)
    def leitor():
        buffer = ""
        while True:
            (count, dados) = pig.bb_serial_read(gpio)
            if count > 0:
                buffer += dados.decode('utf-8', errors='ignore')
                linhas = buffer.split('\r\n')
                buffer = linhas[-1]
                for linha in linhas[:-1]:
                    if linha.startswith('$'):
                        try:
                            msg = pynmea2.parse(linha)
                            if isinstance(msg, pynmea2.types.talker.GGA):
                                lat = msg.latitude
                                lon = msg.longitude
                                alt = msg.altitude
                                if msg.lat_dir == 'S': lat = -lat
                                if msg.lon_dir == 'W': lon = -lon
                                callback((lat, lon, alt))
                        except: pass
            sleep(0.1)
    thread = Thread(target=leitor)
    thread.daemon = True
    thread.start()
    return pig

def principal():
    print("[SISTEMA] Iniciar controlo de voo ...")
    uart = Serial(PORTA_UART, 9600, timeout=1)
    gps_dados = {"lat": None, "lon": None, "alt": None}
    pig = iniciar_gps(GPS_GPIO, lambda d: gps_dados.update({"lat": d[0], "lon": d[1], "alt": d[2]}))
    pig.set_mode(GPIO_BUZZER, OUTPUT)
    pig.set_mode(GPIO_SINAL, OUTPUT)

    i2c = busio.I2C(board.SCL, board.SDA)
    bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
    bmp280.sea_level_pressure = 1013.25

    print("A calcular pressao de referencia local...")
    valores_base = []
    for i in range(26):
        valores_base.append(bmp280.pressure * 100)
        sleep(1)
    pressao_base = sum(valores_base) / len(valores_base)
    print(f"Pressao de referencia: {pressao_base:.2f} Pa")

    if not exists(CAMINHO_FOTOS):
        makedirs(CAMINHO_FOTOS)

    with open(FICHEIRO_CSV, 'w', newline='') as f_csv:
        writer_csv = writer(f_csv)
        writer_csv.writerow(["timestamp", "t", "p", "h", "la", "lo", "hG"])
        estado_fotos = False
        lancamento_detectado = False
        tempo_ultima_foto = 0
        registo_altitudes = []
        pouso_confirmado = False

        while True:
            agora = time.time()
            timestamp = strftime("%Y%m%d_%H%M%S", localtime(agora))

            temperatura = bmp280.temperature
            pressao = bmp280.pressure * 100
            altitude = calcular_altura(pressao, pressao_base)

            dados_json = {
                "d": timestamp,
                "t": round(temperatura, 2),
                "p": round(pressao, 2),
                "h": round(altitude, 2),
                "la": gps_dados["lat"],
                "lo": gps_dados["lon"],
                "hG": gps_dados["alt"]
            }

            uart.write((dumps(dados_json) + "\n").encode("utf-8"))
            print("[RADIO] Transmitido:", dados_json)

            writer_csv.writerow([
                timestamp, temperatura, pressao, altitude,
                gps_dados["lat"], gps_dados["lon"], gps_dados["alt"]
            ])
            f_csv.flush()

            if not estado_fotos and altitude > ALTITUDE_FOTOS:
                estado_fotos = True
                lancamento_detectado = True
                inicializar_camera()
                pig.write(GPIO_BUZZER, 1)
                sleep(0.2)
                pig.write(GPIO_BUZZER, 0)
                print("[BUZZER] Beep breve - lancamento detectado")
                print("[SISTEMA] Altitude > ALTITUDE_FOTOS - iniciar fotos")

            if estado_fotos and not pouso_confirmado and (agora - tempo_ultima_foto) >= INTERVALO_FOTOS:
                tirar_foto(timestamp)
                sinal_mati2(pig)
                tempo_ultima_foto = agora

            registo_altitudes.append(altitude)
            registo_altitudes = registo_altitudes[-TEMPO_VERIFICACAO_SOLO:]

            if lancamento_detectado and len(registo_altitudes) >= TEMPO_VERIFICACAO_SOLO:
                if max(registo_altitudes) - min(registo_altitudes) < 1.0 and not pouso_confirmado:
                    print("[SISTEMA] Regresso ao solo confirmado")
                    pouso_confirmado = True
                    estado_fotos = False
                    buzzer(pig)

            sleep(1)

if __name__ == "__main__":
    principal()
