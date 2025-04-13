import os
import json
import re
from datetime import datetime

# Utilitário para transformar título em slug
def slugify(title):
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

# Categorias que serão processadas
categorias = ["esportes", "economia", "politica", "tecnologia", "entretenimento", "curiosidades"]

# Diretório base de imagens
IMAGEM_PLACEHOLDER = "images/placeholder.jpg"

# Garantir que a pasta categorias/ exista
os.makedirs("categorias", exist_ok=True)

for categoria in categorias:
    print(f"🔍 Processando categoria: {categoria}")

    input_path = f"categorias/noticias_{categoria}.json"
    output_path = f"categorias/{categoria}.json"
    image_dir = f"images/{categoria}"
    os.makedirs(image_dir, exist_ok=True)

    # Criar JSON vazio de exemplo se não existir
    if not os.path.exists(input_path):
        exemplo = [
            {
                "title": f"Título de exemplo da categoria {categoria}",
                "summary": f"Resumo de exemplo da categoria {categoria}.",
                "timestamp": datetime.now().isoformat()
            }
        ]
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(exemplo, f, ensure_ascii=False, indent=2)
        print(f"⚠️ Arquivo {input_path} não existia. Criado com conteúdo de exemplo.")
        continue

    # Carrega as notícias da categoria
    with open(input_path, "r", encoding="utf-8") as f:
        noticias = json.load(f)

    noticias_final = []

    for noticia in noticias[:4]:  # até 4 por categoria
        titulo = noticia["title"]
        resumo = noticia.get("summary") or noticia.get("resumo") or ""
        timestamp = noticia.get("timestamp", datetime.now().isoformat())
        slug = slugify(titulo)

        caminho_imagem = os.path.join(image_dir, f"{slug}.jpg").replace("\\", "/")
        if not os.path.exists(caminho_imagem):
            caminho_imagem = IMAGEM_PLACEHOLDER

        noticia_formatada = {
            "title": titulo,
            "summary": resumo,
            "timestamp": timestamp,
            "link": f"categorias/{categoria}/{slug}.html",
            "image": caminho_imagem
        }

        noticias_final.append(noticia_formatada)

    # Salvar o JSON final para o site
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(noticias_final, f, ensure_ascii=False, indent=2)

    print(f"✅ Gerado {output_path} com {len(noticias_final)} notícia(s).")

# 🔁 Agora gerar o latest_news.json com a notícia mais recente de cada categoria
latest_news = {}

for categoria in categorias:
    json_path = f"categorias/{categoria}.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            noticias = json.load(f)
            if noticias:
                latest_news[categoria] = noticias[0]  # Sempre pega a mais nova

# Salva o arquivo de destaques para homepage
with open("categorias/latest_news.json", "w", encoding="utf-8") as f:
    json.dump(latest_news, f, ensure_ascii=False, indent=2)

print("📰 Arquivo latest_news.json atualizado com sucesso.")

