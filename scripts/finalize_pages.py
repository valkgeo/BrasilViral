#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para finalizar as páginas de exemplo do site BrasilViral.
Este script substitui os placeholders nas páginas de exemplo por conteúdo real.
"""

import os
import re
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("finalize_pages.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PageFinalizer")

class PageFinalizer:
    """Classe para finalizar as páginas de exemplo do site BrasilViral."""
    
    def __init__(self, base_dir="/home/ubuntu/brasilviralsite_images"):
        """
        Inicializa o finalizador de páginas.
        
        Args:
            base_dir (str): Diretório base do site
        """
        self.base_dir = base_dir
        self.categories = ["esportes", "economia", "politica", "tecnologia", "entretenimento", "curiosidades"]
        self.category_tags = {
            "esportes": ["futebol", "campeonato", "atletas", "olimpíadas", "competição"],
            "economia": ["mercado", "finanças", "investimentos", "bolsa", "dólar"],
            "politica": ["governo", "congresso", "eleições", "leis", "democracia"],
            "tecnologia": ["inovação", "digital", "internet", "aplicativos", "inteligência artificial"],
            "entretenimento": ["cinema", "música", "celebridades", "shows", "streaming"],
            "curiosidades": ["fatos", "descobertas", "ciência", "história", "mundo"]
        }
        self.category_content = {
            "esportes": "Este é um exemplo de notícia esportiva. Aqui você encontrará as últimas informações sobre competições, resultados de jogos, transferências de jogadores e muito mais. O BrasilViral traz cobertura completa dos principais eventos esportivos nacionais e internacionais.",
            "economia": "Este é um exemplo de notícia econômica. Aqui você encontrará análises sobre o mercado financeiro, cotações de moedas, informações sobre investimentos e tendências econômicas. O BrasilViral traz informações atualizadas para ajudar você a entender o cenário econômico atual.",
            "politica": "Este é um exemplo de notícia política. Aqui você encontrará informações sobre decisões governamentais, projetos de lei, eleições e debates políticos. O BrasilViral traz cobertura imparcial dos principais acontecimentos políticos do Brasil e do mundo.",
            "tecnologia": "Este é um exemplo de notícia tecnológica. Aqui você encontrará informações sobre lançamentos de produtos, inovações tecnológicas, tendências digitais e avanços científicos. O BrasilViral traz as novidades mais recentes do mundo da tecnologia.",
            "entretenimento": "Este é um exemplo de notícia de entretenimento. Aqui você encontrará informações sobre cinema, música, celebridades, eventos culturais e lançamentos de streaming. O BrasilViral traz as novidades mais quentes do mundo do entretenimento.",
            "curiosidades": "Este é um exemplo de notícia de curiosidades. Aqui você encontrará fatos interessantes, descobertas científicas, histórias inusitadas e fenômenos surpreendentes. O BrasilViral traz conteúdo que vai expandir seus conhecimentos e surpreender você."
        }
    
    def finalize_example_pages(self):
        """
        Finaliza as páginas de exemplo substituindo os placeholders.
        
        Returns:
            int: Número de páginas finalizadas
        """
        try:
            count = 0
            
            for category in self.categories:
                category_dir = os.path.join(self.base_dir, "categorias", category)
                example_path = os.path.join(category_dir, f"exemplo_{category}.html")
                
                if not os.path.exists(example_path):
                    logger.warning(f"Página de exemplo não encontrada para categoria: {category}")
                    continue
                
                # Ler a página de exemplo
                with open(example_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Data atual formatada
                current_date = datetime.now().strftime("%d de %B de %Y").replace("January", "Janeiro").replace("February", "Fevereiro").replace("March", "Março").replace("April", "Abril").replace("May", "Maio").replace("June", "Junho").replace("July", "Julho").replace("August", "Agosto").replace("September", "Setembro").replace("October", "Outubro").replace("November", "Novembro").replace("December", "Dezembro")
                
                # Tags para a categoria
                tags = ", ".join(self.category_tags[category])
                
                # Conteúdo específico para a categoria
                category_content = self.category_content[category]
                
                # Substituir placeholders
                replacements = {
                    "{{CATEGORIA_NOME}}": category.capitalize(),
                    "{{DATA_PUBLICACAO}}": current_date,
                    "{DATA_PUBLICACAO}": current_date,
                    "{{TAGS}}": tags,
                    "{TAGS}": tags,
                    "{{ULTIMAS_NOTICIAS}}": "Dólar atinge maior valor do ano • Novo técnico da seleção brasileira será anunciado hoje • Problemas no WhatsApp afetam milhões de usuários",
                    "{ULTIMAS_NOTICIAS}": "Dólar atinge maior valor do ano • Novo técnico da seleção brasileira será anunciado hoje • Problemas no WhatsApp afetam milhões de usuários",
                    "{{NOTICIAS_RELACIONADAS}}": "Nenhuma notícia relacionada encontrada",
                    "{NOTICIAS_RELACIONADAS}": "Nenhuma notícia relacionada encontrada",
                    "Este é um exemplo de notícia para a categoria": category_content
                }
                
                for placeholder, replacement in replacements.items():
                    content = content.replace(placeholder, replacement)
                
                # Substituir placeholders de imagem e crédito
                if "{{IMAGEM_CREDITO}}" in content or "{IMAGEM_CREDITO}" in content:
                    # Procurar pela imagem atual
                    img_match = re.search(r'<img[^>]*src="([^"]*)"[^>]*class="news-image"[^>]*>', content)
                    if img_match:
                        img_src = img_match.group(1)
                        # Determinar o tipo de imagem
                        img_type = "padrão"
                        if "abstract" in img_src:
                            img_type = "abstrato"
                        elif "icon" in img_src:
                            img_type = "ícone"
                        elif "geometric" in img_src:
                            img_type = "geométrico"
                        
                        # Criar crédito
                        credit = f'<div class="image-credit">Ilustração: BrasilViral - {category.capitalize()} ({img_type})</div>'
                        
                        # Substituir placeholder de crédito
                        content = content.replace("{{IMAGEM_CREDITO}}", credit)
                        content = content.replace("{IMAGEM_CREDITO}", credit)
                
                # Salvar a página atualizada
                with open(example_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                count += 1
                logger.info(f"Página de exemplo finalizada para categoria: {category}")
            
            logger.info(f"Total de {count} páginas de exemplo finalizadas")
            return count
        except Exception as e:
            logger.error(f"Erro ao finalizar páginas de exemplo: {e}")
            return 0
    
    def finalize_index_page(self):
        """
        Finaliza a página inicial substituindo os placeholders.
        
        Returns:
            bool: True se a finalização foi bem-sucedida, False caso contrário
        """
        try:
            index_path = os.path.join(self.base_dir, "index.html")
            
            if not os.path.exists(index_path):
                logger.error(f"Página inicial não encontrada: {index_path}")
                return False
            
            # Ler a página inicial
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substituir placeholders
            replacements = {
                "{{ULTIMAS_NOTICIAS}}": "Dólar atinge maior valor do ano • Novo técnico da seleção brasileira será anunciado hoje • Problemas no WhatsApp afetam milhões de usuários",
                "{ULTIMAS_NOTICIAS}": "Dólar atinge maior valor do ano • Novo técnico da seleção brasileira será anunciado hoje • Problemas no WhatsApp afetam milhões de usuários"
            }
            
            for placeholder, replacement in replacements.items():
                content = content.replace(placeholder, replacement)
            
            # Salvar a página atualizada
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info("Página inicial finalizada")
            return True
        except Exception as e:
            logger.error(f"Erro ao finalizar página inicial: {e}")
            return False
    
    def run_finalizer(self):
        """
        Executa todas as finalizações necessárias.
        
        Returns:
            bool: True se todas as finalizações foram bem-sucedidas, False caso contrário
        """
        logger.info("Iniciando finalização das páginas")
        
        # Finalizar páginas de exemplo
        example_count = self.finalize_example_pages()
        
        # Finalizar página inicial
        index_finalized = self.finalize_index_page()
        
        # Verificar resultados
        if example_count > 0 and index_finalized:
            logger.info("Finalização das páginas concluída com sucesso!")
            return True
        else:
            logger.warning("Finalização das páginas concluída parcialmente. Verifique os logs para mais detalhes.")
            return False


if __name__ == "__main__":
    finalizer = PageFinalizer()
    success = finalizer.run_finalizer()
    
    if success:
        print("Páginas do site BrasilViral finalizadas com sucesso!")
    else:
        print("Houve problemas na finalização das páginas. Verifique os logs para mais detalhes.")
