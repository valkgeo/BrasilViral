// Funções para o site BrasilViral

// Função para alternar o menu mobile
function toggleMobileMenu() {
    const navMenu = document.getElementById('navMenu');
    navMenu.classList.toggle('active');
}

// Inicializar o menu toggle
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menuToggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', toggleMobileMenu);
    }
    
    // Inicializar links para notícias
    initializeNewsLinks();
    
    // Inicializar formulário de newsletter
    const newsletterForm = document.getElementById('newsletterForm');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            alert(`Obrigado por se inscrever! Você receberá nossas notícias no email: ${email}`);
            this.reset();
        });
    }
});

// Função para inicializar links para notícias
function initializeNewsLinks() {
    // Selecionar todos os cards de notícias
    const newsCards = document.querySelectorAll('.featured-card, .article-card');
    
    // Adicionar evento de clique para cada card
    newsCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Verificar se o clique foi em um link interno
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                // Deixar o comportamento padrão do link
                return;
            }
            
            // Obter o link da notícia (se existir)
            const link = this.getAttribute('data-link');
            if (link) {
                window.location.href = link;
            }
        });
    });
}

// Função para carregar mais notícias (simulação)
function loadMoreNews(category) {
    const categorySection = document.getElementById(`${category}Featured`);
    if (categorySection) {
        const articlesContainer = categorySection.querySelector('.category-articles');
        
        // Simular carregamento
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'loading-indicator';
        loadingIndicator.textContent = 'Carregando mais notícias...';
        articlesContainer.appendChild(loadingIndicator);
        
        // Simular delay de rede
        setTimeout(() => {
            // Remover indicador de carregamento
            articlesContainer.removeChild(loadingIndicator);
            
            // Aqui seria feita uma requisição AJAX para carregar mais notícias
            // Por enquanto, apenas exibimos uma mensagem
            alert(`Mais notícias de ${category} seriam carregadas aqui.`);
        }, 1000);
    }
}

// Função para compartilhar notícia
function shareNews(platform, url, title) {
    let shareUrl;
    
    switch(platform) {
        case 'facebook':
            shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
            break;
        case 'twitter':
            shareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`;
            break;
        case 'whatsapp':
            shareUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(title + ' ' + url)}`;
            break;
        case 'telegram':
            shareUrl = `https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`;
            break;
    }
    
    if (shareUrl) {
        window.open(shareUrl, '_blank', 'width=600,height=400');
    }
}

// Função para atualizar as últimas notícias na barra de breaking news
function updateBreakingNews(newsItems) {
    const breakingNewsElement = document.getElementById('breakingNews');
    if (breakingNewsElement && newsItems && newsItems.length) {
        breakingNewsElement.textContent = newsItems.join(' • ');
    }
}

// Função para buscar notícias
function searchNews(query) {
    if (!query || query.trim() === '') {
        alert('Por favor, digite algo para buscar.');
        return;
    }
    
    // Aqui seria feita uma busca real
    // Por enquanto, apenas exibimos uma mensagem
    alert(`Buscando por: ${query}`);
    
    // Redirecionar para uma página de resultados (simulação)
    // window.location.href = `/busca.html?q=${encodeURIComponent(query)}`;
}

// Inicializar a busca quando o formulário for enviado
document.addEventListener('DOMContentLoaded', function() {
    const searchBox = document.querySelector('.search-box');
    if (searchBox) {
        const searchInput = searchBox.querySelector('input');
        const searchButton = searchBox.querySelector('button');
        
        searchButton.addEventListener('click', function() {
            searchNews(searchInput.value);
        });
        
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchNews(this.value);
            }
        });
    }
});
