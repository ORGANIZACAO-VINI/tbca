/**
 * Script para a aplicação TBCA Web
 */

document.addEventListener('DOMContentLoaded', function() {
    // Tooltip para Bootstrap 5
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Ajustar tamanho da tabela de resultados de busca
    adjustTableSize();
    
    // Adicionar eventos para as categorias
    addCategoryEvents();
    
    // Destacar termos de busca nos resultados
    highlightSearchTerms();
    
    // Inicializar componentes do Bootstrap
    initBootstrapComponents();
});

/**
 * Ajusta o tamanho da tabela de resultados de busca
 */
function adjustTableSize() {
    const table = document.querySelector('.table-responsive table');
    if (table) {
        // Adicionar classe para tabelas com muitas colunas
        if (table.querySelectorAll('th').length > 5) {
            table.classList.add('table-sm');
        }
    }
}

/**
 * Adiciona eventos para os links de categoria
 */
function addCategoryEvents() {
    const categoryLinks = document.querySelectorAll('.list-group-item');
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Destaca a categoria clicada
            categoryLinks.forEach(item => item.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

/**
 * Destaca os termos de busca nos resultados
 */
function highlightSearchTerms() {
    // Obter o termo de busca da URL
    const urlParams = new URLSearchParams(window.location.search);
    const searchTerm = urlParams.get('termo');
    
    if (searchTerm) {
        // Dividir o termo de busca em palavras individuais
        const terms = searchTerm.toLowerCase().split(' ');
        
        // Encontrar elementos com a classe 'highlight-search'
        const highlightElements = document.querySelectorAll('.highlight-search');
        
        highlightElements.forEach(element => {
            let html = element.innerHTML;
            
            // Para cada termo, destacar no texto
            terms.forEach(term => {
                if (term.length >= 3) { // Ignorar termos muito curtos
                    // Expressão regular para encontrar o termo, ignorando maiúsculas/minúsculas
                    const regex = new RegExp(`(${term})`, 'gi');
                    
                    // Substituir com a tag <mark>
                    html = html.replace(regex, '<mark>$1</mark>');
                }
            });
            
            // Atualizar o HTML
            element.innerHTML = html;
        });
    }
}

/**
 * Inicializa componentes do Bootstrap
 */
function initBootstrapComponents() {
    // Inicializar popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Inicializar toasts
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    const toastList = toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl);
    });
    
    // Mostrar toasts automaticamente
    toastList.forEach(toast => toast.show());
}
