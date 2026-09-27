#flask nous permet de crée notre application web
#jsonify : python -> json
from flask import Flask, jsonify

#initialise app Flask
app = Flask(__name__)


#dit à Flask que si user tape url/health execute cette fonction

@app.route('/health')
def heath():
    #return en json tout va bien (code 200 de HTTP)
    return jsonify({"status": "healthy", "service": "projet-devops"}), 200

#pour que les conteneurs docker puisse se parler
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)