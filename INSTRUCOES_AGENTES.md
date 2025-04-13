# Instruções para Ativação dos Agentes de IA - BrasilViral

Este documento contém instruções detalhadas sobre como ativar e configurar os agentes de IA para busca de imagens e geração de notícias no site BrasilViral.

## 1. Configuração Inicial

Antes de ativar os agentes, você precisa instalar as dependências necessárias no servidor onde os scripts serão executados:

```bash
pip install requests beautifulsoup4 nltk
```

## 2. Ativação do Agente de Busca de Imagens

O agente de busca de imagens (`image_search_agent.py`) é responsável por encontrar imagens gratuitas relacionadas ao conteúdo das notícias.

### Configuração de APIs (Opcional, mas Recomendado)

Para melhores resultados, recomendamos configurar APIs gratuitas para busca de imagens:

1. **Pixabay API**:
   - Crie uma conta em [Pixabay](https://pixabay.com/api/docs/)
   - Obtenha sua chave de API gratuita
   - Abra o arquivo `scripts/image_search_agent.py`
   - Localize a linha `PIXABAY_API_KEY = ""` e insira sua chave

2. **Pexels API**:
   - Crie uma conta em [Pexels](https://www.pexels.com/api/)
   - Obtenha sua chave de API gratuita
   - Localize a linha `PEXELS_API_KEY = ""` e insira sua chave

### Execução Manual do Agente de Imagens

Para testar o agente de busca de imagens manualmente:

```bash
cd /caminho/para/brasilviralsite
python3 scripts/image_search_agent.py
```

## 3. Ativação do Agente de Pesquisa de Notícias

O agente de pesquisa de notícias (`news_research_agent.py`) é responsável por encontrar e parafrasear notícias virais.

### Execução Manual do Agente de Notícias

Para testar o agente de pesquisa de notícias manualmente:

```bash
cd /caminho/para/brasilviralsite
python3 scripts/news_research_agent.py
```

## 4. Configuração da Automação

Para que os agentes funcionem automaticamente, você precisa configurar o script de automação para ser executado periodicamente.

### Configuração do Cron Job (Linux/Mac)

1. Abra o editor de cron:
   ```bash
   crontab -e
   ```

2. Adicione as seguintes linhas para executar os agentes conforme programado (das 6h às 22h):
   ```
   # Executar agente de notícias a cada hora das 6h às 22h
   0 6-22 * * * cd /caminho/para/brasilviralsite && python3 scripts/automation_agent.py
   
   # Executar pipeline de conteúdo para processar notícias e imagens
   15 6-22 * * * cd /caminho/para/brasilviralsite && python3 scripts/content_pipeline.py
   ```

### Configuração do Agendador de Tarefas (Windows)

1. Abra o Agendador de Tarefas do Windows
2. Crie uma nova tarefa para executar `scripts/automation_agent.py` a cada hora das 6h às 22h
3. Crie outra tarefa para executar `scripts/content_pipeline.py` 15 minutos após cada execução do agente de automação

## 5. Estrutura de Diretórios

Certifique-se de que a seguinte estrutura de diretórios existe e tem permissões de escrita:

```
brasilviralsite/
├── images/                  # Diretório para armazenar imagens
├── categorias/              # Diretório para páginas de categorias
│   ├── esportes/
│   ├── economia/
│   ├── politica/
│   ├── tecnologia/
│   ├── entretenimento/
│   └── curiosidades/
└── scripts/                 # Diretório com os scripts dos agentes
```

## 6. Solução de Problemas

Se os agentes não estiverem funcionando corretamente:

1. **Verifique os logs**:
   - `scripts/image_search.log` para o agente de imagens
   - `scripts/news_research.log` para o agente de notícias

2. **Problemas comuns**:
   - Permissões de diretório: Certifique-se de que os diretórios têm permissões de escrita
   - Conexão com a internet: Os agentes precisam de acesso à internet para funcionar
   - Limites de API: As APIs gratuitas têm limites de uso, verifique se você não excedeu esses limites

3. **Reiniciar os agentes**:
   - Exclua os arquivos de cache (`scripts/*.json`) para forçar uma nova busca

## 7. Personalização

Você pode personalizar o comportamento dos agentes editando os seguintes parâmetros:

### No arquivo `scripts/automation_agent.py`:

- `POSTS_PER_HOUR`: Número de postagens por hora (padrão: 1 por categoria)
- `CATEGORIES`: Lista de categorias para buscar notícias

### No arquivo `scripts/image_search_agent.py`:

- `MAX_IMAGES`: Número máximo de imagens a serem buscadas por notícia
- `KEYWORDS_PER_SEARCH`: Número de palavras-chave a serem usadas na busca

## 8. Contato e Suporte

Se precisar de ajuda adicional com a configuração ou tiver dúvidas sobre os agentes, entre em contato através do GitHub ou do email de suporte.
