from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import werkzeug
import pandas as pd
from datetime import datetime
from bson.objectid import ObjectId

# 1. Configurações Iniciais
load_dotenv()

app = Flask(__name__)
CORS(app) # Permite conexão do Frontend Vue

# Configuração da pasta de uploads (fotos)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 2. Conexão com o Banco de Dados
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)

# IMPORTANTE: Se seu banco chama 'Database', mantenha assim.
db = client.get_database("Database")

instituicoes_col = db.instituicoes
associados_col = db.associados
carteirinhas_col = db.carteirinhas

# --- ROTA INICIAL (Teste de Conexão) ---
@app.route('/')
def index():
    return jsonify({"message": "API Carteirinha4u Online e Completa!"})

# --- ROTA DE LOGIN (Com Toggle) ---
@app.route('/login', methods=['POST'])
def login():
    dados_req = request.get_json()
    email = dados_req.get('email')
    senha = dados_req.get('senha')
    tipo_selecionado = dados_req.get('tipo') 

    usuario = None

    if tipo_selecionado == 'instituicao':
        usuario = instituicoes_col.find_one({"email": email})
    elif tipo_selecionado == 'associado':
        usuario = associados_col.find_one({"email": email})
    
    if usuario and usuario.get('senha') == senha:
        dados_user = usuario.get('dados', {})
        nome_usuario = dados_user.get('nome_fantasia') or dados_user.get('nome') or "Usuário"
        
        return jsonify({
            "message": "Login realizado!",
            "nome": nome_usuario,
            "tipo": tipo_selecionado,
            "id": str(usuario['_id']),
            "dados": dados_user  # <--- LINHA IMPORTANTE ADICIONADA!
        }), 200
    else:
        return jsonify({"message": "Usuário ou senha incorretos."}), 401
    
# --- ROTA DE CADASTRO (Com Upload de Foto) ---
@app.route('/register', methods=['POST'])
def register():
    tipo = request.form.get('tipo')
    email = request.form.get('email')
    senha = request.form.get('senha')
    
    colecao = associados_col if tipo == 'associado' else instituicoes_col
    
    if colecao.find_one({"email": email}):
        return jsonify({"message": "Email já cadastrado!"}), 400

    # Salvar Foto
    caminho_foto = None
    arquivo_foto = request.files.get('foto')
    
    if arquivo_foto:
        filename = werkzeug.utils.secure_filename(arquivo_foto.filename)
        nome_salvo = f"{tipo}_{email}_{filename}"
        arquivo_foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_salvo))
        caminho_foto = f"http://127.0.0.1:5000/uploads/{nome_salvo}"

    # Monta Objeto
    if tipo == 'associado':
        novo_usuario = {
            "tipo_usuario": "associado",
            "email": email,
            "senha": senha,
            "status": "ativo", # Padrão ao criar
            "dados": {
                "nome": request.form.get('nome'),
                "cpf": request.form.get('cpf'),
                "data_nascimento": request.form.get('data_nascimento'),
                "foto_url": caminho_foto
            }
        }
    else:
        novo_usuario = {
            "tipo_usuario": "instituicao",
            "email": email,
            "senha": senha,
            "dados": {
                "nome_fantasia": request.form.get('nome'),
                "cnpj": request.form.get('cpf'),
                "logo_url": caminho_foto
            }
        }

    colecao.insert_one(novo_usuario)
    return jsonify({"message": "Cadastro realizado!"}), 201

# Rota para servir as fotos
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- ROTAS DO DASHBOARD (CRUD e Planilha) ---

# 1. Listar Associados
@app.route('/associados', methods=['GET'])
def get_associados():
    usuarios = list(associados_col.find({}, {"senha": 0}))
    for user in usuarios:
        user['_id'] = str(user['_id'])
        if 'status' not in user: user['status'] = 'ativo'
    return jsonify(usuarios), 200

# 2. Atualizar Associado
@app.route('/associados/<id>', methods=['PUT'])
def update_associado(id):
    dados = request.get_json()
    dados.pop('_id', None) # Proteção
    associados_col.update_one({"_id": ObjectId(id)}, {"$set": dados})
    return jsonify({"message": "Atualizado!"}), 200

# 3. Deletar Associado
@app.route('/associados/<id>', methods=['DELETE'])
def delete_associado(id):
    associados_col.delete_one({"_id": ObjectId(id)})
    return jsonify({"message": "Removido!"}), 200

# 4. Comparar Planilha
@app.route('/comparar-planilha', methods=['POST'])
def comparar_planilha():
    if 'arquivo' not in request.files:
        return jsonify({"message": "Sem arquivo"}), 400
        
    arquivo = request.files['arquivo']
    try:
        if arquivo.filename.endswith('.csv'):
            df = pd.read_csv(arquivo)
        else:
            df = pd.read_excel(arquivo)
            
        # Pega lista de CPFs da planilha e limpa formatação
        cpfs_planilha = df['CPF'].astype(str).str.replace(r'[.\-]', '', regex=True).tolist()
        
        associados_db = list(associados_col.find({}, {"dados.cpf": 1}))
        ids_para_inativar = []
        
        for associado in associados_db:
            cpf_banco = associado.get('dados', {}).get('cpf', '').replace('.', '').replace('-', '')
            if cpf_banco and cpf_banco not in cpfs_planilha:
                ids_para_inativar.append(str(associado['_id']))
                
        return jsonify({
            "ids_para_inativar": ids_para_inativar 
        }), 200 
    except Exception as e:
        return jsonify({"message": f"Erro na leitura: {str(e)}"}), 500

# 5. Inativar em Massa
@app.route('/inativar-em-massa', methods=['POST'])
def inativar_massa():
    ids = request.get_json().get('ids', [])
    data_hoje = datetime.now().isoformat()
    
    associados_col.update_many(
        {"_id": {"$in": [ObjectId(id) for id in ids]}},
        {
            "$set": {
                "status": "inativo",
                "data_inativacao": data_hoje
            }
        }
    )
    return jsonify({"message": "Usuários inativados!"}), 200

if __name__ == '__main__':
    app.run(debug=True)