#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agente de Pesquisa de Notícias Virais para o BrasilViral
Este script pesquisa notícias virais nas categorias do site e as reescreve para publicação.
"""

import os
import json
import random
import requests
import logging
import re
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
from together import Together
# Removida dependência do NLTK
# import nltk
# from nltk.tokenize import sent_tokenize
from urllib.parse import urlparse, urljoin
from PIL import Image
from io import BytesIO
from diffusers import DiffusionPipeline
import torch

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("news_research.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NewsResearchAgent")

# Removida dependência de download do NLTK
# Usando implementação própria de tokenização de sentenças

# Categorias suportadas pelo site
CATEGORIES = {
    'esportes': ['futebol', 'basquete', 'vôlei', 'tênis', 'olimpíadas', 'fórmula 1', 'mma'],
    'economia': ['mercado financeiro', 'bolsa de valores', 'dólar', 'inflação', 'pib', 'empregos'],
    'politica': ['governo', 'congresso', 'eleições', 'stf', 'leis', 'partidos'],
    'tecnologia': ['inteligência artificial', 'smartphones', 'apps', 'redes sociais', 'games', 'inovação'],
    'entretenimento': ['celebridades', 'cinema', 'música', 'tv', 'streaming', 'reality show'],
    'curiosidades': ['ciência', 'saúde', 'animais', 'fenômenos', 'história', 'descobertas']
}

# Fontes de notícias por categoria
NEWS_SOURCES = {
    'esportes': [
        'https://ge.globo.com/',
        'https://www.lance.com.br/',
        'https://www.espn.com.br/',
        'https://www.uol.com.br/esporte/'
    ],
    'economia': [
        'https://economia.uol.com.br/',
        'https://valor.globo.com/',
        'https://www.infomoney.com.br/',
        'https://www.investing.com/news/economy'
    ],
    'politica': [
        'https://g1.globo.com/politica/',
        'https://noticias.uol.com.br/politica/',
        'https://www.poder360.com.br/',
        'https://www.cnnbrasil.com.br/politica/'
    ],
    'tecnologia': [
        'https://www.tecmundo.com.br/',
        'https://olhardigital.com.br/',
        'https://canaltech.com.br/',
        'https://tecnoblog.net/'
    ],
    'entretenimento': [
        'https://www.omelete.com.br/',
        'https://www.papelpop.com/',
        'https://www.uol.com.br/splash/',
        'https://gshow.globo.com/'
    ],
    'curiosidades': [
        'https://revistagalileu.globo.com/',
        'https://super.abril.com.br/',
        'https://www.megacurioso.com.br/',
        'https://www.hypeness.com.br/'
    ]
}

# Fontes de tendências
TREND_SOURCES = [
    'https://trends.google.com.br/trends/trendingsearches/daily?geo=BR',
    'https://twitter.com/explore/tabs/trending',
    'https://www.reddit.com/r/brasil/hot/'
]

class NewsResearchAgent:
    """Agente para pesquisar notícias virais e reescrevê-las para publicação."""
    
    def __init__(self):
        """Inicializa o agente de pesquisa de notícias."""
        self.news_cache = {}
        self.published_news = {}
        self.cache_file = "news_cache.json"
        self.published_file = "published_news.json"
        self._load_cache()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.together_client = Together(api_key="a0ed7d9e416c949da3446ec1605ae122e74d64eedfae029f2ca0a81bdcf41ed7")
        self.diffusers_pipe = DiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float32
        ).to("cpu")  # ou "cuda"

    
    def _load_cache(self):
        """Carrega o cache de notícias e o registro de notícias publicadas."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.news_cache = json.load(f)
                logger.info(f"Cache de notícias carregado com {len(self.news_cache)} entradas")
            
            if os.path.exists(self.published_file):
                with open(self.published_file, 'r', encoding='utf-8') as f:
                    self.published_news = json.load(f)
                logger.info(f"Registro de notícias publicadas carregado com {len(self.published_news)} entradas")
        except Exception as e:
            logger.error(f"Erro ao carregar cache de notícias: {e}")
            self.news_cache = {}
            self.published_news = {}
    
    def _save_cache(self):
        """Salva o cache de notícias e o registro de notícias publicadas."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.news_cache, f, ensure_ascii=False, indent=2)
            logger.info(f"Cache de notícias salvo com {len(self.news_cache)} entradas")
            
            with open(self.published_file, 'w', encoding='utf-8') as f:
                json.dump(self.published_news, f, ensure_ascii=False, indent=2)
            logger.info(f"Registro de notícias publicadas salvo com {len(self.published_news)} entradas")
        except Exception as e:
            logger.error(f"Erro ao salvar cache de notícias: {e}")
    
    def get_trending_topics(self):
        """Obtém tópicos em tendência no Brasil."""
        trending_topics = []
        
        # Google Trends
        try:
            response = requests.get(TREND_SOURCES[0], headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            trend_items = soup.select('.feed-item-header')
            
            for item in trend_items[:10]:  # Limitar aos 10 primeiros
                topic = item.get_text().strip()
                if topic:
                    trending_topics.append(topic)
        except Exception as e:
            logger.error(f"Erro ao obter tendências do Google Trends: {e}")
        
        # Reddit Brasil
        try:
            response = requests.get(TREND_SOURCES[2], headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            posts = soup.select('.Post')
            
            for post in posts[:10]:
                title_elem = post.select_one('h3')
                if title_elem:
                    topic = title_elem.get_text().strip()
                    if topic:
                        trending_topics.append(topic)
        except Exception as e:
            logger.error(f"Erro ao obter tendências do Reddit Brasil: {e}")
        
        # Remover duplicatas e limitar a 20 tópicos
        unique_topics = list(set(trending_topics))
        logger.info(f"Obtidos {len(unique_topics)} tópicos em tendência")
        return unique_topics[:20]
    
    def search_viral_news(self, category, limit=10):
        if category not in CATEGORIES:
            logger.error(f"Categoria inválida: {category}")
            return []

        trending_topics = self.get_trending_topics()
        all_news = []

        for source_url in NEWS_SOURCES.get(category, []):
            try:
                logger.info(f"Pesquisando notícias em: {source_url}")
                response = requests.get(source_url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')

                news_links = []
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if any(x in href for x in ['facebook', 'twitter', 'instagram', 'login', 'cadastro']):
                        continue
                    if not href.startswith(('http://', 'https://')):
                        href = urljoin(source_url, href)
                    if urlparse(href).netloc == urlparse(source_url).netloc:
                        news_links.append(href)

                news_links = list(set(news_links))
                for link in news_links[:5]:
                    try:
                        link_hash = hashlib.md5(link.encode()).hexdigest()
                        if link_hash in self.news_cache:
                            news_data = self.news_cache[link_hash]
                            all_news.append(news_data)
                            continue

                        news_response = requests.get(link, headers=self.headers, timeout=10)
                        news_soup = BeautifulSoup(news_response.text, 'html.parser')

                        title = news_soup.find('h1') or news_soup.find('title')
                        if title:
                            title = title.get_text().strip()
                        else:
                            continue

                        paragraphs = []
                        for p in news_soup.find_all('p'):
                            text = p.get_text().strip()
                            if len(text) < 60:
                                continue
                            if any(x in text.lower() for x in ['clique aqui', 'acesse', 'edição', 'veja também', 'compartilhe']):
                                continue
                            if re.match(r'^\d{1,2}h.*', text.lower()):
                                continue
                            paragraphs.append(text)

                        content = '\n\n'.join(paragraphs[:10])
                        if not content or len(content.split()) < 80:
                            continue

                        viral_score = self._calculate_viral_score(title, content, trending_topics)
                        news_data = {
                            'title': title,
                            'content': content,
                            'source_url': link,
                            'category': category,
                            'viral_score': viral_score,
                            'timestamp': datetime.now().isoformat(),
                            'published': False
                        }

                        self.news_cache[link_hash] = news_data
                        all_news.append(news_data)

                    except Exception as e:
                        logger.error(f"Erro ao processar link de notícia {link}: {e}")

            except Exception as e:
                logger.error(f"Erro ao pesquisar notícias em {source_url}: {e}")

        self._save_cache()
        sorted_news = sorted(all_news, key=lambda x: x['viral_score'], reverse=True)
        filtered_news = [news for news in sorted_news if not self._is_already_published(news)]

        logger.info(f"Encontradas {len(filtered_news)} notícias virais na categoria {category}")
        return filtered_news[:limit]

    
    def _calculate_viral_score(self, title, content, trending_topics):
        """
        Calcula uma pontuação de viralidade para uma notícia.
        
        Args:
            title (str): Título da notícia
            content (str): Conteúdo da notícia
            trending_topics (list): Lista de tópicos em tendência
            
        Returns:
            float: Pontuação de viralidade (0-100)
        """
        score = 0
        
        # Verificar se contém palavras-chave de tendências
        for topic in trending_topics:
            if topic.lower() in title.lower():
                score += 20  # Maior peso para tópicos no título
            elif topic.lower() in content.lower():
                score += 10  # Menor peso para tópicos no conteúdo
        
        # Verificar comprimento do título (títulos entre 6-12 palavras tendem a viralizar mais)
        title_words = len(title.split())
        if 6 <= title_words <= 12:
            score += 15
        
        # Verificar se o título contém números (tendem a atrair mais cliques)
        if any(char.isdigit() for char in title):
            score += 10
        
        # Verificar se o título contém palavras emocionais ou de impacto
        emotional_words = ['incrível', 'chocante', 'surpreendente', 'impressionante', 
                          'polêmica', 'revelado', 'exclusivo', 'urgente', 'viral']
        for word in emotional_words:
            if word.lower() in title.lower():
                score += 5
        
        # Limitar a pontuação máxima a 100
        return min(score, 100)
    
    def _is_already_published(self, news):
        """
        Verifica se uma notícia já foi publicada ou é muito similar a uma publicada.
        
        Args:
            news (dict): Dados da notícia
            
        Returns:
            bool: True se já foi publicada, False caso contrário
        """
        # Verificar por URL exata
        for published in self.published_news.values():
            if published.get('source_url') == news.get('source_url'):
                return True
        
        # Verificar por similaridade de título
        news_title = news.get('title', '').lower()
        for published in self.published_news.values():
            published_title = published.get('title', '').lower()
            
            # Calcular similaridade simples (palavras em comum)
            news_words = set(news_title.split())
            published_words = set(published_title.split())
            common_words = news_words.intersection(published_words)
            
            # Se mais de 70% das palavras são comuns, considerar similar
            if len(common_words) > 0.7 * min(len(news_words), len(published_words)):
                return True
        
        return False
    
    def gerar_imagem_com_diffusers(self, prompt, categoria):
        """Gera uma imagem com Diffusers (Hugging Face) e salva localmente."""
        try:
            prompt_text = f"notícia sobre {prompt}, estilo ilustração digital, realista, colorido, brasil, 800x400"
            image = self.diffusers_pipe(prompt_text).images[0]

            slug = self._create_slug(prompt)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            nome_arquivo = f"{slug}-{timestamp}.jpg"
            pasta = os.path.join("images", categoria)
            os.makedirs(pasta, exist_ok=True)
            caminho = os.path.join(pasta, nome_arquivo)

            image = image.resize((800, 400), Image.LANCZOS)
            image.save(caminho, "JPEG", quality=85)

            logger.info(f"🖼️ Imagem gerada com Hugging Face Diffusers e salva em: {caminho}")
            return caminho.replace("\\", "/")

        except Exception as e:
            logger.error(f"Erro ao gerar imagem com Diffusers: {e}")
            return f"images/placeholder-{categoria}.jpg"



    def rewrite_news(self, news):
        """
        Usa o modelo LLM da Together AI para reescrever uma notícia com linguagem natural e estruturada.
        """
        prompt = f"""
        Você é um jornalista profissional que escreve para um site de notícias brasileiro. 
        Sua tarefa é reescrever a seguinte notícia com linguagem clara, parágrafos bem estruturados e sem referências a redes sociais, links ou chamadas de ação como "clique aqui". 
        Use português correto, estilo informativo e mantenha a notícia coerente do início ao fim.

        ⚠️ Importante: NÃO utilize markdown, a resposta deve ser em texto puro com parágrafos separados por duas quebras de linha (\\n\\n). Não utilize negrito, itálico ou símbolos especiais.

        Título original:
        {news['title']}

        Conteúdo original:
        {news['content']}

        Reescreva a notícia de forma natural e bem estruturada:
        """

        try:
            response = self.together_client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[{"role": "user", "content": prompt}]
            )
            rewritten_content = response.choices[0].message.content.strip()

            rewritten_news = news.copy()
            # Gerar imagem e salvar thumbnail
            image_path = self.gerar_imagem_com_diffusers(news['title'], news['category'])
            rewritten_news['image_url'] = f"../../{image_path}" if image_path.startswith("images/") else image_path
            rewritten_news['original_title'] = news['title']
            #Continua
            rewritten_news['title'] = news['title']
            rewritten_news['original_content'] = news['content']
            rewritten_news['content'] = '\n\n'.join(
                [f"<p>{p.strip()}</p>" for p in rewritten_content.split('\n\n') if p.strip()]
            )
            rewritten_news['rewritten'] = True
            rewritten_news['rewrite_timestamp'] = datetime.now().isoformat()


            logger.info(f"✅ Notícia reescrita com LLM: {news['title']}")
            return rewritten_news

        except Exception as e:
            print(f"❌ Erro ao reescrever com LLM: {e}".encode('utf-8', errors='replace').decode())
            
            # Tentar reescrita local como fallback
            rewritten_content = self._rewrite_text(news["content"])
            rewritten_news = news.copy()
            rewritten_news['original_title'] = news['title']
            rewritten_news['original_content'] = news['content']
            rewritten_news['content'] = rewritten_content
            rewritten_news['rewritten'] = False
            rewritten_news['rewrite_timestamp'] = datetime.now().isoformat()

            logger.info(f"⚠️ Notícia reescrita localmente (fallback): {news['title']}")
            return rewritten_news
    
    
        
        


    
    def _rewrite_text(self, text):
        """
        Reescreve um texto usando técnicas simples de paráfrase.
        
        Args:
            text (str): Texto original
            
        Returns:
            str: Texto reescrito
        """
        # Dividir em sentenças manualmente para evitar dependência do NLTK para português
        # Padrões de fim de sentença em português
        end_patterns = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
        sentences = []
        current = text
        
        # Dividir o texto em sentenças
        while current:
            # Encontrar o próximo fim de sentença
            positions = [current.find(pattern) for pattern in end_patterns if pattern in current]
            if not positions:
                # Se não encontrar mais padrões, adicionar o resto como uma sentença
                sentences.append(current)
                break
                
            # Encontrar a posição do fim de sentença mais próximo
            end_pos = min([pos for pos in positions if pos >= 0])
            
            # Determinar qual padrão foi encontrado
            for pattern in end_patterns:
                if current.find(pattern) == end_pos:
                    pattern_len = len(pattern)
                    break
            
            # Adicionar a sentença encontrada
            sentences.append(current[:end_pos + pattern_len])
            
            # Continuar com o resto do texto
            current = current[end_pos + pattern_len:]
        
        rewritten_sentences = []
        
        for sentence in sentences:
            # Aplicar técnicas de paráfrase
            rewritten = self._apply_paraphrase_techniques(sentence)
            rewritten_sentences.append(rewritten)
        
        # Juntar sentenças reescritas
        rewritten_text = ' '.join(rewritten_sentences)
        
        return rewritten_text
    
    def _apply_paraphrase_techniques(self, sentence):
        """
        Aplica técnicas de paráfrase a uma sentença.
        
        Args:
            sentence (str): Sentença original
            
        Returns:
            str: Sentença reescrita
        """
        # Técnicas simples de paráfrase
        techniques = [
            self._change_word_order,
            self._use_synonyms,
            self._change_voice,
            self._simplify_sentence
        ]
        
        # Aplicar uma técnica aleatória
        technique = random.choice(techniques)
        return technique(sentence)
    
    def fetch_image_url(self, query):
        """Busca uma imagem relacionada ao título da notícia usando DuckDuckGo."""
        try:
            search_url = f"https://duckduckgo.com/?q={requests.utils.quote(query)}&iax=images&ia=images"
            headers = self.headers
            res = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")

            # DuckDuckGo carrega as imagens via JavaScript. Precisamos do endpoint real:
            vqd_match = re.search(r'vqd=([\d-]+)\&', res.text)
            if not vqd_match:
                logger.warning("VQD token não encontrado, usando imagem genérica.")
                return "https://via.placeholder.com/800x400?text=Imagem+indisponível"

            vqd = vqd_match.group(1)
            api_url = f"https://duckduckgo.com/i.js?l=us-en&o=json&q={requests.utils.quote(query)}&vqd={vqd}"
            img_res = requests.get(api_url, headers=headers)
            img_json = img_res.json()

            if img_json["results"]:
                return img_json["results"][0]["image"]
            else:
                return "https://via.placeholder.com/800x400?text=Imagem+indisponível"

        except Exception as e:
            logger.error(f"Erro ao buscar imagem: {e}")
            return "https://via.placeholder.com/800x400?text=Imagem+indisponível"
    
    def _change_word_order(self, sentence):
        """Altera a ordem das palavras na sentença."""
        # Exemplo: "O presidente anunciou hoje" -> "Hoje o presidente anunciou"
        words = sentence.split()
        
        # Se a sentença for muito curta, não alterar
        if len(words) < 4:
            return sentence
        
        # Verificar se começa com "O", "A", "Os", "As"
        if words[0].lower() in ['o', 'a', 'os', 'as']:
            # Mover o sujeito para depois do verbo
            if len(words) > 5:
                mid = len(words) // 2
                return ' '.join(words[mid:] + words[:mid])
        
        # Verificar se há advérbios de tempo (hoje, ontem, amanhã)
        time_adverbs = ['hoje', 'ontem', 'amanhã', 'agora']
        for adverb in time_adverbs:
            if adverb in [w.lower() for w in words]:
                idx = [w.lower() for w in words].index(adverb)
                # Mover advérbio para o início
                new_words = [words[idx]] + words[:idx] + words[idx+1:]
                return ' '.join(new_words)
        
        return sentence
    
    def _use_synonyms(self, sentence):
        """Substitui algumas palavras por sinônimos."""
        # Dicionário simples de sinônimos
        synonyms = {
            'disse': ['afirmou', 'declarou', 'comentou', 'relatou', 'explicou'],
            'informou': ['comunicou', 'notificou', 'avisou', 'revelou', 'divulgou'],
            'grande': ['enorme', 'amplo', 'vasto', 'extenso', 'considerável'],
            'importante': ['relevante', 'significativo', 'essencial', 'fundamental', 'crucial'],
            'bom': ['ótimo', 'excelente', 'positivo', 'favorável', 'benéfico'],
            'ruim': ['péssimo', 'negativo', 'desfavorável', 'prejudicial', 'nocivo'],
            'rápido': ['veloz', 'ágil', 'célere', 'ligeiro', 'acelerado'],
            'devagar': ['lento', 'vagaroso', 'pausado', 'gradual', 'moderado'],
            'muito': ['bastante', 'extremamente', 'consideravelmente', 'intensamente', 'demasiadamente'],
            'pouco': ['escasso', 'insuficiente', 'limitado', 'reduzido', 'restrito'],
            'novo': ['recente', 'atual', 'moderno', 'inovador', 'inédito'],
            'velho': ['antigo', 'ultrapassado', 'obsoleto', 'desatualizado', 'tradicional'],
            'problema': ['questão', 'dificuldade', 'obstáculo', 'desafio', 'empecilho'],
            'solução': ['resposta', 'resolução', 'alternativa', 'saída', 'medida'],
            'fazer': ['realizar', 'executar', 'efetuar', 'concretizar', 'implementar'],
            'dizer': ['falar', 'expressar', 'comunicar', 'pronunciar', 'declarar'],
            'ver': ['observar', 'visualizar', 'enxergar', 'perceber', 'notar'],
            'ir': ['dirigir-se', 'deslocar-se', 'encaminhar-se', 'seguir', 'rumar'],
            'começar': ['iniciar', 'principiar', 'dar início', 'inaugurar', 'estrear'],
            'terminar': ['finalizar', 'concluir', 'encerrar', 'acabar', 'completar']
        }
        
        words = sentence.split()
        new_words = []
        
        for word in words:
            word_lower = word.strip('.,;:?!()[]{}""\'').lower()
            
            # Verificar se a palavra está no dicionário de sinônimos
            if word_lower in synonyms:
                # 70% de chance de substituir por um sinônimo
                if random.random() < 0.7:
                    synonym = random.choice(synonyms[word_lower])
                    
                    # Preservar capitalização
                    if word[0].isupper():
                        synonym = synonym.capitalize()
                    
                    # Preservar pontuação
                    if not word[-1].isalnum():
                        synonym += word[-1]
                    
                    new_words.append(synonym)
                else:
                    new_words.append(word)
            else:
                new_words.append(word)
        
        return ' '.join(new_words)
    
    def _change_voice(self, sentence):
        """Tenta alterar a voz da sentença (ativa/passiva)."""
        # Padrões simples para identificar voz ativa
        active_patterns = [
            (r'(\w+) (disse|afirmou|declarou|informou) que', r'Foi dito por \1 que'),
            (r'(\w+) (anunciou|revelou|divulgou) (\w+)', r'\3 foi \2 por \1'),
            (r'(\w+) (criou|desenvolveu|produziu) (\w+)', r'\3 foi \2 por \1')
        ]
        
        # Aplicar padrões
        result = sentence
        for pattern, replacement in active_patterns:
            if re.search(pattern, sentence):
                result = re.sub(pattern, replacement, sentence)
                break
        
        return result
    
    def _simplify_sentence(self, sentence):
        """Simplifica a sentença removendo detalhes menos importantes."""
        # Remover expressões entre parênteses
        simplified = re.sub(r'\([^)]*\)', '', sentence)
        
        # Remover expressões entre vírgulas se forem explicativas
        simplified = re.sub(r', [^,]*?,', ',', simplified)
        
        # Remover advérbios comuns
        adverbs = ['realmente', 'certamente', 'possivelmente', 'provavelmente', 'basicamente', 'essencialmente']
        for adverb in adverbs:
            simplified = re.sub(r'\s' + adverb + r'\s', ' ', simplified)
        
        # Se a simplificação reduziu muito a sentença, manter original
        if len(simplified) < len(sentence) * 0.7:
            return sentence
        
        return simplified
    

    def publish_news(self, news, output_dir):
        """
        Publica uma notícia reescrita, criando arquivos HTML.
        
        Args:
            news (dict): Dados da notícia reescrita
            output_dir (str): Diretório de saída
            
        Returns:
            dict: Informações sobre a publicação
        """
        try:
            # Criar slug para URL a partir do título
            slug = self._create_slug(news['title'])
            
            # Definir caminho do arquivo
            category_dir = os.path.join(output_dir, 'categorias', news['category'])
            os.makedirs(category_dir, exist_ok=True)
            
            # Criar nome de arquivo único com timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{slug}-{timestamp}.html"
            filepath = os.path.join(category_dir, filename)
            
            # Gerar HTML da notícia
            html_content = self._generate_news_html(news)
            
            # Salvar arquivo
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Registrar como publicada
            news_id = hashlib.md5(news['title'].encode()).hexdigest()
            self.published_news[news_id] = {
                'title': news['title'],
                'category': news['category'],
                'source_url': news.get('source_url', ''),
                'filepath': filepath,
                'url_path': f"categorias/{news['category']}/{filename}",
                'publish_timestamp': datetime.now().isoformat()
            }
            
            # Salvar registro atualizado
            self._save_cache()
            
            logger.info(f"Notícia publicada: {news['title']} em {filepath}")
            
            return {
                'title': news['title'],
                'category': news['category'],
                'filepath': filepath,
                'url_path': f"categorias/{news['category']}/{filename}"
            }
            
        except Exception as e:
            logger.error(f"Erro ao publicar notícia: {e}")
            return None
    
    def _create_slug(self, title):
        """Cria um slug a partir do título da notícia."""
        # Remover acentos
        slug = title.lower()
        slug = re.sub(r'[áàãâä]', 'a', slug)
        slug = re.sub(r'[éèêë]', 'e', slug)
        slug = re.sub(r'[íìîï]', 'i', slug)
        slug = re.sub(r'[óòõôö]', 'o', slug)
        slug = re.sub(r'[úùûü]', 'u', slug)
        slug = re.sub(r'[ç]', 'c', slug)
        
        # Remover caracteres especiais e substituir espaços por hífens
        slug = re.sub(r'[^a-z0-9\s]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        
        # Limitar tamanho
        slug = slug[:50]
        
        return slug
    
    def _generate_news_html(self, news):
        """Gera o HTML para uma página de notícia com base no template da pasta categorias."""
        try:
            # Caminho do template base
            template_path = os.path.join("categorias", "template_noticia.html")
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template não encontrado em {template_path}")

            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()

            # Formatar data
            publish_date = datetime.now().strftime("%d/%m/%Y às %H:%M")

            # Limpa conteúdo HTML antes de inserir no template
            content_html = news["content"].strip()

            # Remove caracteres soltos antes de tags HTML
            content_html = re.sub(r'^[^\w<]*', '', content_html)

            # Remove quebras de linha fora de contexto
            content_html = re.sub(r'^\s*\n*', '', content_html)


            # Substituições no template
            template = template.replace("{{TITULO}}", news["title"])
            template = template.replace("{{RESUMO}}", news["content"].split('\n\n')[0])
            template = template.replace("{{DATA}}", publish_date)
            template = template.replace("{{CATEGORIA}}", news["category"])
            template = template.replace("{{IMAGEM_URL}}", news.get("image_url", f"../../images/placeholder-{news['category']}.jpg"))
            template = template.replace("{{IMAGEM_CREDITO}}", "Imagem: BrasilViral")
            template = template.replace("{{CONTEUDO_HTML}}", content_html.strip())
            template = template.replace("{{TAGS}}", f"{news['category']}, brasil, notícias")

            return template
        except Exception as e:
            logger.error(f"Erro ao gerar HTML da notícia: {e}")
            return "<h1>Erro ao gerar conteúdo</h1>"

    
    def get_top_news_for_category(self, category, count=3):
        """
        Obtém as notícias mais virais de uma categoria.
        
        Args:
            category (str): Categoria de notícias
            count (int): Número de notícias a retornar
            
        Returns:
            list: Lista das notícias mais virais publicadas
        """
        # Filtrar notícias publicadas da categoria
        category_news = [
            news for news_id, news in self.published_news.items()
            if news.get('category') == category
        ]
        
        # Ordenar por data de publicação (mais recentes primeiro)
        sorted_news = sorted(
            category_news,
            key=lambda x: x.get('publish_timestamp', ''),
            reverse=True
        )
        
        return sorted_news[:count]

# Função para demonstração


def gerar_noticias_para_site():
    categorias = ["esportes", "economia", "politica", "tecnologia", "entretenimento", "curiosidades"]
    os.makedirs("categorias", exist_ok=True)

    agent = NewsResearchAgent()
    latest_news = {}

    for categoria in categorias:
        print(f"\n🔎 Coletando notícia para: {categoria.upper()}")

        try:
            noticias = agent.search_viral_news(categoria, limit=1)
            if not noticias:
                print(f"⚠️ Nenhuma notícia encontrada para {categoria}. Pulando.")
                continue

            top_news = noticias[0]
            rewritten = agent.rewrite_news(top_news)

            # Publicar a notícia (gera o arquivo HTML na pasta correta)
            resultado_publicacao = agent.publish_news(rewritten, output_dir=".")
            if not resultado_publicacao:
                print(f"⚠️ Falha ao publicar notícia de {categoria}. Pulando.")
                continue


            # Monta o resumo da notícia para o JSON principal
            noticia_resumida = {
                "title": rewritten["title"],
                "summary": rewritten["content"].split('\n\n')[0],
                "timestamp": datetime.now().isoformat(),
                "link": resultado_publicacao["url_path"],
                "image": rewritten.get("image_url", f"images/placeholder-{categoria}.jpg")
            }

            # Salva o resumo individual da categoria
            with open(os.path.join("categorias", f"noticias_{categoria}.json"), "w", encoding="utf-8") as f:
                json.dump([noticia_resumida], f, ensure_ascii=False, indent=2)

            # Adiciona ao dicionário geral
            latest_news[categoria] = noticia_resumida

            print(f"✅ Notícia publicada e salva: {resultado_publicacao['url_path']}")

        except Exception as e:
            print(f"❌ Erro ao processar {categoria}: {e}")

    # Salvar o JSON com as últimas notícias de todas as categorias
    with open("latest_news.json", "w", encoding="utf-8") as f:
        json.dump(latest_news, f, ensure_ascii=False, indent=2)

    print("📦 Arquivo 'latest_news.json' atualizado com as últimas notícias.")


if __name__ == "__main__":
    gerar_noticias_para_site()
