from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import os
import uuid
import textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import io

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Pasta para salvar as imagens processadas
OUTPUT_FOLDER = "output"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Dicionário com as imagens de fundo disponíveis
BACKGROUND_IMAGES = {
    "template1": "output/pagina_0001.png",
    "template2": "output/pagina_0002.png",
}

def adicionando_textos(arquivo_imagem, lista_textos, cor=(0, 0, 0), tamanho_fonte=40):
    """
    Adiciona múltiplos textos à mesma imagem de uma vez
    """
    try:
        # Abre a imagem uma única vez
        imagem = Image.open(arquivo_imagem)
        draw = ImageDraw.Draw(imagem)

        # Carregamento da fonte 
        try:
            fonte = ImageFont.truetype("arial.ttf", tamanho_fonte)
            fonte_pequena = ImageFont.truetype("arial.ttf", tamanho_fonte - 5)
        except:
            fonte = ImageFont.load_default()
            fonte_pequena = ImageFont.load_default()
        
        # Adiciona TODOS os textos
        for texto_info in lista_textos:
            # Se for um texto longo (observações), quebra em múltiplas linhas
            if texto_info.get("quebrar_linha", False) and len(texto_info["texto"]) > 50:
                lines = textwrap.wrap(texto_info["texto"], width=50)
                y_offset = texto_info["y"]
                for line in lines:
                    draw.text((texto_info["x"], y_offset), line, fill=cor, font=fonte_pequena)
                    y_offset += 30  # Espaçamento entre linhas
            else:
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

def gerar_pdf_com_imagens(imagens, nome_arquivo):
    """
    Gera um PDF com múltiplas imagens
    """
    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        for i, caminho_imagem in enumerate(imagens):
            if os.path.exists(caminho_imagem):
                # Adiciona nova página para cada imagem
                if i > 0:
                    c.showPage()
                
                # Abre a imagem e ajusta para caber na página
                img = Image.open(caminho_imagem)
                img_width, img_height = img.size
                
                # Calcula o scaling para caber na página
                page_width, page_height = letter
                scale = min(page_width/img_width, page_height/img_height) * 0.9
                
                # Posiciona a imagem centralizada
                x = (page_width - (img_width * scale)) / 2
                y = (page_height - (img_height * scale)) / 2
                
                # Desenha a imagem no PDF
                c.drawImage(caminho_imagem, x, y, width=img_width*scale, height=img_height*scale)
        
        c.save()
        buffer.seek(0)
        
        # Salva o PDF
        caminho_pdf = os.path.join(OUTPUT_FOLDER, nome_arquivo)
        with open(caminho_pdf, 'wb') as f:
            f.write(buffer.getvalue())
        
        return caminho_pdf
        
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        return None

@app.route('/api/process-form', methods=['POST'])
def process_form():
    try:
        # Recebe os dados do formulário
        data = request.get_json()
        ticket_number = data.get('ticketNumber', '')
        client_name = data.get('clientName', '')
        technician_name = data.get('technicianName', '')
        start_time = data.get('startTime', '')
        end_time = data.get('endTime', '')
        observations = data.get('observations', '').strip()
        
        # Validação básica
        if not all([ticket_number, client_name, technician_name, start_time, end_time]):
            return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
        
        # Lista para armazenar todas as imagens geradas
        todas_imagens = []
        
        # Processa AMBOS os templates
        for template_type in ["template1", "template2"]:
            # Verifica se o template existe
            if template_type not in BACKGROUND_IMAGES:
                continue
            
            # Prepara os textos para adicionar à imagem
            if template_type == "template1":
                lista_textos = [
                    {"texto": ticket_number, "x": 1670, "y": 390},
                    {"texto": client_name, "x": 320, "y": 399},
                    {"texto": start_time, "x": 442, "y": 517},
                    {"texto": end_time, "x": 1100, "y": 513},
                    {"texto": technician_name, "x": 337, "y": 2736},
                    {"texto": technician_name, "x": 394, "y": 2854}
                ]
            else:  # template2
                lista_textos = [
                    {"texto": observations, "x": 171, "y": 3043},
                ]
                
                # Adiciona observações apenas se não estiver vazia
                if observations:
                    lista_textos.append({"texto": f"Observações: {observations}", "x": 100, "y": 350, "quebrar_linha": True})
            
            # Processa a imagem com o template selecionado
            caminho_imagem_base = BACKGROUND_IMAGES[template_type]
            
            # Verifica se o arquivo existe
            if not os.path.exists(caminho_imagem_base):
                print(f"Arquivo de template não encontrado: {caminho_imagem_base}")
                continue
            
            # Usa tamanho de fonte menor para template2 (que tem mais informações)
            tamanho_fonte = 30 if template_type == "template2" else 35
            imagem_processada = adicionando_textos(caminho_imagem_base, lista_textos, tamanho_fonte=tamanho_fonte)
            
            if imagem_processada:
                todas_imagens.append(imagem_processada)
        
        if todas_imagens:
            # Gera PDF com todas as imagens
            nome_pdf = f"comprovante_{ticket_number}_{str(uuid.uuid4())[:8]}.pdf"
            pdf_path = gerar_pdf_com_imagens(todas_imagens, nome_pdf)
            
            if pdf_path:
                # Retorna a URL para acessar o PDF
                pdf_url = f"http://localhost:5000/api/download/{os.path.basename(pdf_path)}"
                return jsonify({
                    'message': 'PDF gerado com sucesso contendo ambos os templates!',
                    'pdf_url': pdf_url,
                    'templates_gerados': len(todas_imagens),
                    'has_observations': bool(observations)
                })
        
        return jsonify({'error': 'Erro ao processar os templates'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/templates', methods=['GET'])
def list_templates():
    templates = []
    for template_name, template_path in BACKGROUND_IMAGES.items():
        templates.append({
            'name': template_name,
            'path': template_path,
            'exists': os.path.exists(template_path)
        })
    return jsonify({'templates': templates})

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if filename.endswith('.pdf'):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'Arquivo não encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)