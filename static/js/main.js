document.addEventListener('DOMContentLoaded', function() {
    // Инициализация feather icons
    feather.replace();
    
    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const searchResults = document.getElementById('searchResults');
    const aiResponse = document.getElementById('aiResponse');
    const errorMessage = document.getElementById('errorMessage');

    // Функция для обработки удаления
    function handleDelete(btn) {
        const searchId = btn.dataset.id;
        const container = btn.closest('.recent-search-container');
        
        if (!searchId) {
            console.error('ID записи не найден');
            return;
        }
        
        fetch(`/history/${searchId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                container.remove();
                
                // Если все элементы удалены, скрыть секцию истории
                const historySection = document.querySelector('.recent-searches');
                if (historySection && document.querySelectorAll('.recent-search-container').length === 0) {
                    historySection.classList.add('d-none');
                }
            }
        })
        .catch(error => {
            console.error('Ошибка при удалении:', error);
        });
    }

    // Handle search form submission
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = searchInput.value.trim();
        
        if (!query) return;

        // Show loading state
        loading.classList.remove('d-none');
        results.classList.add('d-none');
        errorMessage.classList.add('d-none');

        // Send search request
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Hide loading state
            loading.classList.add('d-none');
            
            if (data.error) {
                // Show error message
                errorMessage.textContent = data.error;
                errorMessage.classList.remove('d-none');
                return;
            }

            // Show results
            results.classList.remove('d-none');
            
            // Update AI response
            aiResponse.innerHTML = data.ai_response.replace(/\n/g, '<br>');
            
            // Update search results
            searchResults.innerHTML = data.search_results.map(result => `
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">
                            <a href="${result.link}" target="_blank" rel="noopener noreferrer">
                                ${result.title}
                            </a>
                        </h5>
                        <p class="card-text">${result.snippet}</p>
                    </div>
                </div>
            `).join('');

            // Add new search to history without page reload
            const historySection = document.querySelector('.recent-searches');
            if (historySection && data.search_id) {
                const searchContainer = document.createElement('div');
                searchContainer.className = 'recent-search-container';
                searchContainer.innerHTML = `
                    <button class="btn btn-sm btn-outline-secondary recent-search-item" 
                        data-query="${query}"
                        data-id="${data.search_id}">
                        ${query}
                    </button>
                    <button class="btn btn-sm btn-outline-danger delete-history-item"
                        data-id="${data.search_id}">
                        <i data-feather="x"></i>
                    </button>
                `;
                historySection.querySelector('.d-flex').prepend(searchContainer);
                feather.replace();
                
                // Show history section if it was hidden
                historySection.classList.remove('d-none');
            }
        })
        .catch(error => {
            // Hide loading state and show error
            loading.classList.add('d-none');
            errorMessage.textContent = 'Произошла ошибка при выполнении запроса';
            errorMessage.classList.remove('d-none');
            console.error('Error:', error);
        });
    });

    // Handle clicks on recent search items
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('recent-search-item')) {
            const query = e.target.dataset.query;
            if (query) {
                searchInput.value = query;
                searchForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Handle delete history item clicks
    document.addEventListener('click', function(e) {
        const deleteBtn = e.target.closest('.delete-history-item');
        if (!deleteBtn) {
            // Проверяем, может быть клик был по иконке внутри кнопки
            const icon = e.target.closest('svg');
            if (icon) {
                const parentBtn = icon.closest('.delete-history-item');
                if (parentBtn) {
                    e.preventDefault();
                    e.stopPropagation();
                    handleDelete(parentBtn);
                }
            }
            return;
        }
        
        e.preventDefault();
        e.stopPropagation();
        handleDelete(deleteBtn);
    });

    // Character counter for input
    searchInput.addEventListener('input', function() {
        if (this.value.length > 200) {
            this.value = this.value.substring(0, 200);
        }
    });
});
