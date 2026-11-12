
from flask import Flask, request, jsonify, Response, render_template, redirect, url_for
import json

app = Flask(__name__,
            template_folder = "municipios/templates",
            static_folder="municipios/static")

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

    municipios = municipios_nordeste_dataset["municipios"]

    busca = request.args.get("busca", "").strip().lower()
    uf = request.args.get("uf", "").strip().upper()

    filtrados = {}

    for nome, dados in municipios.items():

        if busca and busca not in nome.lower():
            continue

        if uf and uf != dados["sigla_uf"].upper():
            continue

        filtrados[nome] = dados

    nome_edicao = request.args.get("editar")
    municipio_edicao = municipios.get(nome_edicao) if nome_edicao else None

    return render_template(
        "index.html",
        municipios=filtrados,
        municipio_edicao=municipio_edicao,
        municipio_edicao_nome=nome_edicao,
        busca=busca,
        uf=uf
    )


# 1. Listar municípios ou filtrar por UF 
@app.route("/municipios", methods=["GET"])
def listar_municipios():

    municipios = municipios_nordeste_dataset["municipios"]
    uf = request.args.get("uf", "").strip().upper()

    if uf:
        filtrados = {}

        for nome, dados in municipios.items():
            if dados["sigla_uf"].upper() == uf:
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


# 3. Cadastrar município via JSON
@app.route("/municipios", methods=["POST"])
def cadastrar_municipio():

    dados = request.get_json(silent=True)

    if not isinstance(dados, dict) or not dados.get("nome"):
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


# 4. Atualizar município via PATCH
@app.route("/municipios/<nome>", methods=["PATCH"])
def atualizar_municipio(nome):

    municipios = municipios_nordeste_dataset["municipios"]

    if nome not in municipios:
        return jsonify({
            "erro": "Município não encontrado."
        }), 404

    dados = request.get_json(silent=True)

    if not isinstance(dados, dict) or not dados:
        return jsonify({
            "erro": "Informe os dados que deseja atualizar."
        }), 400

    municipios[nome].update(dados)

    return jsonify({
        "mensagem": "Município atualizado com sucesso!",
        "municipio": {nome: municipios[nome]}
    })


# 5. Excluir município via DELETE
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


# 6. Salvar pelo formulário HTML
@app.route("/salvar", methods=["POST"])
def salvar():

    municipios = municipios_nordeste_dataset["municipios"]

    nome = request.form.get("nome", "").strip()
    nome_original = request.form.get("nome_original", "").strip()

    if not nome:
        return "Informe o nome do município.", 400

    try:
        novo_municipio = {
            "id_ibge": int(request.form["id_ibge"]),
            "estado": request.form["estado"].strip(),
            "sigla_uf": request.form["sigla_uf"].strip().upper(),
            "capital": "capital" in request.form,
            "populacao_estimada": int(request.form["populacao_estimada"])
        }

    except (ValueError, KeyError):
        return "Verifique os dados informados.", 400

    if nome_original and nome_original in municipios:

        if nome != nome_original and nome in municipios:
            return "Esse município já está cadastrado.", 409

        municipios.pop(nome_original)

    elif nome in municipios:
        return "Esse município já está cadastrado.", 409

    municipios[nome] = novo_municipio

    return redirect(url_for("inicio"))


# 7. Excluir pelo formulário HTML
@app.route("/excluir/<nome>", methods=["POST"])
def excluir_pela_pagina(nome):

    municipios = municipios_nordeste_dataset["municipios"]

    if nome in municipios:
        municipios.pop(nome)

    return redirect(url_for("inicio"))


# 8. Baixar arquivo JSON
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
    app.run(debug=True, host="0.0.0.0", port=5000)
