#agregando comentarios pq me da miedo que no sea un release cada semana
from flask import Flask, jsonify    
from flask_cors import CORS 
app = Flask(__name__)
CORS(app)   
@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        'message': 'Hello, World!',
        'status': 'success'
    }
    return jsonify(data)
if __name__ == '__main__':
    app.run(debug=True)
#agregando comentarios pq me da miedo que no sea un release cada semana
