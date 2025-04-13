// Script para gerenciar anúncios no site BrasilViral

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar placeholders de anúncios
    initializeAdPlaceholders();
    
    // Simular carregamento de anúncios reais (em produção, seria substituído pelo código do AdSense)
    simulateAdLoading();
});

// Função para inicializar placeholders de anúncios
function initializeAdPlaceholders() {
    // Adicionar classe de animação aos placeholders
    const adPlaceholders = document.querySelectorAll('.ad-placeholder');
    adPlaceholders.forEach(placeholder => {
        placeholder.classList.add('ad-loading');
    });
}

// Função para simular carregamento de anúncios
function simulateAdLoading() {
    // Simular delay de carregamento
    setTimeout(() => {
        const adPlaceholders = document.querySelectorAll('.ad-placeholder');
        adPlaceholders.forEach(placeholder => {
            placeholder.classList.remove('ad-loading');
            placeholder.classList.add('ad-loaded');
        });
    }, 1500);
}

// Função para registrar cliques em anúncios (para análise)
function trackAdClick(adId, position) {
    // Em produção, isso enviaria dados para um sistema de analytics
    console.log(`Ad clicked: ${adId} at position ${position}`);
}

// Função para verificar visibilidade de anúncios (para métricas de impressão)
function checkAdVisibility() {
    const adSlots = document.querySelectorAll('.ad-slot');
    
    adSlots.forEach(slot => {
        const rect = slot.getBoundingClientRect();
        const isVisible = (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
        
        if (isVisible && !slot.dataset.viewed) {
            // Marcar como visualizado para não contar múltiplas impressões
            slot.dataset.viewed = 'true';
            
            // Em produção, isso registraria uma impressão
            const adId = slot.id || 'unknown';
            console.log(`Ad impression: ${adId}`);
        }
    });
}

// Adicionar listener de scroll para verificar visibilidade de anúncios
window.addEventListener('scroll', function() {
    // Usar throttle para não sobrecarregar com muitos eventos
    if (!window.adScrollTimeout) {
        window.adScrollTimeout = setTimeout(function() {
            checkAdVisibility();
            window.adScrollTimeout = null;
        }, 250);
    }
});
