
from flask import Flask, render_template, request, jsonify, Response
import json

app = Flask(__name__)

municipios_nordeste_dataset = {
    "metadados": {
        "regiao": "Nordeste",
        "pais": "Brasil",
        "total_municipios": 30,
        "fonte_dados_populacao": "IBGE"
    },

    "municipios": {
        "Fortaleza": {
            "id_ibge": 2304400,
            "estado": "Ceará",
            "sigla_uf": "CE",
            "capital": True,
            "populacao_estimada": 2582360
        },
        "Salvador": {
            "id_ibge": 2927408,
            "estado": "Bahia",
            "sigla_uf": "BA",
            "capital": True,
            "populacao_estimada": 2559945
        }
    }
}

municipios = municipios_nordeste_dataset["municipios"]

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/municipios", methods=["GET"])
def listar():
    uf = request.args.get("uf")

    if uf:
        resultado = {
            nome: dados
            for nome, dados in municipios.items()
            if dados["sigla_uf"].upper() == uf.upper()
        }
        return jsonify(resultado)

    return jsonify(municipios)

@app.route("/municipios/<nome>", methods=["GET"])
def consultar(nome):
    if nome in municipios:
        return jsonify(municipios[nome])

    return jsonify({"erro": "Município não encontrado"}), 404

@app.route("/municipios", methods=["POST"])
def cadastrar():
    dados = request.get_json()

    if not dados or not dados.get("nome"):
        return jsonify({"erro": "Informe o nome do município"}), 400

    nome = dados["nome"].strip()

    if nome in municipios:
        return jsonify({"erro": "Município já cadastrado"}), 409

    campos = [
        "id_ibge", "estado", "sigla_uf",
        "capital", "populacao_estimada"
    ]

    if any(campo not in dados for campo in campos):
        return jsonify({"erro": "Preencha todos os campos"}), 400

    municipios[nome] = {
        campo: dados[campo] for campo in campos
    }

    return jsonify({"mensagem": "Município cadastrado!"}), 201

@app.route("/municipios/<nome>", methods=["PATCH"])
def atualizar(nome):
    if nome not in municipios:
        return jsonify({"erro": "Município não encontrado"}), 404

    dados = request.get_json()

    if not isinstance(dados, dict):
        return jsonify({"erro": "Dados inválidos"}), 400

    campos = [
        "id_ibge", "estado", "sigla_uf",
        "capital", "populacao_estimada"
    ]

    if any(campo not in campos for campo in dados):
        return jsonify({"erro": "Campo inválido"}), 400

    municipios[nome].update(dados)

    return jsonify({"mensagem": "Município atualizado!"})

@app.route("/municipios/<nome>", methods=["DELETE"])
def excluir(nome):
    if nome not in municipios:
        return jsonify({"erro": "Município não encontrado"}), 404

    municipios.pop(nome)
    return jsonify({"mensagem": "Município excluído!"})

@app.route("/municipios/download")
def download():
    arquivo = json.dumps(
        municipios_nordeste_dataset,
        ensure_ascii=False,
        indent=4
    )

    return Response(
        arquivo,
        mimetype="application/json",
        headers={
            "Content-Disposition":
            "attachment; filename=municipios_nordeste.json"
        }
    )

if __name__ == "__main__":
    app.run(debug=True)