import cv2
import numpy as np
import matplotlib.pyplot as plt

def alinhar_imagens(im1, im2):
    # ORB detector
    orb = cv2.ORB_create(5000)
    kp1, des1 = orb.detectAndCompute(im1, None)
    kp2, des2 = orb.detectAndCompute(im2, None)

    # Feature matching
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)

    # Extrair pontos correspondentes
    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    # Homografia
    H, _ = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
    altura, largura = im1.shape[:2]
    im2_alinhada = cv2.warpPerspective(im2, H, (largura, altura))

    return im2_alinhada

def calcular_ndvi(im_normal, im_noir):
    # Extrair canais
    red = im_normal[:, :, 0].astype(float)
    nir = im_noir[:, :, 0].astype(float)

    # NDVI
    denom = (nir + red)
    denom[denom == 0] = 1e-5
    ndvi = (nir - red) / denom

    return ndvi

def main():
    # Caminhos das imagens
    caminho_normal = "normal.jpg"
    caminho_noir = "noir.jpg"

    # Ler imagens e converter para RGB
    im_normal = cv2.imread(caminho_normal)
    im_normal = cv2.cvtColor(im_normal, cv2.COLOR_BGR2RGB)

    im_noir = cv2.imread(caminho_noir)
    im_noir = cv2.cvtColor(im_noir, cv2.COLOR_BGR2RGB)

    # Alinhar imagem NoIR à normal
    im_noir_alinhada = alinhar_imagens(im_normal, im_noir)

    # Calcular NDVI
    ndvi = calcular_ndvi(im_normal, im_noir_alinhada)

    # Normalizar para visualização
    ndvi_vis = (ndvi + 1) / 2

    # Mostrar resultado
    plt.figure(figsize=(12, 6))
    plt.imshow(ndvi_vis, cmap='RdYlGn')
    plt.colorbar(label='NDVI')
    plt.title("NDVI - Imagem Normal vs NoIR")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig("ndvi_resultado.png")
    plt.show()

if __name__ == "__main__":
    main()
