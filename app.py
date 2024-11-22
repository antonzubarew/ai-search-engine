from flask import Flask, render_template, jsonify, request
from config import Config
from services.search import SearchService
from services.gigachat import GigaChatService
import logging

app = Flask(__name__)
app.config.from_object(Config)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

search_service = SearchService(app.config['SEARCH_API_KEY'])
gigachat_service = GigaChatService(app.config['GIGACHAT_API_KEY'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        query = request.json.get('query', '')
        
        if not query:
            return jsonify({'error': 'Пустой запрос'}), 400
            
        if len(query) > app.config['MAX_QUERY_LENGTH']:
            return jsonify({'error': 'Запрос слишком длинный'}), 400

        # Get search results
        search_results = search_service.search(query)
        
        # Get GigaChat response
        giga_response = gigachat_service.get_response(query, search_results)
        
        return jsonify({
            'answer': giga_response,
            'search_results': search_results
        })

    except Exception as e:
        logger.error(f"Error processing search request: {str(e)}")
        return jsonify({'error': 'Произошла ошибка при обработке запроса'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Внутренняя ошибка сервера'}), 500
