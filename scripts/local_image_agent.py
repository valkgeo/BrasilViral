#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agente de Imagens Simplificado para o BrasilViral
Este script utiliza imagens locais para as notícias, eliminando a dependência de APIs externas.
"""

import os
import json
import random
import logging
import shutil
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("image_search.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LocalImageAgent")

class LocalImageAgent:
    """Agente para gerenciar imagens locais para o site BrasilViral."""
    
    def __init__(self, base_dir="/home/ubuntu/brasilviralsite_images"):
        """
        Inicializa o agente de imagens local.
        
        Args:
            base_dir (str): Diretório base do site
        """
        self.base_dir = base_dir
        self.default_images_dir = os.path.join(base_dir, "images_default")
        self.images_dir = os.path.join(base_dir, "images")
        self.categories = ["esportes", "economia", "politica", "tecnologia", "entretenimento", "curiosidades"]
        self.image_cache = {}
        self.cache_file = os.path.join(base_dir, "image_cache.json")
        
        # Garantir que os diretórios existam
        self._ensure_directories()
        
        # Carregar cache
        self._load_cache()
        
        # Verificar disponibilidade de imagens
        self._check_images()
    
    def _ensure_directories(self):
        """Garante que todos os diretórios necessários existam."""
        # Diretório principal de imagens
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Diretórios para cada categoria
        for category in self.categories:
            os.makedirs(os.path.join(self.images_dir, category), exist_ok=True)
    
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
    
    def _check_images(self):
        """Verifica se há imagens disponíveis para todas as categorias."""
        for category in self.categories:
            default_category_dir = os.path.join(self.default_images_dir, category)
            if not os.path.exists(default_category_dir):
                logger.warning(f"Diretório de imagens padrão não encontrado para categoria: {category}")
                continue
                
            images = [f for f in os.listdir(default_category_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
            logger.info(f"Categoria {category}: {len(images)} imagens padrão disponíveis")
    
    def get_image_for_news(self, title, content, category, force_refresh=False):
        """
        Obtém uma imagem relevante para uma notícia.
        
        Args:
            title (str): Título da notícia
            content (str): Conteúdo da notícia
            category (str): Categoria da notícia
            force_refresh (bool): Se True, ignora o cache e seleciona uma nova imagem
            
        Returns:
            dict: Informações da imagem selecionada
        """
        # Normalizar categoria
        category = category.lower()
        if category not in self.categories:
            logger.warning(f"Categoria desconhecida: {category}. Usando 'curiosidades' como padrão.")
            category = "curiosidades"
        
        # Criar uma chave única para esta notícia
        cache_key = f"{title[:50]}_{category}"
        
        # Verificar se já temos uma imagem em cache para esta notícia
        if not force_refresh and cache_key in self.image_cache:
            logger.info(f"Imagem encontrada no cache para: {title[:30]}...")
            return self.image_cache[cache_key]
        
        # Diretório de imagens padrão para esta categoria
        default_category_dir = os.path.join(self.default_images_dir, category)
        
        # Verificar se o diretório existe
        if not os.path.exists(default_category_dir):
            logger.error(f"Diretório de imagens padrão não encontrado para categoria: {category}")
            # Usar uma categoria alternativa
            default_category_dir = os.path.join(self.default_images_dir, "curiosidades")
        
        # Listar todas as imagens disponíveis para esta categoria
        available_images = [f for f in os.listdir(default_category_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        
        if not available_images:
            logger.error(f"Nenhuma imagem encontrada para categoria: {category}")
            return {
                'url': f"images/placeholder-default.jpg",
                'thumbnail': f"images/placeholder-default.jpg",
                'source': 'Padrão',
                'source_url': '',
                'width': 800,
                'height': 600,
                'is_default': True,
                'category': category
            }
        
        # Selecionar uma imagem aleatória
        selected_image_file = random.choice(available_images)
        selected_image_path = os.path.join(default_category_dir, selected_image_file)
        
        # Determinar o tipo de imagem (abstract, icon, geometric)
        image_type = "padrão"
        if "abstract" in selected_image_file:
            image_type = "abstrato"
        elif "icon" in selected_image_file:
            image_type = "ícone"
        elif "geometric" in selected_image_file:
            image_type = "geométrico"
        
        # Criar um nome único para a imagem no site
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{category}_{image_type}_{timestamp}.png"
        destination_path = os.path.join(self.images_dir, category, unique_filename)
        
        # Copiar a imagem para o diretório de imagens do site
        try:
            shutil.copy2(selected_image_path, destination_path)
            logger.info(f"Imagem copiada para: {destination_path}")
            
            # Caminho relativo para uso no HTML
            relative_path = os.path.join("images", category, unique_filename)
            
            # Informações da imagem
            image_info = {
                'url': relative_path,
                'thumbnail': relative_path,
                'source': 'BrasilViral',
                'source_url': '',
                'width': 800,  # Valores padrão
                'height': 600,  # Valores padrão
                'is_default': False,
                'category': category,
                'type': image_type,
                'credit': f"Ilustração: BrasilViral - {category.capitalize()} ({image_type})"
            }
            
            # Armazenar no cache
            self.image_cache[cache_key] = image_info
            self._save_cache()
            
            return image_info
            
        except Exception as e:
            logger.error(f"Erro ao copiar imagem: {e}")
            # Retornar caminho direto para a imagem original em caso de erro
            return {
                'url': os.path.join("images_default", category, selected_image_file),
                'thumbnail': os.path.join("images_default", category, selected_image_file),
                'source': 'BrasilViral',
                'source_url': '',
                'width': 800,
                'height': 600,
                'is_default': False,
                'category': category,
                'type': image_type,
                'credit': f"Ilustração: BrasilViral - {category.capitalize()} ({image_type})"
            }
    
    def update_index_images(self):
        """
        Atualiza as imagens na página inicial do site.
        
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        try:
            index_html_path = os.path.join(self.base_dir, "index.html")
            
            # Verificar se o arquivo existe
            if not os.path.exists(index_html_path):
                logger.error(f"Arquivo index.html não encontrado em: {index_html_path}")
                return False
            
            # Ler o conteúdo atual
            with open(index_html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Para cada categoria, selecionar uma imagem aleatória
            for category in self.categories:
                # Gerar uma notícia fictícia para obter uma imagem
                dummy_title = f"Notícia de {category}"
                dummy_content = f"Conteúdo de exemplo para a categoria {category}"
                
                # Obter uma imagem
                image_info = self.get_image_for_news(dummy_title, dummy_content, category, force_refresh=True)
                
                # Substituir no HTML
                # Procurar por padrões como: <img src="images/placeholder-esportes.jpg" alt="Esportes">
                placeholder_pattern = f'<img src="images/placeholder-{category}.jpg"'
                replacement = f'<img src="{image_info["url"]}"'
                
                # Também procurar por outros padrões de imagem para esta categoria
                alt_pattern = f'alt="{category.capitalize()}"'
                
                # Substituir todas as ocorrências
                if placeholder_pattern in content:
                    content = content.replace(placeholder_pattern, replacement)
                    logger.info(f"Substituída imagem placeholder para categoria: {category}")
                elif alt_pattern in content:
                    # Encontrar a tag img completa e substituir
                    import re
                    img_pattern = re.compile(f'<img[^>]*{alt_pattern}[^>]*>')
                    matches = img_pattern.findall(content)
                    for match in matches:
                        new_img = f'<img src="{image_info["url"]}" alt="{category.capitalize()}" class="card-img-top">'
                        content = content.replace(match, new_img)
                    logger.info(f"Substituídas {len(matches)} imagens para categoria: {category}")
            
            # Salvar o conteúdo atualizado
            with open(index_html_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info("Imagens da página inicial atualizadas com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar imagens da página inicial: {e}")
            return False
    
    def process_news_images(self, news_dir):
        """
        Processa imagens para todas as notícias em um diretório.
        
        Args:
            news_dir (str): Diretório contendo arquivos HTML de notícias
            
        Returns:
            int: Número de notícias processadas
        """
        try:
            # Verificar se o diretório existe
            if not os.path.exists(news_dir):
                logger.error(f"Diretório de notícias não encontrado: {news_dir}")
                return 0
            
            # Listar todos os arquivos HTML
            html_files = [f for f in os.listdir(news_dir) if f.endswith('.html')]
            
            count = 0
            for html_file in html_files:
                file_path = os.path.join(news_dir, html_file)
                
                # Ler o conteúdo
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extrair título, conteúdo e categoria
                import re
                title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content)
                title = title_match.group(1) if title_match else "Notícia sem título"
                
                # Extrair categoria do nome do arquivo ou do conteúdo
                category = None
                for cat in self.categories:
                    if cat in html_file.lower():
                        category = cat
                        break
                
                if not category:
                    # Tentar extrair do conteúdo
                    for cat in self.categories:
                        if cat in content.lower():
                            category = cat
                            break
                
                if not category:
                    category = "curiosidades"  # Categoria padrão
                
                # Extrair um trecho do conteúdo
                content_match = re.search(r'<div class="news-content">(.*?)</div>', content, re.DOTALL)
                news_content = content_match.group(1) if content_match else ""
                
                # Obter uma imagem
                image_info = self.get_image_for_news(title, news_content, category)
                
                # Substituir a imagem no HTML
                img_pattern = re.compile(r'<img[^>]*class="news-image"[^>]*>')
                matches = img_pattern.findall(content)
                
                if matches:
                    new_img = f'<img src="{image_info["url"]}" alt="{title}" class="news-image">'
                    content = content.replace(matches[0], new_img)
                    
                    # Adicionar crédito da imagem
                    if 'credit' in image_info:
                        credit_html = f'<div class="image-credit">{image_info["credit"]}</div>'
                        content = content.replace(new_img, new_img + credit_html)
                    
                    # Salvar o arquivo atualizado
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    count += 1
                    logger.info(f"Imagem atualizada para notícia: {html_file}")
                else:
                    logger.warning(f"Nenhuma imagem encontrada para substituir em: {html_file}")
            
            logger.info(f"Total de {count} notícias processadas")
            return count
            
        except Exception as e:
            logger.error(f"Erro ao processar imagens de notícias: {e}")
            return 0


# Função para demonstração
def demo():
    """Demonstra o uso do agente de imagens local."""
    agent = LocalImageAgent()
    
    # Atualizar imagens da página inicial
    print("Atualizando imagens da página inicial...")
    agent.update_index_images()
    
    # Exemplos de notícias
    news_samples = [
        {
            'title': 'Lula anuncia novo pacote de investimentos para o Nordeste',
            'content': 'O presidente Lula anunciou hoje um novo pacote de investimentos para o Nordeste, com foco em infraestrutura e energia renovável. O pacote prevê a liberação de R$ 30 bilhões para obras em rodovias, portos e aeroportos, além de incentivos para a instalação de parques eólicos e solares na região.',
            'category': 'politica'
        },
        {
            'title': 'Neymar marca três gols em retorno aos gramados após lesão',
            'content': 'Neymar voltou a jogar após oito meses afastado por lesão e marcou três gols na vitória de sua equipe. O craque brasileiro mostrou que está recuperado e pronto para ajudar tanto seu clube quanto a seleção brasileira nos próximos compromissos.',
            'category': 'esportes'
        },
        {
            'title': 'Nova tecnologia promete revolucionar tratamento contra o câncer',
            'content': 'Cientistas desenvolveram uma nova tecnologia que utiliza inteligência artificial para identificar células cancerígenas com precisão muito superior aos métodos atuais. Os testes iniciais mostram uma eficácia de 95% na detecção precoce de tumores.',
            'category': 'tecnologia'
        }
    ]
    
    # Testar o agente com as amostras
    for news in news_samples:
        print(f"\nBuscando imagem para: {news['title']}")
        image = agent.get_image_for_news(news['title'], news['content'], news['category'])
        print(f"Imagem selecionada: {image['url']}")
        print(f"Crédito: {image.get('credit', 'Sem crédito')}")
    
    print("\nDemo concluída!")

if __name__ == "__main__":
    demo()
