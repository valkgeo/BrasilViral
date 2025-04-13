#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agente de Pesquisa de Imagens para o BrasilViral
Este script pesquisa imagens gratuitas relacionadas ao conteúdo das notícias.
"""

import os
import re
import json
import random
import requests
from bs4 import BeautifulSoup
from pexels_api import API as PexelsAPI
import time
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("image_search.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ImageSearchAgent")

# Chaves de API gratuitas (limitadas, mas funcionais para demonstração)
# Em produção, recomenda-se obter chaves próprias
# Nota: A API do Pexels está desativada devido a problemas de autenticação
PEXELS_API_KEY = "jrXJGlYFro4VREfpV5wUrbInYmsx4yOt7lcRlSiAre1dbE2TD1kUjswV"  # Desativada temporariamente
PIXABAY_API_KEY = "49718726-79b3e5b5dc7b07437ad852cdb"

def slugify(text):
    """Transforma um título em um nome de arquivo seguro e legível"""
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


class ImageSearchAgent:
    """Agente para pesquisar imagens gratuitas relacionadas a notícias."""
    
    def __init__(self):
        """Inicializa o agente de pesquisa de imagens."""
        self.pexels = None
        if PEXELS_API_KEY:
            self.pexels = PexelsAPI(PEXELS_API_KEY)
        self.image_cache = {}
        self.cache_file = "image_cache.json"
        self._load_cache()
        
    def _load_cache(self):
        """Carrega o cache de imagens do arquivo, se existir."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.image_cache = json.load(f)
                logger.info(f"Cache de imagens carregado com {len(self.image_cache)} entradas")
        except Exception as e:
            logger.error(f"Erro ao carregar cache de imagens: {e}")
            self.image_cache = {}
    
    def _save_cache(self):
        """Salva o cache de imagens em um arquivo."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.image_cache, f, ensure_ascii=False, indent=2)
            logger.info(f"Cache de imagens salvo com {len(self.image_cache)} entradas")
        except Exception as e:
            logger.error(f"Erro ao salvar cache de imagens: {e}")
    
    def search_pexels(self, query, per_page=15):
        """Pesquisa imagens no Pexels."""
        # Se o cliente Pexels não estiver disponível, retorna lista vazia
        if not self.pexels:
            logger.warning("API do Pexels não configurada. Pulando pesquisa no Pexels.")
            return []
            
        try:
            self.pexels.search(query, page=1, results_per_page=per_page)
            photos = self.pexels.get_entries()
            if photos:
                # Ordenar por popularidade (mais visualizações primeiro)
                photos.sort(key=lambda x: x.width * x.height, reverse=True)
                return [
                    {
                        'url': photo.original,
                        'thumbnail': photo.medium,
                        'source': 'Pexels',
                        'source_url': photo.url,
                        'width': photo.width,
                        'height': photo.height
                    } for photo in photos
                ]
            return []
        except Exception as e:
            logger.error(f"Erro ao pesquisar no Pexels: {e}")
            return []
    
    def search_pixabay(self, query, per_page=15):
        """Pesquisa imagens no Pixabay."""
        try:
            url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query.replace(' ', '+')}&image_type=photo&per_page={per_page}"
            response = requests.get(url)
            data = response.json()
            
            if 'hits' in data and data['hits']:
                return [
                    {
                        'url': hit['largeImageURL'],
                        'thumbnail': hit['webformatURL'],
                        'source': 'Pixabay',
                        'source_url': hit['pageURL'],
                        'width': hit['imageWidth'],
                        'height': hit['imageHeight']
                    } for hit in data['hits']
                ]
            return []
        except Exception as e:
            logger.error(f"Erro ao pesquisar no Pixabay: {e}")
            return []
    
    def search_google_images(self, query, num_images=5):
        """Pesquisa imagens no Google Images (método alternativo sem API)."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            query = query.replace(' ', '+')
            url = f"https://www.google.com/search?q={query}&tbm=isch&tbs=il:cl"  # imagens com licença de uso comercial
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            images = []
            img_tags = soup.find_all('img')
            
            # Pular a primeira imagem (geralmente é o logo do Google)
            for img in img_tags[1:num_images+1]:
                if 'src' in img.attrs and img['src'].startswith('http'):
                    images.append({
                        'url': img['src'],
                        'thumbnail': img['src'],
                        'source': 'Google Images',
                        'source_url': url,
                        'width': 0,  # Não disponível sem processamento adicional
                        'height': 0  # Não disponível sem processamento adicional
                    })
            
            return images
        except Exception as e:
            logger.error(f"Erro ao pesquisar no Google Images: {e}")
            return []
    
    def get_image_for_news(self, title, content, category, force_refresh=False):
        """
        Obtém uma imagem relevante para uma notícia.
        
        Args:
            title (str): Título da notícia
            content (str): Conteúdo da notícia
            category (str): Categoria da notícia
            force_refresh (bool): Se True, ignora o cache e busca novas imagens
            
        Returns:
            dict: Informações da imagem selecionada
        """
        # Criar uma chave única para esta notícia
        cache_key = f"{title[:50]}_{category}"
        
        # Verificar se já temos uma imagem em cache para esta notícia
        if not force_refresh and cache_key in self.image_cache:
            logger.info(f"Imagem encontrada no cache para: {title[:30]}...")
            return self.image_cache[cache_key]
        
        # Extrair palavras-chave do título e conteúdo
        keywords = self._extract_keywords(title, content, category)
        logger.info(f"Palavras-chave extraídas: {keywords}")
        
        # Tentar diferentes combinações de palavras-chave
        all_images = []
        
        # Pesquisar com palavras-chave principais
        main_query = " ".join(keywords[:3])
        # Priorizar Pixabay já que Pexels pode estar indisponível
        all_images.extend(self.search_pixabay(main_query))
        all_images.extend(self.search_pexels(main_query))
        
        # Se não encontrou imagens suficientes, tenta com a categoria
        if len(all_images) < 5:
            category_query = f"{category} {keywords[0] if keywords else ''}"
            all_images.extend(self.search_pixabay(category_query))
            all_images.extend(self.search_pexels(category_query))
        
        # Se ainda não encontrou imagens suficientes, tenta com Google Images
        if len(all_images) < 3:
            all_images.extend(self.search_google_images(main_query))
            
        # Se ainda não encontrou imagens suficientes, tenta novamente com Google Images e termos mais específicos
        if len(all_images) < 2:
            specific_query = f"{keywords[0] if keywords else ''} {category} notícia"
            all_images.extend(self.search_google_images(specific_query))
        
        # Se não encontrou nenhuma imagem, usa uma imagem padrão para a categoria
        if not all_images:
            logger.warning(f"Nenhuma imagem encontrada para: {title}. Usando imagem padrão.")
            return {
                'url': f"images/placeholder-{category.lower()}.jpg",
                'thumbnail': f"images/placeholder-{category.lower()}.jpg",
                'source': 'Padrão',
                'source_url': '',
                'width': 800,
                'height': 600,
                'is_default': True
            }
        
        # Ordenar imagens por potencial de cliques (preferindo imagens maiores e mais coloridas)
        all_images = self._sort_images_by_click_potential(all_images)
        
        # Selecionar uma imagem aleatória entre as 3 melhores para evitar repetição
        selected_image = random.choice(all_images[:min(3, len(all_images))])
        
        # Armazenar no cache
        self.image_cache[cache_key] = selected_image
        self._save_cache()
        
        logger.info(f"Imagem selecionada para '{title[:30]}...': {selected_image['source']} - {selected_image['url'][:50]}...")
        return selected_image
    
    def _extract_keywords(self, title, content, category):
        """Extrai palavras-chave relevantes do título e conteúdo da notícia."""
        # Lista de palavras a serem ignoradas (stopwords em português)
        stopwords = [
            "a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo", "as", "até",
            "com", "como", "da", "das", "de", "dela", "delas", "dele", "deles", "depois",
            "do", "dos", "e", "ela", "elas", "ele", "eles", "em", "entre", "era",
            "eram", "éramos", "essa", "essas", "esse", "esses", "esta", "estas", "este",
            "estes", "eu", "foi", "fomos", "for", "foram", "fosse", "fossem", "fui",
            "há", "isso", "isto", "já", "lhe", "lhes", "mais", "mas", "me", "mesmo",
            "meu", "meus", "minha", "minhas", "muito", "na", "não", "nas", "nem", "no",
            "nos", "nós", "nossa", "nossas", "nosso", "nossos", "num", "numa", "o", "os",
            "ou", "para", "pela", "pelas", "pelo", "pelos", "por", "qual", "quando",
            "que", "quem", "são", "se", "seja", "sejam", "sem", "será", "seu", "seus",
            "só", "somos", "sou", "sua", "suas", "também", "te", "tem", "tém", "temos",
            "tenho", "teu", "teus", "tu", "tua", "tuas", "um", "uma", "você", "vocês", "vos"
        ]
        
        # Combinar título e primeiros parágrafos do conteúdo
        text = f"{title} {content[:500]}"
        
        # Dividir em palavras e filtrar
        words = text.lower().split()
        filtered_words = [word.strip('.,;:?!()[]{}""\'') for word in words 
                         if word.strip('.,;:?!()[]{}""\'').lower() not in stopwords 
                         and len(word) > 3]
        
        # Contar frequência das palavras
        word_freq = {}
        for word in filtered_words:
            if word in word_freq:
                word_freq[word] += 1
            else:
                word_freq[word] = 1
        
        # Ordenar por frequência
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Extrair nomes próprios (palavras que começam com maiúscula no texto original)
        proper_nouns = [word for word in text.split() 
                       if word and word[0].isupper() 
                       and word.lower().strip('.,;:?!()[]{}""\'') not in stopwords]
        
        # Combinar palavras frequentes com nomes próprios
        keywords = [word for word, _ in sorted_words[:5]]
        for noun in proper_nouns[:3]:
            if noun.lower().strip('.,;:?!()[]{}""\'') not in [k.lower() for k in keywords]:
                keywords.append(noun.strip('.,;:?!()[]{}""\''))
        
        # Adicionar a categoria como palavra-chave se ainda não estiver presente
        if category.lower() not in [k.lower() for k in keywords]:
            keywords.append(category)
        
        return keywords[:6]  # Limitar a 6 palavras-chave
    
    def _sort_images_by_click_potential(self, images):
        """
        Ordena imagens pelo potencial de gerar cliques.
        Prioriza imagens maiores, mais coloridas e de melhor qualidade.
        """
        # Função para calcular pontuação de potencial de cliques
        def click_score(img):
            # Pontuação base pela resolução (tamanho)
            size_score = img.get('width', 0) * img.get('height', 0) / 1000000  # normalizado para megapixels
            
            # Bônus para imagens de certas fontes (confiáveis)
            source_bonus = 1.0
            if img.get('source') == 'Pexels':
                source_bonus = 1.2
            elif img.get('source') == 'Pixabay':
                source_bonus = 1.1
            
            # Pontuação final
            return size_score * source_bonus
        
        # Ordenar imagens por pontuação
        return sorted(images, key=click_score, reverse=True)
    
    def download_image(self, image_info, save_path):
        """
        Baixa uma imagem e a salva localmente.
        
        Args:
            image_info (dict): Informações da imagem
            save_path (str): Caminho onde a imagem será salva
            
        Returns:
            bool: True se o download foi bem-sucedido, False caso contrário
        """
        try:
            # Se for uma imagem padrão, não precisa baixar
            if image_info.get('is_default', False):
                logger.info(f"Usando imagem padrão: {image_info['url']}")
                return True
            
            # Baixar a imagem
            response = requests.get(image_info['url'], stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                logger.info(f"Imagem baixada com sucesso: {save_path}")
                return True
            else:
                logger.error(f"Erro ao baixar imagem. Status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Erro ao baixar imagem: {e}")
            return False


# Função para demonstração
def demo():
    """Busca imagens, baixa-as e gera arquivo JSON para ser consumido pelo index.html."""
    import json

    agent = ImageSearchAgent()

    news_samples = [
        {'title': 'Neymar marca três gols em retorno aos gramados após lesão',
         'content': 'Após longo período afastado, Neymar voltou aos gramados...',
         'category': 'esportes'},
        {'title': 'Dólar atinge maior valor do ano e preocupa mercado brasileiro',
         'content': 'Alta histórica do dólar preocupa mercado financeiro...',
         'category': 'economia'},
        {'title': 'Lula anuncia novo pacote de investimentos para o Nordeste',
         'content': 'Pacote prevê investimentos em infraestrutura regional...',
         'category': 'politica'},
        {'title': 'Nova tecnologia promete revolucionar tratamento contra o câncer',
         'content': 'Tecnologia utiliza inteligência artificial para detecção precoce...',
         'category': 'tecnologia'},
        {'title': 'Katy Perry viaja ao espaço na segunda nave turística da SpaceX',
         'content': 'Cantora participa de missão turística espacial...',
         'category': 'entretenimento'},
        {'title': 'Lua cheia rosa ilumina céu brasileiro neste fim de semana',
         'content': 'Fenômeno astronômico observado em todo o Brasil...',
         'category': 'curiosidades'}
    ]

    image_info_for_json = {}

    for news in news_samples:
        print(f"\nBuscando imagem para: {news['title']}")
        image = agent.get_image_for_news(news['title'], news['content'], news['category'])

        slug = slugify(news['title'])
        image_filename = f"{slug}.jpg"
        save_path = os.path.join("images", news['category'], image_filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        sucesso = agent.download_image(image, save_path)

        if sucesso:
            print(f"✅ Imagem salva: {save_path}")
            image_info_for_json[news['category']] = {
                'title': news['title'],
                'image_path': f"images/{news['category']}/{image_filename}",
                'timestamp': int(time.time())
            }
        else:
            print(f"❌ Falha ao salvar imagem para: {news['title']}")

    # Salvar arquivo JSON final
    with open('images/latest_images.json', 'w', encoding='utf-8') as f:
        json.dump(image_info_for_json, f, ensure_ascii=False, indent=2)

    print("\n✅ Arquivo JSON com caminhos das imagens atualizado.")




if __name__ == "__main__":
    demo()
