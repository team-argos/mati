# 📡 MátiSat – Mission Protocol

## 1. Pré-lançamento
- Ativar uma rede Wi-Fi (Argos, cansat2025)
- Ligar o CanSat no interruptor principal.
- Verificar se o LED azul exterior pisca, indicado energia no sistema.
- Verificar se o Máti1 e Máti2 estão com acesso ao router e confirmar os respetivos IP.
- Verificar nível de carga da bateria pelo Máti2.
  ```bash
  python3 nivel_bateria.py
  ```
- Confirmar ligação à Ground Station via APC220.
- Iniciar o script de voo no Máti1, via SSH:
  ```bash
  nohup python3 mati1_controlo_voo.py
  ```
- Iniciar o script de voo no Máti2, via SSH:
```bash
  nohup python3 mati2_voo.py
  ```

## 2. Lançamento
- O sistema deteta automaticamente o lançamento quando a altitude (BMP280 ou GPS) ultrapassa os 10 metros.
- A câmara visível começa a capturar fotos a cada 4 segundos.
- A segunda câmara (infravermelho) é ativada via GPIO17.

## 3. Voo e recolha de dados
- Durante o voo, o sistema recolhe e transmite os seguintes dados a cada segundo:
  - Temperatura (BMP280)
  - Pressão (BMP280)
  - Altitude estimada (BMP280 + GPS)
  - Latitude e Longitude (GPS)
  - Altitude GPS
- As imagens são gravadas em `/mnt/fotos/` com timestamp no nome.
- O sistema transmite os dados em formato JSON via APC220 para a Ground Station.

## 4. Pouso
- Após pouso confirmado (1 minuto de altitude estável), o sistema:
  - Para a captura de imagens.
  - Ativa o buzzer de forma intermitente para localização acústica.

## 5. Pós-missão
- Verificar os ficheiros guardados em `/mnt/fotos/`:
  - Fotografias com timestamp.
  - Ficheiro CSV com log completo da missão.
- Transferir os dados para o computador via SSH ou cartão SD.
- Processar as imagens NDVI com o script `ndvi_calculo.py`.

## 6. Ground Station
- Iniciar o script no portátil:
  ```bash
  python3 ground_station.py
  ```
- Este script:
  - Recebe dados pela porta serial (APC220).
  - Mostra gráficos em tempo real (temperatura, pressão, altitude BMP/GPS).
  - Mostra a localização no Google Maps.

## 7. Eficiência energética
- O script desativa a interface Wi-Fi automaticamente após a estabilização da linha base de pressão:
  ```bash
  rfkill block wifi
  ```

## 8. Encerramento
- O script pode ser terminado com Ctrl+C.
- O encerramento é feito de forma segura, libertando o pigpio e finalizando o programa corretamente.
