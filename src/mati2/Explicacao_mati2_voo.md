# 📷 Explicação Detalhada do Código `mati2_voo.py` (Sistema de Captura - Mati2)

Este script é usado no Raspberry Pi secundário (`mati2`) do projeto MátiSat. A sua função principal é **tirar fotografias no momento certo** — sempre que recebe um sinal elétrico através de um pino específico do Raspberry Pi.

---

## 🔧 O que este código faz, passo a passo:

### 1. **Importar bibliotecas**
```python
import os
from datetime import datetime
from time import sleep
from picamera2 import Picamera2
from gpiozero import DigitalInputDevice
```
Estas linhas importam ferramentas essenciais:
- `os` e `datetime` são usadas para criar nomes de ficheiros com a data e hora.
- `sleep` permite fazer pausas no programa.
- `Picamera2` serve para controlar a câmara.
- `DigitalInputDevice` serve para escutar sinais num pino do Raspberry Pi.

---

### 2. **Definir o pino de escuta**
```python
gpio_disparo = DigitalInputDevice(23)
```
O Raspberry Pi vai escutar o **pino GPIO 23** para saber quando deve tirar uma foto. Este pino está ligado ao outro Raspberry Pi (mati1), que envia um "sinal" sempre que é preciso tirar uma fotografia.

---

### 3. **Criar pasta e ficheiro de registo**
```python
diretorio_imagens = "/mnt/fotos"
ficheiro_log = os.path.join(diretorio_imagens, "registo_mati2.csv")
os.makedirs(diretorio_imagens, exist_ok=True)
```
- As fotos vão ser guardadas na pasta `/mnt/fotos`
- Cada fotografia vai ser registada num ficheiro `.csv` com o nome e a hora

---

### 4. **Esperar pelo sinal de arranque**
```python
gpio_disparo.wait_for_active()
```
O programa **fica à espera** que o outro Raspberry Pi envie o primeiro sinal. Só depois disso é que inicializa a câmara.

---

### 5. **Inicializar a câmara**
```python
camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()
sleep(2)
```
A câmara é preparada e ligada. O `sleep(2)` dá-lhe tempo para ficar pronta antes de começar a fotografar.

---

### 6. **Loop principal**
```python
while True:
    gpio_disparo.wait_for_active()
    ...
```
O programa entra num ciclo infinito, sempre à espera de novo sinal no GPIO 23. Cada vez que recebe um:
- Tira uma fotografia
- Dá-lhe um nome com a hora
- Guarda a imagem
- Regista no ficheiro `.csv`

---

### 7. **Parar com Ctrl+C**
Se carregares `Ctrl+C`, o programa termina e fecha a câmara corretamente:
```python
except KeyboardInterrupt:
    ...
finally:
    camera.close()
```

---

## ✅ O que aprendemos com este código

- Como escutar sinais elétricos com o Raspberry Pi (GPIO)
- Como controlar uma câmara com Python
- Como guardar fotos com nomes automáticos e registar num ficheiro
- Como usar estruturas de repetição e exceções (`try/except`)

---

Este script é simples, mas poderoso — faz parte da coordenação entre os dois Raspberry Pi do MátiSat. Ele garante que a câmara VIS tira fotos **exatamente ao mesmo tempo** que a câmara principal, para que depois seja possível fazer análises de NDVI com precisão!
