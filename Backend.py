from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import os
import uuid

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Pasta para salvar as imagens processadas
OUTPUT_FOLDER = "output"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

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

        # Gera um nome único para o arquivo
        nome_saida = f"modificado_{str(uuid.uuid4())[:8]}.png"
        caminho_saida = os.path.join(OUTPUT_FOLDER, nome_saida)
        
        # Salva a imagem com todos os textos
        imagem.save(caminho_saida)

        print(f"Todos os textos adicionados! Imagem salva como: {caminho_saida}")
        return caminho_saida
    
    except Exception as e:
        print(f"Erro ao adicionar textos: {e}")
        return None

@app.route('/api/process-form', methods=['POST'])
def process_form():
    try:
        # Recebe os dados do formulário
        data = request.get_json()
        client_name = data.get('clientName', '')
        technician_name = data.get('technicianName', '')
        start_time = data.get('startTime', '')
        end_time = data.get('endTime', '')
        
        # Validação básica
        if not all([client_name, technician_name, start_time, end_time]):
            return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
        
        # Prepara os textos para adicionar à imagem
        # (Ajuste estas coordenadas conforme necessário)
        lista_textos = [
            {"texto": client_name, "x": 320, "y": 399},
            {"texto": start_time, "x": 442, "y": 517},
            {"texto": end_time, "x": 1100, "y": 513},
            {"texto": technician_name, "x": 337, "y": 2736},
            {"texto": technician_name, "x": 394, "y": 2854}
        ]
        
        # Processa a imagem (substitua pelo caminho da sua imagem base)
        caminho_imagem_base = "output/pagina_0001.png"  # Altere para o caminho correto
        imagem_processada = adicionando_textos(caminho_imagem_base, lista_textos, tamanho_fonte=35)
        
        if imagem_processada:
            # Retorna a URL para acessar a imagem
            image_url = f"http://localhost:5000/api/download/{os.path.basename(imagem_processada)}"
            return jsonify({
                'message': 'Imagem processada com sucesso!',
                'image_url': image_url
            })
        else:
            return jsonify({'error': 'Erro ao processar a imagem'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'Arquivo não encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)