#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para corrigir os links de navegação no site BrasilViral.
Este script atualiza os links no menu de navegação para apontar para as páginas de categorias corretas.
"""

import os
import re
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fix_navigation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NavigationFixer")

class NavigationFixer:
    """Classe para corrigir os links de navegação no site BrasilViral."""
    
    def __init__(self, base_dir="/home/ubuntu/brasilviralsite_images"):
        """
        Inicializa o corretor de navegação.
        
        Args:
            base_dir (str): Diretório base do site
        """
        self.base_dir = base_dir
        self.categories = ["esportes", "economia", "politica", "tecnologia", "entretenimento", "curiosidades"]
    
    def fix_index_navigation(self):
        """
        Corrige os links de navegação na página inicial.
        
        Returns:
            bool: True se a correção foi bem-sucedida, False caso contrário
        """
        try:
            index_path = os.path.join(self.base_dir, "index.html")
            
            if not os.path.exists(index_path):
                logger.error(f"Arquivo index.html não encontrado: {index_path}")
                return False
            
            # Ler o conteúdo atual
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Corrigir links no menu de navegação
            for category in self.categories:
                # Padrão para encontrar links de categoria no menu
                category_pattern = rf'<a[^>]*href="[^"]*"[^>]*>{category.capitalize()}</a>'
                category_matches = re.findall(category_pattern, content, re.IGNORECASE)
                
                if category_matches:
                    for match in category_matches:
                        # Criar novo link apontando para a página de exemplo da categoria
                        new_link = f'<a href="categorias/{category}/exemplo_{category}.html">{category.capitalize()}</a>'
                        content = content.replace(match, new_link)
                        logger.info(f"Link corrigido para categoria: {category}")
                else:
                    logger.warning(f"Link não encontrado para categoria: {category}")
            
            # Corrigir links nas notícias em destaque
            for category in self.categories:
                # Padrão para encontrar cards de notícias
                card_pattern = rf'<div[^>]*class="[^"]*card[^"]*"[^>]*>.*?{category.upper()}.*?</div>'
                card_matches = re.findall(card_pattern, content, re.DOTALL | re.IGNORECASE)
                
                if card_matches:
                    for match in card_matches:
                        # Verificar se já tem um link
                        if f'href="categorias/{category}/exemplo_{category}.html"' not in match:
                            # Adicionar link para a página de exemplo
                            new_card = re.sub(r'(<h5[^>]*class="[^"]*card-title[^"]*"[^>]*>)',
                                             f'<a href="categorias/{category}/exemplo_{category}.html">\\1',
                                             match)
                            new_card = re.sub(r'(</h5>)', '\\1</a>', new_card)
                            content = content.replace(match, new_card)
                            logger.info(f"Link adicionado ao card de notícia para categoria: {category}")
            
            # Salvar o conteúdo atualizado
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info("Links de navegação corrigidos na página inicial")
            return True
        except Exception as e:
            logger.error(f"Erro ao corrigir links de navegação: {e}")
            return False
    
    def create_category_index_pages(self):
        """
        Cria páginas de índice para cada categoria.
        
        Returns:
            int: Número de páginas de índice criadas
        """
        try:
            count = 0
            
            for category in self.categories:
                category_dir = os.path.join(self.base_dir, "categorias", category)
                
                if not os.path.exists(category_dir):
                    logger.warning(f"Diretório não encontrado para categoria: {category}")
                    continue
                
                # Verificar se já existe uma página de exemplo
                example_path = os.path.join(category_dir, f"exemplo_{category}.html")
                
                if not os.path.exists(example_path):
                    logger.warning(f"Página de exemplo não encontrada para categoria: {category}")
                    continue
                
                # Ler a página de exemplo
                with open(example_path, 'r', encoding='utf-8') as f:
                    example_content = f.read()
                
                # Criar uma página de índice para a categoria
                index_content = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BrasilViral - {category.capitalize()}</title>
    <link rel="stylesheet" href="../../css/style.css">
    <link rel="stylesheet" href="../../css/news.css">
    <link rel="stylesheet" href="../../css/share-buttons.css">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1234567890123456" crossorigin="anonymous"></script>
    <style>
        .category-header {{
            background-color: #f8f9fa;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            text-align: center;
        }}
        .news-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .news-card {{
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
            transition: transform 0.3s;
        }}
        .news-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .news-card img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
        }}
        .news-card-content {{
            padding: 15px;
        }}
        .news-card h3 {{
            margin-top: 0;
            font-size: 1.2em;
        }}
        .news-card p {{
            color: #666;
            font-size: 0.9em;
        }}
        .news-card .date {{
            color: #999;
            font-size: 0.8em;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="logo">
                <a href="../../index.html">
                    <h1>Brasil<span>Viral</span></h1>
                    <p>Notícias que Bombam</p>
                </a>
            </div>
            <nav>
                <ul>
                    <li><a href="../../index.html">Home</a></li>
                    <li><a href="../esportes/exemplo_esportes.html">Esportes</a></li>
                    <li><a href="../economia/exemplo_economia.html">Economia</a></li>
                    <li><a href="../politica/exemplo_politica.html">Política</a></li>
                    <li><a href="../tecnologia/exemplo_tecnologia.html">Tecnologia</a></li>
                    <li><a href="../entretenimento/exemplo_entretenimento.html">Entretenimento</a></li>
                    <li><a href="../curiosidades/exemplo_curiosidades.html">Curiosidades</a></li>
                </ul>
            </nav>
            <div class="search">
                <input type="text" placeholder="Buscar notícias...">
                <button><i class="fas fa-search"></i></button>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="category-header">
            <h1>{category.capitalize()}</h1>
            <p>As últimas notícias sobre {category}</p>
        </div>

        <div class="news-list">
            <div class="news-card">
                <a href="exemplo_{category}.html">
                    <img src="../../images/{category}/{category}_abstrato_20250412183401.png" alt="Notícia de {category}">
                    <div class="news-card-content">
                        <h3>Exemplo de notícia de {category}</h3>
                        <p>Este é um exemplo de notícia para a categoria {category}.</p>
                        <div class="date">12 de Abril de 2025</div>
                    </div>
                </a>
            </div>
            <!-- Mais cards de notícias seriam adicionados aqui pelo agente de notícias -->
        </div>
    </div>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-section about">
                    <h2>Sobre Nós</h2>
                    <p>O BrasilViral é um site de notícias dedicado a trazer as informações mais relevantes e virais do Brasil e do mundo.</p>
                </div>
                <div class="footer-section links">
                    <h2>Links Rápidos</h2>
                    <ul>
                        <li><a href="../../index.html">Home</a></li>
                        <li><a href="../esportes/exemplo_esportes.html">Esportes</a></li>
                        <li><a href="../economia/exemplo_economia.html">Economia</a></li>
                        <li><a href="../politica/exemplo_politica.html">Política</a></li>
                        <li><a href="../tecnologia/exemplo_tecnologia.html">Tecnologia</a></li>
                        <li><a href="../entretenimento/exemplo_entretenimento.html">Entretenimento</a></li>
                        <li><a href="../curiosidades/exemplo_curiosidades.html">Curiosidades</a></li>
                    </ul>
                </div>
                <div class="footer-section contact">
                    <h2>Contato</h2>
                    <p><i class="fas fa-envelope"></i> contato@brasilviral.com</p>
                    <p><i class="fas fa-phone"></i> (11) 99999-9999</p>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2025 BrasilViral - Todos os direitos reservados</p>
            </div>
        </div>
    </footer>

    <script src="../../js/main.js"></script>
    <script src="../../js/adsense.js"></script>
</body>
</html>
"""
                
                # Salvar a página de índice
                index_path = os.path.join(category_dir, "index.html")
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write(index_content)
                
                count += 1
                logger.info(f"Página de índice criada para categoria: {category}")
            
            logger.info(f"Total de {count} páginas de índice criadas")
            return count
        except Exception as e:
            logger.error(f"Erro ao criar páginas de índice: {e}")
            return 0
    
    def run_fixes(self):
        """
        Executa todas as correções necessárias.
        
        Returns:
            bool: True se todas as correções foram bem-sucedidas, False caso contrário
        """
        logger.info("Iniciando correções de navegação")
        
        # Corrigir links na página inicial
        index_fixed = self.fix_index_navigation()
        
        # Criar páginas de índice para categorias
        category_count = self.create_category_index_pages()
        
        # Verificar resultados
        if index_fixed and category_count > 0:
            logger.info("Correções de navegação concluídas com sucesso!")
            return True
        else:
            logger.warning("Correções de navegação concluídas parcialmente. Verifique os logs para mais detalhes.")
            return False


if __name__ == "__main__":
    fixer = NavigationFixer()
    success = fixer.run_fixes()
    
    if success:
        print("Navegação do site BrasilViral corrigida com sucesso!")
    else:
        print("Houve problemas na correção da navegação. Verifique os logs para mais detalhes.")
