# 🧠 Explicação Detalhada do Código `mati1_controlo_voo.py` (Sistema de Controlo - Mati1)

Este é o programa principal que corre no **Raspberry Pi principal (`mati1`)** do projeto MátiSat. A sua missão é:
- Ler sensores (temperatura, pressão e GPS)
- Calcular altitude
- Tirar fotografias durante o voo
- Enviar dados por rádio
- Ativar a câmara secundária (`mati2`) e o buzzer quando necessário

---

## 📦 Bibliotecas Importadas

Este programa usa várias bibliotecas para:
- Controlar sensores (`adafruit_bmp280`, `pynmea2`)
- Usar a câmara (`picamera2`)
- Trabalhar com ficheiros, tempo, comunicação serial (`csv`, `os`, `time`)
- Ler GPS com `pigpio` e enviar sinais digitais

---

## 🔧 Constantes e Configurações

Define:
- Pinos GPIO para o buzzer e sinal para `mati2`
- Pasta onde as fotos são guardadas
- Limite de altitude para começar a tirar fotos (`ALTITUDE_FOTOS`)
- Intervalo de tempo entre fotos
- Tempo de verificação da aterragem

---

## 📷 Funções importantes

### `inicializar_camera()`
Prepara a câmara para tirar fotos (apenas uma vez, quando necessário)

### `tirar_foto(timestamp)`
Tira uma foto com o nome baseado na hora atual

### `buzzer(pig)`
Ativa o buzzer indefinidamente (com som intermitente) para ajudar a localizar o CanSat após a aterragem

### `sinal_mati2(pig)`
Envia um pulso elétrico para o `mati2` (a câmara VIS), para sincronizar a captura de imagens

### `calcular_altura(pressao, pressao_nivel_mar)`
Calcula a altitude estimada a partir da pressão medida e da pressão ao nível do mar

### `iniciar_gps(gpio, callback)`
Lê os dados GPS a partir do pino GPIO5 usando pigpio (software serial), e atualiza as coordenadas e altitude GPS

---

## 🚀 Função principal: `principal()`

1. Inicializa UART, GPS, sensores e buzzer
2. Mede a pressão de referência (nível do solo) durante 26 segundos
3. Cria a pasta e ficheiro CSV para guardar os dados
4. Entra num **loop contínuo** para:
   - Ler temperatura e pressão
   - Calcular altitude
   - Ler posição GPS
   - Guardar os dados num ficheiro CSV
   - Enviar os dados por rádio em formato JSON
   - Se a altitude ultrapassar `ALTITUDE_FOTOS`, ativa a câmara e inicia as fotos
   - A cada 4 segundos, tira uma foto e envia sinal ao `mati2`
   - Se a altitude ficar estável durante 20 segundos, assume que o CanSat aterrou e ativa o buzzer

---

## 🛑 Parar o programa

Usa `Ctrl+C` no terminal. (O programa termina o loop, mas atualmente não tem um encerramento gracioso)

---

## ✅ O que aprendemos com este código

- Como ler sensores físicos em Python
- Como calcular altitude com pressão atmosférica
- Como controlar GPIO para enviar sinais ou buzinar
- Como comunicar com módulos GPS e rádio (UART)
- Como sincronizar dois Raspberry Pi
- Como guardar e transmitir dados científicos de forma estruturada (JSON + CSV)

---

Este é o **cérebro principal** da missão MátiSat — recolhe, regista, decide e comanda. É um ótimo exemplo de como usar Python para controlar um sistema embarcado completo com múltiplos sensores e funções!
