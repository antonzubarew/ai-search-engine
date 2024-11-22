from flask import Flask, render_template, jsonify, request
from config import Config
from services.search import SearchService
from services.tavily_service import TavilyService
from services.history import HistoryService
import logging

app = Flask(__name__)
app.config.from_object(Config)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

search_service = SearchService()
tavily_service = TavilyService(app.config['TAVILY_API_KEY'])
history_service = HistoryService()

@app.route('/')
def index():
    recent_searches = history_service.get_recent_searches()
    return render_template('index.html', recent_searches=recent_searches)

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Ожидается JSON'}), 400
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Пустой запрос'}), 400
            
        if len(query) > app.config['MAX_QUERY_LENGTH']:
            return jsonify({'error': 'Запрос слишком длинный'}), 400

        # Save search query to history
        search_entry = history_service.add_search(query)
        if not search_entry:
            return jsonify({'error': 'Ошибка при сохранении запроса'}), 500

        # Get search results
        search_results = search_service.search(query)
        
        # Get Tavily response
        ai_response = tavily_service.get_response(query, search_results)
        
        return jsonify({
            'ai_response': ai_response,
            'search_results': search_results,
            'search_id': search_entry.id
        })

    except Exception as e:
        logger.error(f"Error processing search request: {str(e)}")
        return jsonify({'error': 'Произошла ошибка при обработке запроса'}), 500


@app.route('/history/<int:search_id>', methods=['DELETE'])
def delete_search(search_id):
    try:
        history_service.delete_search(search_id)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting search history: {str(e)}")
        return jsonify({'error': 'Ошибка при удалении записи'}), 500

@app.route('/search/last_id')
def get_last_search_id():
    try:
        last_search = history_service.get_last_search()
        return jsonify({'id': last_search.id if last_search else None})
    except Exception as e:
        logger.error(f"Error getting last search ID: {str(e)}")
        return jsonify({'error': 'Ошибка при получении ID'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Внутренняя ошибка сервера'}), 500
