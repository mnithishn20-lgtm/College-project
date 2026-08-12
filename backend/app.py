from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
from utils.predictor import CollegePredictor, ChatbotAssistant

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.normpath(os.path.join(BASE_DIR, '..', 'frontend'))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

# Initialize predictor and chatbot
predictor = CollegePredictor()
chatbot = ChatbotAssistant(predictor)

# Store chat history (optional)
chat_history = []

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict colleges based on student marks and category
    """
    try:
        data = request.get_json()
        
        # Extract input parameters
        mathematics = data.get('mathematics')
        physics = data.get('physics')
        chemistry = data.get('chemistry')
        community = data.get('community')
        stream = data.get('stream')
        
        # Validate inputs
        if None in [mathematics, physics, chemistry, community, stream]:
            return jsonify({
                'success': False,
                'error': 'Missing required fields. Please provide mathematics, physics, chemistry, community, and stream.'
            }), 400
        
        # Convert to float and validate ranges
        try:
            mathematics = float(mathematics)
            physics = float(physics)
            chemistry = float(chemistry)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Marks must be valid numbers'
            }), 400
        
        if not (0 <= mathematics <= 100 and 0 <= physics <= 100 and 0 <= chemistry <= 100):
            return jsonify({
                'success': False,
                'error': 'Marks must be between 0 and 100'
            }), 400
        
        # Validate community
        valid_communities = ['OC', 'BC', 'MBC', 'SC', 'ST']
        if community not in valid_communities:
            return jsonify({
                'success': False,
                'error': f'Invalid community. Must be one of: {", ".join(valid_communities)}'
            }), 400
        
        # Validate stream
        valid_streams = ['ENGINEERING', 'SCIENCE', 'ARTS']
        if stream not in valid_streams:
            return jsonify({
                'success': False,
                'error': f'Invalid stream. Must be one of: {", ".join(valid_streams)}'
            }), 400
        
        # Calculate cutoff score
        cutoff_score = predictor.calculate_cutoff(mathematics, physics, chemistry, stream)
        
        # Get matched colleges
        results = predictor.match_colleges(
            cutoff_score,
            community,
            stream
        )
        
        # Get statistics for context
        stats = predictor.get_statistics()
        
        return jsonify({
            'success': True,
            'cutoff_score': results.get('effective_cutoff', cutoff_score),
            'results': {
                'safe': results.get('safe', []),
                'borderline': results.get('borderline', []),
                'dream': results.get('dream', []),
                'total_matched': results.get('total_matched', 0)
            },
            'student_data': {
                'mathematics': mathematics,
                'physics': physics,
                'chemistry': chemistry,
                'community': community,
                'stream': stream
            },
            'statistics': {
                'total_colleges_available': stats.get('total_colleges', 0)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    """
    Chatbot endpoint for college counselling queries
    """
    try:
        data = request.get_json()
        message = data.get('message')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400
        
        # Get chatbot response
        response = chatbot.get_response(message)
        
        # Store in chat history
        chat_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_message': message,
            'bot_response': response
        })
        
        return jsonify({
            'success': True,
            'bot_response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/chat/history', methods=['GET'])
def get_chat_history():
    """
    Get chat history
    """
    try:
        limit = request.args.get('limit', default=50, type=int)
        history = chat_history[-limit:] if limit > 0 else chat_history
        return jsonify({
            'success': True,
            'history': history,
            'total': len(chat_history)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/chat/clear', methods=['POST'])
def clear_chat_history():
    """
    Clear chat history
    """
    try:
        global chat_history
        chat_history = []
        return jsonify({
            'success': True,
            'message': 'Chat history cleared successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/colleges', methods=['GET'])
def get_colleges():
    """
    Get all colleges with optional filters
    """
    try:
        # Get query parameters
        district = request.args.get('district')
        stream = request.args.get('stream')
        college_type = request.args.get('type')
        limit = request.args.get('limit', default=100, type=int)
        
        # Get all colleges from predictor
        all_colleges = predictor.colleges_data if hasattr(predictor, 'colleges_data') else []
        
        # Apply filters
        filtered_colleges = all_colleges.copy()
        
        if district:
            filtered_colleges = [c for c in filtered_colleges if c.get('district', '').lower() == district.lower()]
        
        if stream:
            filtered_colleges = [c for c in filtered_colleges if c.get('stream', '').upper() == stream.upper()]
        
        if college_type:
            filtered_colleges = [c for c in filtered_colleges if c.get('college_type', '').lower() == college_type.lower()]
        
        # Limit results
        filtered_colleges = filtered_colleges[:limit]
        
        return jsonify({
            'success': True,
            'total': len(filtered_colleges),
            'colleges': filtered_colleges
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/colleges/<college_name>', methods=['GET'])
def get_college_details(college_name):
    """
    Get details of a specific college
    """
    try:
        college = predictor.get_college_by_name(college_name)
        
        if college:
            return jsonify({
                'success': True,
                'college': college
            })
        else:
            return jsonify({
                'success': False,
                'error': 'College not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/colleges/districts', methods=['GET'])
def get_districts():
    """
    Get list of all districts with college count
    """
    try:
        stats = predictor.get_statistics()
        districts = stats.get('districts', {})
        
        # Sort by count (descending)
        sorted_districts = sorted(districts.items(), key=lambda x: x[1], reverse=True)
        
        return jsonify({
            'success': True,
            'districts': [{'name': d, 'count': c} for d, c in sorted_districts]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/colleges/streams', methods=['GET'])
def get_streams():
    """
    Get list of all streams with college count
    """
    try:
        stats = predictor.get_statistics()
        streams = stats.get('streams', {})
        
        return jsonify({
            'success': True,
            'streams': [{'name': s, 'count': c} for s, c in streams.items()]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/colleges/stats', methods=['GET'])
def get_college_stats():
    """
    Get college statistics
    """
    try:
        stats = predictor.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    """
    try:
        stats = predictor.get_statistics()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'colleges_loaded': stats.get('total_colleges', 0),
            'districts_available': len(stats.get('districts', {})),
            'streams_available': list(stats.get('streams', {}).keys()),
            'chat_history_count': len(chat_history)
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve frontend static files and fallback to index.html"""
    file_path = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/colleges/community-cutoffs', methods=['GET'])
def get_community_cutoffs():
    """
    Get community cutoff relaxations
    """
    try:
        community_cutoffs = predictor.community_relaxations if hasattr(predictor, 'community_relaxations') else {}
        
        return jsonify({
            'success': True,
            'community_cutoffs': community_cutoffs,
            'description': 'Additional marks added to cutoff for each community'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/colleges/search', methods=['GET'])
def search_colleges():
    """
    Search colleges by name or branch
    """
    try:
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query required'
            }), 400
        
        all_colleges = predictor.colleges_data if hasattr(predictor, 'colleges_data') else []
        
        # Search in college name and branch name
        results = []
        for college in all_colleges:
            college_name = college.get('college_name', '').lower()
            branch_name = college.get('branch_name', '').lower()
            
            if query in college_name or query in branch_name:
                results.append(college)
        
        return jsonify({
            'success': True,
            'total': len(results),
            'colleges': results[:20]  # Limit to 20 results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Print startup message
    print(f"\n{'='*60}")
    print(f"🏛️  Tamil Nadu College Admission Predictor & Chatbot")
    print(f"{'='*60}")
    print(f"📊 Server running on: http://localhost:{port}")
    print(f"📚 Health check: http://localhost:{port}/health")
    print(f"🤖 Chat endpoint: http://localhost:{port}/chat")
    print(f"📈 Predict endpoint: http://localhost:{port}/predict")
    print(f"🏫 Colleges endpoint: http://localhost:{port}/colleges")
    print(f"{'='*60}\n")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=port)