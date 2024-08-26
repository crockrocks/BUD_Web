from flask import Flask, send_from_directory, jsonify, request
import requests
import json
import os

app = Flask(__name__, static_folder='dist')

def get_access_token():
    url = "https://iam.cloud.ibm.com/identity/token"
    payload = 'grant_type=urn%3Aibm%3Aparams%3Aoauth%3Agrant-type%3Aapikey&apikey=PHOHucRMFU8cE0MB5_Xndc7LuzfeBtscn8wEfOo7f1_h'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, headers=headers, data=payload)
    return response.json().get("access_token")

def load_context(character):
    with open(f'characters/{character}/example.json', 'r') as file:
        return json.load(file)

def make_api_call(input_user, character):
    access_token = get_access_token()
    context_json = load_context(character)

    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    payload = json.dumps({
        "input": f"{context_json}Input: {input_user}\n\nOutput:",
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 200,
            "min_new_tokens": 0,
            "stop_sequences": ["additional","input","\n"],
            "stop_sequences": [],
            "repetition_penalty": 1
        },
        "model_id": "ibm/granite-13b-chat-v2",
        "project_id": "93fe2e61-f4bc-426e-b081-5a59f704a93f"
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.post(url, headers=headers, data=payload)
    return response.json()['results'][0]['generated_text']

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    input_user = data.get('input_user')
    character = data.get('character')

    if not input_user or not character:
        return jsonify({'error': 'Both input_user and character are required'}), 400

    try:
        generated_text = make_api_call(input_user, character)
        return jsonify({'generated_text': generated_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def serve_react_app():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(app.static_folder, 'assets'), filename)

@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(app.static_folder, 'images'), filename)

if __name__ == '__main__':
    app.run(debug=True)
