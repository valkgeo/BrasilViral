import os
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime

# Caminhos
CATEGORIAS = ['esportes', 'economia', 'politica', 'tecnologia', 'entretenimento', 'curiosidades']
CATEGORIAS_DIR = 'categorias'
OUTPUT_JSON = 'latest_news.json'

# Função para extrair dados de uma notícia HTML
def extrair_dados_noticia(filepath, categoria):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        h1_tags = soup.find_all('h1')
        title = h1_tags[1].text.strip() if len(h1_tags) > 1 else h1_tags[0].text.strip()


        image_tag = soup.select_one('.article-featured-image img')
        if image_tag and image_tag.get('src'):
            image = image_tag['src']
            if image.startswith('images/'):
                image = f"../../{image}"
        else:
            image = f"../../images/placeholder-{categoria}.jpg"

        summary_tag = soup.select_one('.article-content p')
        summary = summary_tag.text.strip() if summary_tag else ''

        # Prioriza data da notícia no HTML
        publish_datetime = None
        date_tag = soup.select_one('.post-date')
        if date_tag:
            date_str = date_tag.text.strip()
            match = re.search(r'(\d{2}/\d{2}/\d{4}) às (\d{2}:\d{2})', date_str)
            if match:
                full_date = f"{match.group(1)} {match.group(2)}"
                try:
                    publish_datetime = datetime.strptime(full_date, '%d/%m/%Y %H:%M')
                except ValueError:
                    pass

        if not publish_datetime:
            publish_datetime = datetime.fromtimestamp(os.path.getmtime(filepath))

        return {
            'title': title,
            'summary': summary,
            'timestamp': publish_datetime.isoformat(),
            'link': os.path.join('categorias', categoria, os.path.basename(filepath)).replace('\\', '/'),
            'image': image,
            'category': categoria
        }

    except Exception as e:
        print(f"Erro ao processar {filepath}: {e}")
        return None

def indexar_noticias():
    todas_noticias = []

    for categoria in CATEGORIAS:
        cat_dir = os.path.join(CATEGORIAS_DIR, categoria)
        if not os.path.isdir(cat_dir):
            continue

        noticias_categoria = []
        for arquivo in os.listdir(cat_dir):
            if (
                not arquivo.endswith('.html') or 
                arquivo.startswith('template') or 
                arquivo == 'index.html'
            ):
                continue

            caminho = os.path.join(cat_dir, arquivo)
            dados = extrair_dados_noticia(caminho, categoria)
            if dados:
                noticias_categoria.append(dados)
                todas_noticias.append(dados)

        noticias_categoria.sort(key=lambda x: x['timestamp'], reverse=True)

        with open(os.path.join(CATEGORIAS_DIR, f'noticias_{categoria}.json'), 'w', encoding='utf-8') as f:
            json.dump(noticias_categoria, f, ensure_ascii=False, indent=2)

        print(f"✅ {len(noticias_categoria)} notícias indexadas na categoria {categoria}")

    # Agrupar as 4 últimas de cada categoria e ordenar por data
    ultimas = []
    for categoria in CATEGORIAS:
        path = os.path.join(CATEGORIAS_DIR, f'noticias_{categoria}.json')
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            noticias = json.load(f)
            ultimas.extend(noticias[:4])

    ultimas.sort(key=lambda x: x['timestamp'], reverse=True)

    latest_news_path = os.path.join(CATEGORIAS_DIR, 'latest_news.json')
    with open(latest_news_path, 'w', encoding='utf-8') as f:
        json.dump(ultimas, f, ensure_ascii=False, indent=2)

    print(f"📦 latest_news.json gerado com {len(ultimas)} notícias")


if __name__ == "__main__":
    indexar_noticias()
