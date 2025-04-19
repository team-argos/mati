# 🛰️ MátiSat – CanSat 2025 Mission (Team Argos)

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red)
![License](https://img.shields.io/badge/License-MIT-green)

MátiSat is a CanSat developed by **Team Argos** from *Escola Secundária Daniel Sampaio*, Portugal, as part of the ESA CanSat 2025 competition. It integrates environmental sensing, telemetry, NDVI imaging, and autonomous operation using a dual Raspberry Pi Zero 2W platform.

---

## 🚀 Primary Mission

To measure **air temperature** and **atmospheric pressure** during descent and transmit data via APC220 radio to the Ground Station at **1Hz**. Altitude is calculated from barometric data and GPS.

---

## 🌱 Secondary Mission

To capture images in both **near-infrared** and **visible red light** using two Raspberry Pi Camera Module 3 units (one per Pi), process them later to produce **NDVI maps** and assess **vegetation health**.

---

## 🧠 System Overview

The onboard system includes:

- 2× Raspberry Pi Zero 2W (mati1 + mati2)
- Grove BMP280 (I²C)
- Grove GPS Air530 (GPIO5)
- Grove Buzzer (PWM)
- APC220 RF Module (UART)
- Camera Module 3 (visible + NoIR)
- Waveshare UPS HAT with 2000 mAh LiPo battery

📐 See [docs/protocolo_missao.md](docs/protocolo_missao.md) for full system architecture and recovery strategy.

---
## 🧪 Cansat code

Flight code (on RPi-mati1):
```bash
python3 src/mati1/mati1_controlo_voo.py
```

Flight code (on RPi-mati2):
```bash
python3 src/mati2/mati2_voo.py
```


## 💻 Ground Station

The Ground Station script:

- Receives telemetry via serial (APC220)
- Displays live graphs: temperature, pressure, altitude (BMP & GPS)
- Shows CanSat position on Google Maps

Ground Station (on PC):
```bash
python3 src/groundstation/ground_station.py
```

---

## 📸 NDVI Processing

NDVI is calculated using two synchronized images (visible + NIR).  
Processing script is located in the [`src/ndvi/`](src/ndvi/) folder.

---

## 📂 Repository Structure

```
/src/         → Flight code, Ground Station, Simulator
/ndvi/        → NDVI scripts and sample data
/docs/        → Final report, protocol, diagrams
/3D/cansat/   → 3D models and structural design
/fotos/       → Photos of the hardware and prototypes
```

---

## 📄 Key Files

- 📘 [Final Report (PDF)](docs/Team_Argos_MatiSat_final_report_20250419.pdf)
- 🛠️ [Mission Protocol](docs/protocolo_missao.md)
- 🧰 [3D Models](3D/cansat/)
- 📊 [Budget Spreadsheet](docs/budget.xlsx)

---

## 🌐 Links

- 🔗 [Official Google Site Project Page](https://sites.google.com/ae-danielsampaio.pt/argos-team-and-mati-sat/)
- 🔬 [GitHub Repository](https://github.com/team-argos/mati)
-    [Instagram] (https://www.instagram.com/argosteam_cansat)

---

## 👨‍🚀 Team Argos

Secondary school students (10th–12th grade) from Daniel Sampaio High School  
Almada, Portugal 🇵🇹

---

© 2025 Team Argos – MIT License
