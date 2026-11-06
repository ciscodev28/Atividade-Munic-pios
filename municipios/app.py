
from flask import Flask, request, jsonify, Response
import json

app = Flask(__name__)

# Dicionário inicial de municípios
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


# Página inicial
@app.route("/")
def inicio():
    return """
        <h1>Cadastro de Municípios do Nordeste</h1>

        <p>Aplicativo desenvolvido com Flask.</p>

        <a href="/municipios">Listar municípios</a>
        <br><br>
        <a href="/municipios/baixar">Baixar arquivo JSON</a>
    """


# 1. Listar todos os municípios ou filtrar por estado
@app.route("/municipios", methods=["GET"])
def listar_municipios():

    uf = request.args.get("uf")

    municipios = municipios_nordeste_dataset["municipios"]

    if uf:
        filtrados = {}

        for nome, dados in municipios.items():
            if dados["sigla_uf"].upper() == uf.upper():
                filtrados[nome] = dados

        return jsonify(filtrados)

    return jsonify(municipios)


# 2. Consultar município pelo nome
@app.route("/municipios/<nome>", methods=["GET"])
def consultar_municipio(nome):

    municipios = municipios_nordeste_dataset["municipios"]

    if nome in municipios:
        return jsonify({
            nome: municipios[nome]
        })

    return jsonify({
        "erro": "Município não encontrado."
    }), 404


# 3. Cadastrar novo município
@app.route("/municipios", methods=["POST"])
def cadastrar_municipio():

    dados = request.get_json()

    if not dados or "nome" not in dados:
        return jsonify({
            "erro": "Informe o nome do município."
        }), 400

    nome = dados["nome"].strip()

    if not nome:
        return jsonify({
            "erro": "O nome não pode ficar vazio."
        }), 400

    municipios = municipios_nordeste_dataset["municipios"]

    if nome in municipios:
        return jsonify({
            "erro": "Esse município já está cadastrado."
        }), 409

    novo_municipio = dados.copy()
    novo_municipio.pop("nome")

    municipios[nome] = novo_municipio

    return jsonify({
        "mensagem": "Município cadastrado com sucesso!",
        "municipio": {nome: municipios[nome]}
    }), 201


# 4. Atualizar município
@app.route("/municipios/<nome>", methods=["PATCH"])
def atualizar_municipio(nome):

    municipios = municipios_nordeste_dataset["municipios"]

    if nome not in municipios:
        return jsonify({
            "erro": "Município não encontrado."
        }), 404

    dados = request.get_json()

    if not isinstance(dados, dict) or not dados:
        return jsonify({
            "erro": "Informe os dados que deseja atualizar."
        }), 400

    # Atualiza somente os campos enviados
    municipios[nome].update(dados)

    return jsonify({
        "mensagem": "Município atualizado com sucesso!",
        "municipio": {nome: municipios[nome]}
    })


# 5. Excluir município
@app.route("/municipios/<nome>", methods=["DELETE"])
def excluir_municipio(nome):

    municipios = municipios_nordeste_dataset["municipios"]

    if nome not in municipios:
        return jsonify({
            "erro": "Município não encontrado."
        }), 404

    municipios.pop(nome)

    return jsonify({
        "mensagem": "Município excluído com sucesso!"
    })


# 6. Baixar todos os municípios em arquivo JSON
@app.route("/municipios/baixar", methods=["GET"])
def baixar_json():

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


# Inicialização do servidor
if __name__ == "__main__":
    app.run(debug=True)
