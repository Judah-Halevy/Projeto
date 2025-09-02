from PIL import Image, ImageDraw, ImageFont
import os
import cv2
import numpy as np

def encontrar_coordenadas_imagem(caminho_imagem):
    """Mostra a imagem e permite clicar para obter coordenadas"""
    # Verifica se o arquivo existe
    if not os.path.exists(caminho_imagem):
        print(f"Erro: Arquivo '{caminho_imagem}' não encontrado!")
        return
    
    imagem = cv2.imread(caminho_imagem)
    if imagem is None:
        print(f"Erro: Não foi possível carregar a imagem '{caminho_imagem}'")
        return
    
    # Obter dimensões originais da imagem
    altura, largura = imagem.shape[:2]
    print(f"Dimensões originais: {largura}x{altura} pixels")
    
    # Definir tamanho máximo para a janela (opcional)
    max_largura = 1200
    max_altura = 800
    
    # Calcular fator de escala mantendo a proporção
    escala = 1.0
    if largura > max_largura or altura > max_altura:
        escala_largura = max_largura / largura
        escala_altura = max_altura / altura
        escala = min(escala_largura, escala_altura)
    
    nova_largura = int(largura * escala)
    nova_altura = int(altura * escala)
    
    # Redimensionar mantendo proporção
    imagem_redimensionada = cv2.resize(imagem, (nova_largura, nova_altura))
    clone = imagem_redimensionada.copy()
    
    # Criar janela com flag para manter proporção
    cv2.namedWindow('Selecionar Coordenadas', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Selecionar Coordenadas', nova_largura, nova_altura)
    
    cv2.imshow('Selecionar Coordenadas', imagem_redimensionada)
    
    # Função para converter coordenadas clicadas para coordenadas originais
    def obter_coordenadas_originais(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Converter coordenadas clicadas (na imagem redimensionada) para coordenadas originais
            x_original = int(x / escala)
            y_original = int(y / escala)
            print(f"Coordenadas na imagem original: X={x_original}, Y={y_original}")
            print(f"Coordenadas na janela: X={x}, Y={y}")
            
            # Mostrar um ponto no local clicado (na imagem redimensionada)
            cv2.circle(param['imagem'], (x, y), 5, (0, 0, 255), -1)
            cv2.imshow('Selecionar Coordenadas', param['imagem'])
    
    cv2.setMouseCallback('Selecionar Coordenadas', obter_coordenadas_originais, {'imagem': clone})
    
    print("Clique na imagem para obter coordenadas. Pressione 'q' para sair.")
    print("As coordenadas mostradas são referentes à imagem ORIGINAL (tamanho real).")
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    cv2.destroyAllWindows()

# Uso:
encontrar_coordenadas_imagem("output/pagina_0001.png") 

################################################################################################################

# Adicionando os textos após obter as coordenadas

def adicionando_textos(arquivo_imagem, lista_textos, cor=(0, 0, 0), tamanho_fonte=20):
    """
    Adiciona múltiplos textos à mesma imagem de uma vez
    
    Args:
        arquivo_imagem: caminho da imagem original
        lista_textos: lista de dicionários com [texto, x, y]
        cor: cor do texto em RGB
        tamanho_fonte: tamanho da fonte
    """
    try:
        # Abre a imagem uma única vez
        imagem = Image.open(arquivo_imagem)
        draw = ImageDraw.Draw(imagem)

        # Carregamento da fonte 
        try:
            fonte = ImageFont.truetype("arial.ttf", tamanho_fonte)
        except:
            fonte = ImageFont.load_default()
        
        # Adiciona TODOS os textos
        for texto_info in lista_textos:
            draw.text((texto_info["x"], texto_info["y"]), texto_info["texto"], fill=cor, font=fonte)
            print(f"Texto '{texto_info['texto']}' adicionado em ({texto_info['x']}, {texto_info['y']})")

        # Salva a imagem com todos os textos
        nome_base = os.path.basename(arquivo_imagem)
        nome_saida = f"modificado_{nome_base}"
        imagem.save(nome_saida)

        print(f"Todos os textos adicionados! Imagem salva como: {nome_saida}")
        return nome_saida
    
    except Exception as e:
        print(f"Erro ao adicionar textos: {e}")
        return None

# Uso correto:
lista_textos = [
    {"texto": "19-006957-0-TORRE DA FELICIDADE", "x": 320, "y": 399},
    {"texto": "09:00", "x": 442, "y": 517},
    {"texto": "10:00", "x": 1100, "y": 513},
    {"texto": "ELSON MOTTO MENDES JUNIOR", "x": 337, "y": 2736},
    {"texto": "ELSON MOTTO MENDES JUNIOR", "x": 394, "y": 2854}
]

adicionando_textos("output/pagina_0001.png", lista_textos, tamanho_fonte=35)