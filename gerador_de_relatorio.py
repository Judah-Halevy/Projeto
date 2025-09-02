import fitz  # PyMuPDF
import os

# converter o pdf em imagem
def pdf_para_imagem(arquivo_pdf, pasta_saida="output", dpi=300):
    # Verificar se o arquivo existe
    if not os.path.exists(arquivo_pdf):
        print(f"Erro: O arquivo '{arquivo_pdf}' não foi encontrado!")
        print("Certifique-se de que o arquivo existe no diretório correto.")
        return
    
    try:
        pdf_documento = fitz.open(arquivo_pdf)
        os.makedirs(pasta_saida, exist_ok=True)

        for num_pagina in range(len(pdf_documento)):
            # vai pegar a página
            pagina = pdf_documento.load_page(num_pagina)

            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = pagina.get_pixmap(matrix=mat)

            # salvando a imagem em PNG
            nome_imagem = f"pagina_{num_pagina + 1:04d}.png"
            caminho_completo = os.path.join(pasta_saida, nome_imagem)
            pix.save(caminho_completo)

            print(f"Página {num_pagina + 1} salva como {caminho_completo}")

        pdf_documento.close()
        print("Conversão concluída com sucesso!")
        
    except Exception as e:
        print(f"Ocorreu um erro durante a conversão: {e}")

# Verificar se o arquivo existe antes de chamar a função
arquivo = "relatorio.pdf"
if os.path.exists(arquivo):
    pdf_para_imagem(arquivo, dpi=300)
else:
    print(f"Arquivo '{arquivo}' não encontrado.")
    print("Por favor, verifique se:")
    print("1. O arquivo existe no mesmo diretório do script")
    print("2. O nome do arquivo está correto (incluindo a extensão .pdf)")
    print("3. O arquivo não está corrompido")
    
    # Listar arquivos PDF no diretório atual para ajudar
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if pdf_files:
        print("\nArquivos PDF encontrados neste diretório:")
        for pdf in pdf_files:
            print(f" - {pdf}")
    else:
        print("\nNenhum arquivo PDF encontrado neste diretório.")