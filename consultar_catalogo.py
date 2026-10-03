import csv
import json
from io import StringIO

import requests
URL = "https://dados.ons.org.br/api/3/action/package_show"
PARAMETROS = {"id": "carga-energia"}

resposta = requests.get(
    URL,
    params=PARAMETROS,
    timeout=20,
)

print("URL consultada:", resposta.url)
print("Status HTTP:", resposta.status_code)
print("Tipo de conteúdo:", resposta.headers.get("Content-Type"))

resposta.raise_for_status()

dados = resposta.json()

if dados.get("success") is not True:
    raise RuntimeError(f"Erro retornado pelo catálogo: {dados.get('error')}")

conjunto = dados["result"]
recursos = conjunto["resources"]

print("\nConjunto:", conjunto["title"])
print("Identificador:", conjunto["name"])
print("Quantidade de recursos:", len(recursos))

csv_2025 = None
dicionario_json = None

for recurso in recursos:
    nome = recurso.get("name")
    formato = recurso.get("format")

    if nome == "Carga_Energia-2025" and formato == "CSV":
        csv_2025 = recurso

    if nome == "Dicionário de Dados Json" and formato == "JSON":
        dicionario_json = recurso

if csv_2025 is None:
    raise RuntimeError("O recurso CSV de 2025 não foi encontrado.")

if dicionario_json is None:
    raise RuntimeError("O dicionário JSON não foi encontrado.")

print("\nURL do CSV de 2025:")
print(csv_2025["url"])

print("\nURL do dicionário JSON:")
print(dicionario_json["url"])

resposta_dicionario = requests.get(
    dicionario_json["url"],
    timeout=20,
)
resposta_dicionario.raise_for_status()

dicionario = resposta_dicionario.json()

print("\nConteúdo do dicionário:")
print(json.dumps(dicionario, indent=2, ensure_ascii=False))

resposta_csv = requests.get(
    csv_2025["url"],
    timeout=20,
)

print("\nStatus HTTP do CSV:", resposta_csv.status_code)
resposta_csv.raise_for_status()

resposta_csv.encoding = "utf-8-sig"
linhas = resposta_csv.text.splitlines()

print("\nPrimeiras seis linhas do CSV:")
for linha in linhas[:6]:
    print(linha)

leitor = csv.DictReader(
    StringIO(resposta_csv.text),
    delimiter=";",
)

registros = list(leitor)

if not registros:
    raise RuntimeError("O CSV não contém registros de dados.")

print("\nQuantidade de registros:", len(registros))

print("\nPrimeiro registro estruturado:")
print(json.dumps(registros[0], indent=2, ensure_ascii=False))