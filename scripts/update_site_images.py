#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para atualizar o site BrasilViral para usar o agente de imagens local.
Este script integra o agente de imagens local ao site e atualiza as referências de imagens.
"""

import os
import sys
import re
import shutil
import logging
from local_image_agent import LocalImageAgent

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("site_update.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SiteUpdater")

class SiteUpdater:
    """Classe para atualizar o site BrasilViral para usar o agente de imagens local."""
    
    def __init__(self, base_dir="/home/ubuntu/brasilviralsite_images"):
        """
        Inicializa o atualizador de site.
        
        Args:
            base_dir (str): Diretório base do site
        """
        self.base_dir = base_dir
        self.image_agent = LocalImageAgent(base_dir)
        self.categories = ["esportes", "economia", "politica", "tecnologia", "entretenimento", "curiosidades"]
        
    def update_index_page(self):
        """
        Atualiza a página inicial para usar imagens locais.
        
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        try:
            # Usar o método do agente de imagens para atualizar a página inicial
            result = self.image_agent.update_index_images()
            if result:
                logger.info("Página inicial atualizada com sucesso")
            else:
                logger.error("Falha ao atualizar a página inicial")
            return result
        except Exception as e:
            logger.error(f"Erro ao atualizar página inicial: {e}")
            return False
    
    def update_category_pages(self):
        """
        Atualiza as páginas de categorias para usar imagens locais.
        
        Returns:
            int: Número de páginas de categorias atualizadas
        """
        try:
            count = 0
            categories_dir = os.path.join(self.base_dir, "categorias")
            
            if not os.path.exists(categories_dir):
                logger.error(f"Diretório de categorias não encontrado: {categories_dir}")
                return 0
            
            # Para cada categoria
            for category in self.categories:
                category_dir = os.path.join(categories_dir, category)
                
                # Se o diretório da categoria não existir, criar
                if not os.path.exists(category_dir):
                    os.makedirs(category_dir, exist_ok=True)
                    logger.info(f"Diretório criado para categoria: {category}")
                
                # Processar arquivos HTML nesta categoria
                html_files = [f for f in os.listdir(category_dir) if f.endswith('.html')]
                
                if html_files:
                    # Processar cada arquivo HTML
                    for html_file in html_files:
                        file_path = os.path.join(category_dir, html_file)
                        
                        # Ler o conteúdo
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Extrair título
                        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content)
                        title = title_match.group(1) if title_match else f"Notícia de {category}"
                        
                        # Extrair conteúdo
                        content_match = re.search(r'<div class="news-content">(.*?)</div>', content, re.DOTALL)
                        news_content = content_match.group(1) if content_match else ""
                        
                        # Obter uma imagem
                        image_info = self.image_agent.get_image_for_news(title, news_content, category)
                        
                        # Substituir a imagem no HTML
                        img_pattern = re.compile(r'<img[^>]*class="[^"]*news-image[^"]*"[^>]*>')
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
                else:
                    # Se não houver arquivos HTML, criar um arquivo de exemplo
                    template_path = os.path.join(categories_dir, "template_noticia.html")
                    
                    if os.path.exists(template_path):
                        # Ler o template
                        with open(template_path, 'r', encoding='utf-8') as f:
                            template = f.read()
                        
                        # Criar uma notícia de exemplo
                        title = f"Exemplo de notícia de {category}"
                        content = f"<p>Este é um exemplo de notícia para a categoria {category}.</p>"
                        
                        # Substituir placeholders no template
                        template = template.replace("{{TITULO}}", title)
                        template = template.replace("{{CONTEUDO}}", content)
                        template = template.replace("{{CATEGORIA}}", category.capitalize())
                        template = template.replace("{{DATA}}", "12 de Abril de 2025")
                        
                        # Obter uma imagem
                        image_info = self.image_agent.get_image_for_news(title, content, category)
                        template = template.replace("{{IMAGEM}}", image_info["url"])
                        
                        # Adicionar crédito da imagem
                        if 'credit' in image_info:
                            credit_html = f'<div class="image-credit">{image_info["credit"]}</div>'
                            template = template.replace('<img src="{{IMAGEM}}"', f'<img src="{image_info["url"]}"')
                            template = template.replace('class="news-image">', 'class="news-image">' + credit_html)
                        
                        # Salvar o arquivo de exemplo
                        example_path = os.path.join(category_dir, f"exemplo_{category}.html")
                        with open(example_path, 'w', encoding='utf-8') as f:
                            f.write(template)
                        
                        count += 1
                        logger.info(f"Criado arquivo de exemplo para categoria: {category}")
            
            logger.info(f"Total de {count} páginas de categorias atualizadas")
            return count
        except Exception as e:
            logger.error(f"Erro ao atualizar páginas de categorias: {e}")
            return 0
    
    def update_template(self):
        """
        Atualiza o template de notícias para incluir suporte a créditos de imagens.
        
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        try:
            template_path = os.path.join(self.base_dir, "categorias", "template_noticia.html")
            
            if not os.path.exists(template_path):
                logger.error(f"Template de notícia não encontrado: {template_path}")
                return False
            
            # Ler o template
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Verificar se já tem suporte para créditos de imagens
            if 'class="image-credit"' in template:
                logger.info("Template já tem suporte para créditos de imagens")
                return True
            
            # Adicionar CSS para créditos de imagens
            css_style = """
    <style>
        .image-credit {
            font-size: 0.8em;
            color: #666;
            text-align: right;
            margin-top: 5px;
            font-style: italic;
        }
    </style>
"""
            # Inserir o CSS no head
            if '</head>' in template:
                template = template.replace('</head>', css_style + '</head>')
            
            # Salvar o template atualizado
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template)
            
            logger.info("Template atualizado com suporte para créditos de imagens")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar template: {e}")
            return False
    
    def update_css(self):
        """
        Atualiza os arquivos CSS para incluir estilos para créditos de imagens.
        
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        try:
            css_dir = os.path.join(self.base_dir, "css")
            
            if not os.path.exists(css_dir):
                logger.error(f"Diretório CSS não encontrado: {css_dir}")
                return False
            
            # Arquivo CSS principal
            news_css_path = os.path.join(css_dir, "news.css")
            
            # Se o arquivo não existir, criar
            if not os.path.exists(news_css_path):
                with open(news_css_path, 'w', encoding='utf-8') as f:
                    f.write("""/* Estilos para páginas de notícias */

.news-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.news-image {
    width: 100%;
    max-height: 400px;
    object-fit: cover;
    margin-bottom: 10px;
}

.image-credit {
    font-size: 0.8em;
    color: #666;
    text-align: right;
    margin-top: 5px;
    font-style: italic;
}

.news-title {
    font-size: 2em;
    margin-bottom: 10px;
}

.news-meta {
    color: #666;
    margin-bottom: 20px;
}

.news-content {
    line-height: 1.6;
}
""")
                logger.info("Arquivo CSS de notícias criado")
            else:
                # Ler o arquivo CSS
                with open(news_css_path, 'r', encoding='utf-8') as f:
                    css = f.read()
                
                # Verificar se já tem estilos para créditos de imagens
                if '.image-credit' in css:
                    logger.info("CSS já tem estilos para créditos de imagens")
                else:
                    # Adicionar estilos para créditos de imagens
                    css += """
.image-credit {
    font-size: 0.8em;
    color: #666;
    text-align: right;
    margin-top: 5px;
    font-style: italic;
}
"""
                    # Salvar o arquivo CSS atualizado
                    with open(news_css_path, 'w', encoding='utf-8') as f:
                        f.write(css)
                    
                    logger.info("CSS atualizado com estilos para créditos de imagens")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar CSS: {e}")
            return False
    
    def run_update(self):
        """
        Executa todas as atualizações necessárias.
        
        Returns:
            bool: True se todas as atualizações foram bem-sucedidas, False caso contrário
        """
        logger.info("Iniciando atualização do site BrasilViral")
        
        # Atualizar template
        template_updated = self.update_template()
        
        # Atualizar CSS
        css_updated = self.update_css()
        
        # Atualizar página inicial
        index_updated = self.update_index_page()
        
        # Atualizar páginas de categorias
        category_count = self.update_category_pages()
        
        # Verificar resultados
        if template_updated and css_updated and index_updated and category_count > 0:
            logger.info("Site atualizado com sucesso!")
            return True
        else:
            logger.warning("Site atualizado parcialmente. Verifique os logs para mais detalhes.")
            return False


if __name__ == "__main__":
    updater = SiteUpdater()
    success = updater.run_update()
    
    if success:
        print("Site BrasilViral atualizado com sucesso!")
        sys.exit(0)
    else:
        print("Houve problemas na atualização do site. Verifique os logs para mais detalhes.")
        sys.exit(1)
