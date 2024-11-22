document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const aiResponse = document.getElementById('aiResponse');
    const searchResults = document.getElementById('searchResults');
    const errorMessage = document.getElementById('errorMessage');

    // Initialize Feather icons
    feather.replace();

    // Function to perform search
    async function performSearch(query) {
        if (!query) {
            showError('Пожалуйста, введите вопрос');
            return;
        }

        // Show loading state
        loading.classList.remove('d-none');
        results.classList.add('d-none');
        errorMessage.classList.add('d-none');

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Произошла ошибка при выполнении запроса');
            }

            // Display AI response
            aiResponse.textContent = data.answer;

            // Display search results
            searchResults.innerHTML = data.search_results.map(result => `
                <div class="search-result-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6>${result.title}</h6>
                            <p>${result.snippet}</p>
                            <a href="${result.link}" target="_blank" rel="noopener noreferrer">
                                Подробнее <i data-feather="external-link"></i>
                            </a>
                        </div>
                        <button class="btn btn-sm btn-outline-danger delete-result">
                            <i data-feather="x"></i>
                        </button>
                    </div>
                </div>
            `).join('');

            // Re-initialize Feather icons for new content
            feather.replace();

            // Show results
            results.classList.remove('d-none');
        } catch (error) {
            showError(error.message);
        } finally {
            loading.classList.add('d-none');
        }
    }

    // Handle form submit
    searchForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const query = searchInput.value.trim();
        await performSearch(query);
    });

    // Handle clicks on recent searches
    document.addEventListener('click', async function(e) {
        if (e.target.classList.contains('recent-search-item')) {
            const query = e.target.dataset.query;
            searchInput.value = query;
            await performSearch(query);
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('d-none');
    }

    // Handle delete result clicks
    document.addEventListener('click', function(e) {
        if (e.target.closest('.delete-result')) {
            const resultItem = e.target.closest('.search-result-item');
            if (resultItem) {
                resultItem.remove();
                
                // Если все результаты удалены, скрыть секцию
                if (searchResults.children.length === 0) {
                    document.querySelector('.search-results').classList.add('d-none');
                }
            }
        }
    });

    // Handle delete history item clicks
    document.addEventListener('click', function(e) {
        if (e.target.closest('.delete-history-item')) {
            const btn = e.target.closest('.delete-history-item');
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
                        historySection.remove();
                    }
                } else {
                    console.error('Ошибка при удалении:', data.error);
                }
            })
            .catch(error => {
                console.error('Ошибка при удалении:', error);
            });
        }
    });
    // Character counter for input
    searchInput.addEventListener('input', function() {
        if (this.value.length > 200) {
            this.value = this.value.substring(0, 200);
        }
    });
});
