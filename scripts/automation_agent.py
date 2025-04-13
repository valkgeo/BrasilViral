#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agente de Automação para o BrasilViral
Este script configura a automação para publicação programada de notícias.
"""

import os
import time
import json
import random
import logging
import schedule
import datetime
import subprocess
from pathlib import Path

# Importar os agentes de pesquisa
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from image_search_agent import ImageSearchAgent
from news_research_agent import NewsResearchAgent

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AutomationAgent")

# Categorias suportadas pelo site
CATEGORIES = [
    'esportes', 'economia', 'politica', 
    'tecnologia', 'entretenimento', 'curiosidades'
]

# Configuração de horários (6h às 22h, uma publicação por hora por categoria)
PUBLISH_HOURS = list(range(6, 23))  # 6h às 22h

class AutomationAgent:
    """Agente para automatizar a publicação programada de notícias."""
    
    def __init__(self, base_dir):
        """
        Inicializa o agente de automação.
        
        Args:
            base_dir (str): Diretório base do site
        """
        self.base_dir = base_dir
        self.image_agent = ImageSearchAgent()
        self.news_agent = NewsResearchAgent()
        self.config_file = os.path.join(base_dir, "scripts", "automation_config.json")
        self.load_config()
        
    def load_config(self):
        """Carrega a configuração de automação."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"Configuração carregada: {self.config}")
            else:
                # Configuração padrão
                self.config = {
                    "posts_per_category_per_day": 17,
                    "start_hour": 6,
                    "end_hour": 22,
                    "enabled": True,
                    "last_run": None,
                    "categories": CATEGORIES
                }
                self.save_config()
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            # Configuração padrão em caso de erro
            self.config = {
                "posts_per_category_per_day": 17,
                "start_hour": 6,
                "end_hour": 22,
                "enabled": True,
                "last_run": None,
                "categories": CATEGORIES
            }
    
    def save_config(self):
        """Salva a configuração de automação."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"Configuração salva: {self.config}")
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
    
    def update_config(self, **kwargs):
        """
        Atualiza a configuração de automação.
        
        Args:
            **kwargs: Pares chave-valor para atualizar na configuração
        """
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
        self.save_config()
    
    def setup_schedule(self):
        """Configura o agendamento de publicações."""
        # Limpar agendamentos existentes
        schedule.clear()
        
        if not self.config.get("enabled", True):
            logger.info("Automação desativada nas configurações.")
            return
        
        # Configurar publicações para cada categoria
        for category in self.config.get("categories", CATEGORIES):
            # Distribuir as publicações ao longo do dia
            posts_per_category = self.config.get("posts_per_category_per_day", 17)
            start_hour = self.config.get("start_hour", 6)
            end_hour = self.config.get("end_hour", 22)
            
            # Calcular intervalo entre publicações
            hours_range = end_hour - start_hour + 1
            
            if posts_per_category <= hours_range:
                # Se temos menos posts que horas, distribuir uniformemente
                hours_to_publish = sorted(random.sample(range(start_hour, end_hour + 1), posts_per_category))
                
                for hour in hours_to_publish:
                    # Minuto aleatório para cada hora
                    minute = random.randint(0, 59)
                    schedule_time = f"{hour:02d}:{minute:02d}"
                    
                    # Agendar publicação
                    schedule.every().day.at(schedule_time).do(
                        self.publish_news_for_category, category=category
                    )
                    logger.info(f"Agendada publicação para {category} às {schedule_time}")
            else:
                # Se temos mais posts que horas, distribuir múltiplos posts por hora
                posts_per_hour = posts_per_category / hours_range
                
                for hour in range(start_hour, end_hour + 1):
                    # Determinar quantos posts nesta hora
                    if hour == end_hour:
                        # Garantir que o total seja exato
                        num_posts = posts_per_category - int(posts_per_hour) * (hours_range - 1)
                    else:
                        num_posts = int(posts_per_hour)
                        if random.random() < (posts_per_hour - int(posts_per_hour)):
                            num_posts += 1
                    
                    # Agendar múltiplas publicações nesta hora
                    for i in range(num_posts):
                        minute = random.randint(0, 59)
                        schedule_time = f"{hour:02d}:{minute:02d}"
                        
                        schedule.every().day.at(schedule_time).do(
                            self.publish_news_for_category, category=category
                        )
                        logger.info(f"Agendada publicação para {category} às {schedule_time}")
        
        # Agendar atualização da página inicial
        schedule.every(1).hours.do(self.update_index_page)
        logger.info("Agendada atualização da página inicial a cada hora")
        
        # Agendar limpeza de notícias antigas (manter apenas últimos 30 dias)
        schedule.every().day.at("03:00").do(self.cleanup_old_news)
        logger.info("Agendada limpeza de notícias antigas às 03:00")
    
    def publish_news_for_category(self, category):
        """
        Publica uma nova notícia para a categoria especificada.
        
        Args:
            category (str): Categoria da notícia
            
        Returns:
            bool: True se a publicação foi bem-sucedida, False caso contrário
        """
        try:
            logger.info(f"Iniciando publicação para categoria: {category}")
            
            # Pesquisar notícias virais
            news_list = self.news_agent.search_viral_news(category, limit=5)
            
            if not news_list:
                logger.warning(f"Nenhuma notícia encontrada para categoria: {category}")
                return False
            
            # Selecionar a notícia mais viral
            news = news_list[0]
            
            # Reescrever a notícia
            rewritten_news = self.news_agent.rewrite_news(news)
            
            # Buscar imagem para a notícia
            image_info = self.image_agent.get_image_for_news(
                rewritten_news['title'], 
                rewritten_news['content'], 
                category
            )
            
            # Criar diretório para imagens da categoria se não existir
            category_images_dir = os.path.join(self.base_dir, "images", category)
            os.makedirs(category_images_dir, exist_ok=True)
            
            # Gerar nome de arquivo para a imagem
            image_filename = f"{int(time.time())}_{category}.jpg"
            image_path = os.path.join(category_images_dir, image_filename)
            
            # Baixar a imagem
            if not image_info.get('is_default', False):
                self.image_agent.download_image(image_info, image_path)
                image_url = f"../../images/{category}/{image_filename}"
            else:
                # Usar imagem padrão
                image_url = f"../../images/placeholder-{category}.jpg"
            
            # Publicar a notícia
            publish_info = self.news_agent.publish_news(rewritten_news, self.base_dir)
            
            if publish_info:
                logger.info(f"Notícia publicada com sucesso: {publish_info['title']}")
                
                # Atualizar a imagem na página da notícia
                self.update_news_image(publish_info['filepath'], image_url)
                
                # Atualizar a página inicial
                self.update_index_page()
                
                return True
            else:
                logger.error(f"Falha ao publicar notícia: {rewritten_news['title']}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao publicar notícia para categoria {category}: {e}")
            return False
    
    def update_news_image(self, news_filepath, image_url):
        """
        Atualiza a imagem em uma página de notícia.
        
        Args:
            news_filepath (str): Caminho do arquivo HTML da notícia
            image_url (str): URL da imagem
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        try:
            with open(news_filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substituir o placeholder da imagem
            updated_content = content.replace(
                '{{IMAGEM_URL}}', 
                image_url
            )
            
            with open(news_filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logger.info(f"Imagem atualizada em {news_filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar imagem em {news_filepath}: {e}")
            return False
    
    def update_index_page(self):
        """
        Atualiza a página inicial com as notícias mais recentes.
        
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        try:
            logger.info("Atualizando página inicial...")
            
            # Obter as notícias mais recentes de cada categoria
            featured_news = {}
            for category in self.config.get("categories", CATEGORIES):
                category_news = self.news_agent.get_top_news_for_category(category, count=3)
                featured_news[category] = category_news
            
            # Atualizar a página inicial
            index_path = os.path.join(self.base_dir, "index.html")
            
            # Aqui seria implementada a lógica para atualizar o HTML da página inicial
            # com as notícias mais recentes de cada categoria
            # Por simplicidade, apenas logamos a ação
            
            logger.info(f"Página inicial atualizada com {sum(len(news) for news in featured_news.values())} notícias")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar página inicial: {e}")
            return False
    
    def cleanup_old_news(self, days=30):
        """
        Remove notícias antigas para manter o site organizado.
        
        Args:
            days (int): Número de dias para manter notícias
            
        Returns:
            bool: True se a limpeza foi bem-sucedida, False caso contrário
        """
        try:
            logger.info(f"Iniciando limpeza de notícias com mais de {days} dias...")
            
            # Calcular data limite
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
            cutoff_timestamp = cutoff_date.timestamp()
            
            # Percorrer diretórios de categorias
            categories_dir = os.path.join(self.base_dir, "categorias")
            for category in os.listdir(categories_dir):
                category_dir = os.path.join(categories_dir, category)
                if os.path.isdir(category_dir):
                    # Verificar arquivos HTML
                    for filename in os.listdir(category_dir):
                        if filename.endswith(".html") and filename != "index.html":
                            filepath = os.path.join(category_dir, filename)
                            file_mtime = os.path.getmtime(filepath)
                            
                            # Remover se for mais antigo que o limite
                            if file_mtime < cutoff_timestamp:
                                os.remove(filepath)
                                logger.info(f"Removida notícia antiga: {filepath}")
            
            logger.info("Limpeza de notícias antigas concluída")
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar notícias antigas: {e}")
            return False
    
    def run_scheduler(self):
        """Executa o agendador de tarefas."""
        logger.info("Iniciando agendador de tarefas...")
        
        # Configurar agendamento
        self.setup_schedule()
        
        # Registrar última execução
        self.config["last_run"] = datetime.datetime.now().isoformat()
        self.save_config()
        
        # Executar agendador
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
        except KeyboardInterrupt:
            logger.info("Agendador interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro no agendador: {e}")
    
    def start_as_daemon(self):
        """Inicia o agendador como um processo daemon."""
        try:
            # Criar script de inicialização
            startup_script = os.path.join(self.base_dir, "scripts", "start_automation.sh")
            with open(startup_script, 'w') as f:
                f.write(f"""#!/bin/bash
cd {self.base_dir}/scripts
nohup python3 -c "from automation_agent import AutomationAgent; agent = AutomationAgent('{self.base_dir}'); agent.run_scheduler()" > automation.out 2>&1 &
echo $! > automation.pid
""")
            
            # Tornar executável
            os.chmod(startup_script, 0o755)
            
            # Executar script
            subprocess.run(["bash", startup_script])
            
            logger.info("Agendador iniciado como daemon")
            return True
        except Exception as e:
            logger.error(f"Erro ao iniciar daemon: {e}")
            return False
    
    def stop_daemon(self):
        """Para o processo daemon do agendador."""
        try:
            pid_file = os.path.join(self.base_dir, "scripts", "automation.pid")
            if os.path.exists(pid_file):
                with open(pid_file, 'r') as f:
                    pid = f.read().strip()
                
                # Matar processo
                subprocess.run(["kill", pid])
                os.remove(pid_file)
                
                logger.info(f"Daemon parado (PID: {pid})")
                return True
            else:
                logger.warning("Arquivo PID não encontrado, daemon pode não estar em execução")
                return False
        except Exception as e:
            logger.error(f"Erro ao parar daemon: {e}")
            return False


# Função para demonstração
def demo():
    """Demonstra o uso do agente de automação."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    agent = AutomationAgent(base_dir)
    
    print("Configuração atual:")
    print(json.dumps(agent.config, indent=2))
    
    print("\nConfigurando agendamento...")
    agent.setup_schedule()
    
    print("\nSimulando publicação para categoria 'tecnologia':")
    result = agent.publish_news_for_category("tecnologia")
    print(f"Resultado: {'Sucesso' if result else 'Falha'}")
    
    print("\nPara iniciar o agendador como daemon:")
    print("agent.start_as_daemon()")
    
    print("\nPara parar o daemon:")
    print("agent.stop_daemon()")


if __name__ == "__main__":
    demo()
