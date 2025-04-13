#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pipeline de Geração de Conteúdo para o BrasilViral
Este script integra todos os componentes para criar um fluxo completo de geração e publicação de conteúdo.
"""

import os
import sys
import json
import time
import random
import logging
import argparse
import datetime
from pathlib import Path

# Importar os agentes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from image_search_agent import ImageSearchAgent
from news_research_agent import NewsResearchAgent
from automation_agent import AutomationAgent

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("content_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ContentPipeline")

# Categorias suportadas pelo site
CATEGORIES = [
    'esportes', 'economia', 'politica', 
    'tecnologia', 'entretenimento', 'curiosidades'
]

class ContentPipeline:
    """Pipeline para geração e publicação de conteúdo."""
    
    def __init__(self, base_dir):
        """
        Inicializa o pipeline de conteúdo.
        
        Args:
            base_dir (str): Diretório base do site
        """
        self.base_dir = base_dir
        self.image_agent = ImageSearchAgent()
        self.news_agent = NewsResearchAgent()
        self.automation_agent = AutomationAgent(base_dir)
        
        # Criar diretórios necessários
        self.create_directories()
        
        # Carregar configuração
        self.config_file = os.path.join(base_dir, "scripts", "pipeline_config.json")
        self.load_config()
    
    def create_directories(self):
        """Cria os diretórios necessários para o site."""
        # Diretórios principais
        dirs = [
            os.path.join(self.base_dir, "images"),
            os.path.join(self.base_dir, "css"),
            os.path.join(self.base_dir, "js"),
            os.path.join(self.base_dir, "scripts")
        ]
        
        # Diretórios de categorias
        for category in CATEGORIES:
            dirs.append(os.path.join(self.base_dir, "categorias", category))
            dirs.append(os.path.join(self.base_dir, "images", category))
        
        # Criar diretórios
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Diretório criado/verificado: {directory}")
    
    def load_config(self):
        """Carrega a configuração do pipeline."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"Configuração carregada: {self.config}")
            else:
                # Configuração padrão
                self.config = {
                    "batch_size": 5,  # Número de notícias a processar por vez
                    "min_viral_score": 20,  # Pontuação mínima de viralidade
                    "max_duplicates": 3,  # Máximo de notícias similares permitidas
                    "image_refresh_days": 7,  # Dias para atualizar imagens
                    "categories": CATEGORIES,
                    "last_run": None
                }
                self.save_config()
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            # Configuração padrão em caso de erro
            self.config = {
                "batch_size": 5,
                "min_viral_score": 20,
                "max_duplicates": 3,
                "image_refresh_days": 7,
                "categories": CATEGORIES,
                "last_run": None
            }
    
    def save_config(self):
        """Salva a configuração do pipeline."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"Configuração salva: {self.config}")
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
    
    def update_config(self, **kwargs):
        """
        Atualiza a configuração do pipeline.
        
        Args:
            **kwargs: Pares chave-valor para atualizar na configuração
        """
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
        self.save_config()
    
    def generate_category_index(self, category):
        """
        Gera a página de índice para uma categoria.
        
        Args:
            category (str): Categoria para gerar o índice
            
        Returns:
            bool: True se a geração foi bem-sucedida, False caso contrário
        """
        try:
            logger.info(f"Gerando página de índice para categoria: {category}")
            
            # Obter as notícias mais recentes da categoria
            category_news = self.news_agent.get_top_news_for_category(category, count=10)
            
            if not category_news:
                logger.warning(f"Nenhuma notícia encontrada para categoria: {category}")
                return False
            
            # Caminho para o arquivo de índice
            index_path = os.path.join(self.base_dir, "categorias", category, "index.html")
            
            # Gerar HTML para a página de índice
            html_content = self._generate_category_index_html(category, category_news)
            
            # Salvar arquivo
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Página de índice gerada para categoria: {category}")
            return True
        except Exception as e:
            logger.error(f"Erro ao gerar página de índice para categoria {category}: {e}")
            return False
    
    def _generate_category_index_html(self, category, news_list):
        """
        Gera o HTML para a página de índice de uma categoria.
        
        Args:
            category (str): Nome da categoria
            news_list (list): Lista de notícias da categoria
            
        Returns:
            str: HTML da página de índice
        """
        # Mapear categoria para nome em português
        category_names = {
            'esportes': 'Esportes',
            'economia': 'Economia',
            'politica': 'Política',
            'tecnologia': 'Tecnologia',
            'entretenimento': 'Entretenimento',
            'curiosidades': 'Curiosidades'
        }
        
        category_name = category_names.get(category, category.capitalize())
        
        # Gerar HTML para as notícias
        news_html = ""
        for news in news_list:
            news_html += f"""
            <article class="article-card" data-link="{news.get('url_path', '#')}">
                <div class="article-image">
                    <img src="../../images/placeholder-{category}.jpg" alt="{news.get('title', 'Notícia')}">
                </div>
                <div class="article-content">
                    <h3>{news.get('title', 'Título da notícia')}</h3>
                    <span class="post-date"><i class="far fa-clock"></i> {self._format_date(news.get('publish_timestamp', ''))}</span>
                </div>
            </article>
            """
        
        # Template HTML para a página de índice
        html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{category_name} - BrasilViral</title>
    <link rel="stylesheet" href="../../css/style.css">
    <link rel="stylesheet" href="../../css/ads.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <meta name="description" content="Notícias de {category_name.lower()} que estão bombando no Brasil e no mundo.">
    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1234567890123456" crossorigin="anonymous"></script>
</head>
<body>
    <header>
        <div class="container">
            <div class="logo">
                <h1><a href="../../index.html">Brasil<span>Viral</span></a></h1>
                <p class="slogan">Notícias que Bombam</p>
            </div>
            <nav class="main-nav">
                <button class="menu-toggle" id="menuToggle">
                    <i class="fas fa-bars"></i>
                </button>
                <ul class="nav-menu" id="navMenu">
                    <li><a href="../../index.html">Home</a></li>
                    <li><a href="../../categorias/esportes/index.html" class="{category == 'esportes' and 'active' or ''}">Esportes</a></li>
                    <li><a href="../../categorias/economia/index.html" class="{category == 'economia' and 'active' or ''}">Economia</a></li>
                    <li><a href="../../categorias/politica/index.html" class="{category == 'politica' and 'active' or ''}">Política</a></li>
                    <li><a href="../../categorias/tecnologia/index.html" class="{category == 'tecnologia' and 'active' or ''}">Tecnologia</a></li>
                    <li><a href="../../categorias/entretenimento/index.html" class="{category == 'entretenimento' and 'active' or ''}">Entretenimento</a></li>
                    <li><a href="../../categorias/curiosidades/index.html" class="{category == 'curiosidades' and 'active' or ''}">Curiosidades</a></li>
                </ul>
            </nav>
            <div class="search-box">
                <input type="text" placeholder="Buscar notícias...">
                <button><i class="fas fa-search"></i></button>
            </div>
        </div>
    </header>

    <div class="breaking-news">
        <div class="container">
            <span class="breaking-label">ÚLTIMAS:</span>
            <div class="breaking-text" id="breakingNews">
                Dólar atinge maior valor do ano • Novo técnico da seleção brasileira será anunciado hoje • Problemas no WhatsApp afetam milhões de usuários
            </div>
        </div>
    </div>

    <main class="container main-content">
        <div class="category-header">
            <h1><i class="fas fa-{self._get_category_icon(category)}"></i> {category_name}</h1>
            <p>As notícias mais virais de {category_name.lower()} que estão bombando no Brasil e no mundo.</p>
        </div>
        
        <div class="content-sidebar-wrapper">
            <div class="main-content-area">
                <section class="category-articles">
                    {news_html}
                </section>
                
                <div class="pagination">
                    <span class="current-page">Página 1</span>
                    <a href="#" class="next-page">Próxima <i class="fas fa-angle-right"></i></a>
                </div>
            </div>
            
            <aside class="sidebar">
                <div class="sidebar-widget trending">
                    <h3><i class="fas fa-fire"></i> Em Alta</h3>
                    <ul class="trending-list" id="trendingNews">
                        <li>
                            <div class="trending-item">
                                <div class="trending-number">1</div>
                                <div class="trending-title"><a href="#">Lua cheia rosa ilumina céu brasileiro neste fim de semana</a></div>
                            </div>
                        </li>
                        <li>
                            <div class="trending-item">
                                <div class="trending-number">2</div>
                                <div class="trending-title"><a href="#">The Last of Us: 2ª temporada ganha primeiras imagens</a></div>
                            </div>
                        </li>
                        <li>
                            <div class="trending-item">
                                <div class="trending-number">3</div>
                                <div class="trending-title"><a href="#">Dólar atinge R$ 5,87 e bate recorde do ano</a></div>
                            </div>
                        </li>
                        <li>
                            <div class="trending-item">
                                <div class="trending-number">4</div>
                                <div class="trending-title"><a href="#">Resultado da Quina 6704: veja os números sorteados</a></div>
                            </div>
                        </li>
                        <li>
                            <div class="trending-item">
                                <div class="trending-number">5</div>
                                <div class="trending-title"><a href="#">WhatsApp fora do ar: usuários relatam problemas no aplicativo</a></div>
                            </div>
                        </li>
                    </ul>
                </div>

                <div id="sidebar-top" class="ad-slot sidebar-widget">
                    <div class="ad-placeholder">
                        <span>Anúncio</span>
                    </div>
                </div>

                <div class="sidebar-widget newsletter">
                    <h3><i class="far fa-envelope"></i> Newsletter</h3>
                    <p>Receba as principais notícias diretamente no seu email</p>
                    <form id="newsletterForm">
                        <input type="email" placeholder="Seu melhor email" required>
                        <button type="submit">Inscrever-se</button>
                    </form>
                </div>

                <div id="sidebar-bottom" class="ad-slot sidebar-widget">
                    <div class="ad-placeholder">
                        <span>Anúncio</span>
                    </div>
                </div>
            </aside>
        </div>
    </main>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-logo">
                    <h2>Brasil<span>Viral</span></h2>
                    <p>O seu portal de notícias virais do Brasil</p>
                </div>
                <div class="footer-links">
                    <h3>Links Rápidos</h3>
                    <ul>
                        <li><a href="../../index.html">Home</a></li>
                        <li><a href="../../categorias/esportes/index.html">Esportes</a></li>
                        <li><a href="../../categorias/economia/index.html">Economia</a></li>
                        <li><a href="../../categorias/politica/index.html">Política</a></li>
                        <li><a href="../../categorias/tecnologia/index.html">Tecnologia</a></li>
                        <li><a href="../../categorias/entretenimento/index.html">Entretenimento</a></li>
                        <li><a href="../../categorias/curiosidades/index.html">Curiosidades</a></li>
                    </ul>
                </div>
                <div class="footer-info">
                    <h3>Informações</h3>
                    <ul>
                        <li><a href="../../sobre.html">Quem Somos</a></li>
                        <li><a href="../../contato.html">Contato</a></li>
                        <li><a href="../../politica-privacidade.html">Política de Privacidade</a></li>
                        <li><a href="../../termos-uso.html">Termos de Uso</a></li>
                    </ul>
                </div>
                <div class="footer-social">
                    <h3>Redes Sociais</h3>
                    <div class="social-icons">
                        <a href="#" target="_blank"><i class="fab fa-facebook-f"></i></a>
                        <a href="#" target="_blank"><i class="fab fa-twitter"></i></a>
                        <a href="#" target="_blank"><i class="fab fa-instagram"></i></a>
                        <a href="#" target="_blank"><i class="fab fa-youtube"></i></a>
                    </div>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2025 BrasilViral. Todos os direitos reservados.</p>
            </div>
        </div>
    </footer>

    <script src="../../js/main.js"></script>
    <script src="../../js/adsense.js"></script>
</body>
</html>
"""
        
        return html_template
    
    def _format_date(self, timestamp_str):
        """
        Formata uma data ISO para exibição.
        
        Args:
            timestamp_str (str): String de timestamp ISO
            
        Returns:
            str: Data formatada
        """
        if not timestamp_str:
            return "Recentemente"
        
        try:
            dt = datetime.datetime.fromisoformat(timestamp_str)
            now = datetime.datetime.now()
            diff = now - dt
            
            if diff.days == 0:
                hours = diff.seconds // 3600
                if hours == 0:
                    minutes = diff.seconds // 60
                    return f"Há {minutes} minutos"
                return f"Há {hours} horas"
            elif diff.days == 1:
                return "Ontem"
            else:
                return dt.strftime("%d/%m/%Y")
        except Exception:
            return "Recentemente"
    
    def _get_category_icon(self, category):
        """
        Retorna o ícone FontAwesome para uma categoria.
        
        Args:
            category (str): Nome da categoria
            
        Returns:
            str: Nome do ícone FontAwesome
        """
        icons = {
            'esportes': 'futbol',
            'economia': 'chart-line',
            'politica': 'landmark',
            'tecnologia': 'microchip',
            'entretenimento': 'film',
            'curiosidades': 'lightbulb'
        }
        
        return icons.get(category, 'newspaper')
    
    def generate_all_category_indexes(self):
        """
        Gera páginas de índice para todas as categorias.
        
        Returns:
            bool: True se todas as gerações foram bem-sucedidas, False caso contrário
        """
        success = True
        for category in self.config.get("categories", CATEGORIES):
            if not self.generate_category_index(category):
                success = False
        
        return success
    
    def run_content_generation(self, category=None, count=5):
        """
        Executa o pipeline de geração de conteúdo.
        
        Args:
            category (str, optional): Categoria específica para gerar conteúdo. Se None, gera para todas.
            count (int): Número de notícias a gerar por categoria
            
        Returns:
            dict: Estatísticas de geração
        """
        stats = {
            "total_generated": 0,
            "total_published": 0,
            "categories": {},
            "start_time": datetime.datetime.now().isoformat(),
            "end_time": None
        }
        
        try:
            logger.info(f"Iniciando pipeline de geração de conteúdo para {'todas as categorias' if category is None else category}")
            
            # Determinar categorias a processar
            categories_to_process = [category] if category else self.config.get("categories", CATEGORIES)
            
            # Processar cada categoria
            for cat in categories_to_process:
                logger.info(f"Processando categoria: {cat}")
                cat_stats = {"generated": 0, "published": 0, "errors": 0}
                
                # Pesquisar notícias virais
                news_list = self.news_agent.search_viral_news(cat, limit=count)
                
                if not news_list:
                    logger.warning(f"Nenhuma notícia encontrada para categoria: {cat}")
                    stats["categories"][cat] = cat_stats
                    continue
                
                # Filtrar por pontuação de viralidade
                min_score = self.config.get("min_viral_score", 20)
                viral_news = [news for news in news_list if news.get('viral_score', 0) >= min_score]
                
                if not viral_news:
                    logger.warning(f"Nenhuma notícia com pontuação de viralidade >= {min_score} para categoria: {cat}")
                    stats["categories"][cat] = cat_stats
                    continue
                
                # Processar cada notícia
                for news in viral_news[:count]:
                    try:
                        # Reescrever a notícia
                        rewritten_news = self.news_agent.rewrite_news(news)
                        cat_stats["generated"] += 1
                        
                        # Buscar imagem para a notícia
                        image_info = self.image_agent.get_image_for_news(
                            rewritten_news['title'], 
                            rewritten_news['content'], 
                            cat
                        )
                        
                        # Criar diretório para imagens da categoria se não existir
                        category_images_dir = os.path.join(self.base_dir, "images", cat)
                        os.makedirs(category_images_dir, exist_ok=True)
                        
                        # Gerar nome de arquivo para a imagem
                        image_filename = f"{int(time.time())}_{cat}.jpg"
                        image_path = os.path.join(category_images_dir, image_filename)
                        
                        # Baixar a imagem
                        if not image_info.get('is_default', False):
                            self.image_agent.download_image(image_info, image_path)
                            image_url = f"../../images/{cat}/{image_filename}"
                        else:
                            # Usar imagem padrão
                            image_url = f"../../images/placeholder-{cat}.jpg"
                        
                        # Publicar a notícia
                        publish_info = self.news_agent.publish_news(rewritten_news, self.base_dir)
                        
                        if publish_info:
                            # Atualizar a imagem na página da notícia
                            self.automation_agent.update_news_image(publish_info['filepath'], image_url)
                            cat_stats["published"] += 1
                            logger.info(f"Notícia publicada: {publish_info['title']}")
                        else:
                            logger.error(f"Falha ao publicar notícia: {rewritten_news['title']}")
                            cat_stats["errors"] += 1
                    
                    except Exception as e:
                        logger.error(f"Erro ao processar notícia: {e}")
                        cat_stats["errors"] += 1
                
                # Atualizar estatísticas da categoria
                stats["categories"][cat] = cat_stats
                stats["total_generated"] += cat_stats["generated"]
                stats["total_published"] += cat_stats["published"]
                
                # Gerar página de índice da categoria
                self.generate_category_index(cat)
            
            # Atualizar a página inicial
            self.automation_agent.update_index_page()
            
            # Registrar última execução
            self.config["last_run"] = datetime.datetime.now().isoformat()
            self.save_config()
            
            # Finalizar estatísticas
            stats["end_time"] = datetime.datetime.now().isoformat()
            logger.info(f"Pipeline de geração de conteúdo concluído. Estatísticas: {stats}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro no pipeline de geração de conteúdo: {e}")
            stats["end_time"] = datetime.datetime.now().isoformat()
            stats["error"] = str(e)
            return stats
    
    def start_automation(self):
        """
        Inicia o agendador de automação.
        
        Returns:
            bool: True se o agendador foi iniciado com sucesso, False caso contrário
        """
        try:
            # Configurar agendamento
            self.automation_agent.setup_schedule()
            
            # Iniciar como daemon
            result = self.automation_agent.start_as_daemon()
            
            return result
        except Exception as e:
            logger.error(f"Erro ao iniciar automação: {e}")
            return False
    
    def stop_automation(self):
        """
        Para o agendador de automação.
        
        Returns:
            bool: True se o agendador foi parado com sucesso, False caso contrário
        """
        try:
            result = self.automation_agent.stop_daemon()
            return result
        except Exception as e:
            logger.error(f"Erro ao parar automação: {e}")
            return False


# Função principal
def main():
    """Função principal para execução via linha de comando."""
    parser = argparse.ArgumentParser(description='Pipeline de Geração de Conteúdo para o BrasilViral')
    parser.add_argument('--base-dir', type=str, default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        help='Diretório base do site')
    parser.add_argument('--category', type=str, choices=CATEGORIES, 
                        help='Categoria específica para gerar conteúdo')
    parser.add_argument('--count', type=int, default=5,
                        help='Número de notícias a gerar por categoria')
    parser.add_argument('--start-automation', action='store_true',
                        help='Iniciar o agendador de automação')
    parser.add_argument('--stop-automation', action='store_true',
                        help='Parar o agendador de automação')
    parser.add_argument('--generate-indexes', action='store_true',
                        help='Gerar páginas de índice para todas as categorias')
    
    args = parser.parse_args()
    
    # Criar pipeline
    pipeline = ContentPipeline(args.base_dir)
    
    # Executar ações conforme argumentos
    if args.start_automation:
        print("Iniciando agendador de automação...")
        if pipeline.start_automation():
            print("Agendador iniciado com sucesso!")
        else:
            print("Falha ao iniciar agendador.")
    
    elif args.stop_automation:
        print("Parando agendador de automação...")
        if pipeline.stop_automation():
            print("Agendador parado com sucesso!")
        else:
            print("Falha ao parar agendador.")
    
    elif args.generate_indexes:
        print("Gerando páginas de índice para todas as categorias...")
        if pipeline.generate_all_category_indexes():
            print("Páginas de índice geradas com sucesso!")
        else:
            print("Houve erros ao gerar algumas páginas de índice.")
    
    else:
        # Executar pipeline de geração de conteúdo
        print(f"Executando pipeline de geração de conteúdo para {'todas as categorias' if args.category is None else args.category}...")
        stats = pipeline.run_content_generation(args.category, args.count)
        
        # Exibir estatísticas
        print("\nEstatísticas de geração:")
        print(f"Total de notícias geradas: {stats['total_generated']}")
        print(f"Total de notícias publicadas: {stats['total_published']}")
        
        for cat, cat_stats in stats.get("categories", {}).items():
            print(f"\nCategoria: {cat}")
            print(f"  Geradas: {cat_stats.get('generated', 0)}")
            print(f"  Publicadas: {cat_stats.get('published', 0)}")
            print(f"  Erros: {cat_stats.get('errors', 0)}")


# Função para demonstração
def demo():
    """Demonstra o uso do pipeline de conteúdo."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pipeline = ContentPipeline(base_dir)
    
    print("Configuração atual:")
    print(json.dumps(pipeline.config, indent=2))
    
    print("\nGerando página de índice para categoria 'tecnologia':")
    result = pipeline.generate_category_index("tecnologia")
    print(f"Resultado: {'Sucesso' if result else 'Falha'}")
    
    print("\nPara executar o pipeline completo:")
    print("pipeline.run_content_generation()")
    
    print("\nPara iniciar a automação:")
    print("pipeline.start_automation()")
    
    print("\nPara parar a automação:")
    print("pipeline.stop_automation()")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        demo()
