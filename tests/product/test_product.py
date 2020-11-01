from fixtures.usuario import cadastrar_usuario
from model.produto import Produto
from copy import copy

import pytest
import random
import requests


class TestProdutos:
    """
    Classe de testes do endpoint /produtos
    """

    def test_buscar_produtos(self, cadastrar_produto, produtos_url):
        produto = cadastrar_produto()

        resposta = requests.get(produtos_url)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 200
        assert resposta_de_sucesso["quantidade"] > 1
        assert produto in resposta_de_sucesso["produtos"]

    def test_buscar_produto_por_id(self, cadastrar_produto, produtos_url):
        produto = cadastrar_produto()

        query = f'?_id={produto["_id"]}'
        resposta = requests.get(produtos_url + query)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 200
        assert resposta_de_sucesso["quantidade"] == 1
        assert resposta_de_sucesso["produtos"][0] == produto

    def test_buscar_produto_por_nome(self, cadastrar_produto, produtos_url):
        produto = cadastrar_produto()

        query = f'?nome={produto["nome"]}'
        resposta = requests.get(produtos_url + query)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 200
        assert resposta_de_sucesso["quantidade"] == 1
        assert resposta_de_sucesso["produtos"][0] == produto

    def test_buscar_produto_por_preco(self, cadastrar_produto, produtos_url):
        produto = cadastrar_produto()

        query = f'?preco={produto["preco"]}'
        resposta = requests.get(produtos_url + query)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 200
        assert resposta_de_sucesso["quantidade"] >= 1

        produtos = resposta_de_sucesso["produtos"]
        somente_preco_buscado = set([item["preco"] for item in produtos])
        assert len(somente_preco_buscado) == 1
        assert somente_preco_buscado.pop() == produto["preco"]

    def test_buscar_produto_por_descricao(self, cadastrar_produto, produtos_url):
        produto = cadastrar_produto()

        query = f'?descricao={produto["descricao"]}'
        resposta = requests.get(produtos_url + query)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 200
        assert resposta_de_sucesso["quantidade"] >= 1

        produtos = resposta_de_sucesso["produtos"]
        somente_descricao_buscado = set(
            [item["descricao"] for item in produtos])
        assert len(somente_descricao_buscado) == 1
        assert somente_descricao_buscado.pop() == produto["descricao"]

    def test_buscar_produto_por_quantidade(self, cadastrar_produto, produtos_url):
        produto = cadastrar_produto()

        query = f'?quantidade={produto["quantidade"]}'
        resposta = requests.get(produtos_url + query)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 200
        assert resposta_de_sucesso["quantidade"] >= 1

        produtos = resposta_de_sucesso["produtos"]
        somente_quantidade_buscado = set(
            [item["quantidade"] for item in produtos])
        assert len(somente_quantidade_buscado) == 1
        assert somente_quantidade_buscado.pop() == produto["quantidade"]

    def test_buscar_produto_por_descricao_e_preco(self, cadastrar_produto, produtos_url):
        produto = cadastrar_produto()

        query = f'?descricao={produto["descricao"]}&preco={produto["preco"]}'
        resposta = requests.get(produtos_url + query)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 200
        assert resposta_de_sucesso["quantidade"] >= 1

        produtos = resposta_de_sucesso["produtos"]
        somente_campo_preco = set(
            [item["preco"] for item in produtos])
        somente_descricao_buscado = set(
            [item["descricao"] for item in produtos])
        assert len(somente_campo_preco) == 1
        assert len(somente_descricao_buscado) == 1
        assert somente_campo_preco.pop() == produto["preco"]
        assert somente_descricao_buscado.pop() == produto["descricao"]

    def test_cadastrar_produto(self, produtos_url, get_auth_token):
        produto = Produto()

        headers = {"Authorization": f"{get_auth_token}"}

        resposta = requests.post(produtos_url, json={
            "nome": produto.nome,
            "preco": produto.preco,
            "descricao": produto.descricao,
            "quantidade": produto.quantidade
        }, headers=headers)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 201
        assert resposta_de_sucesso["message"] == "Cadastro realizado com sucesso"
        assert "_id" in resposta_de_sucesso

    def test_cadastrar_produto_existente(self, faker, cadastrar_produto, produtos_url, get_auth_token):
        produto = cadastrar_produto()

        headers = {"Authorization": f"{get_auth_token}"}

        resposta = requests.post(
            produtos_url, json={
                "nome": produto["nome"],
                "preco": random.randint(10, 30000),
                "descricao": faker.sentence(),
                "quantidade": random.randint(1, 1000)
            }, headers=headers)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 400
        assert resposta_de_sucesso["message"] == "Já existe produto com esse nome"

    def test_cadastrar_produto_com_token_invalido(self, faker, produtos_url):
        produto = Produto()

        headers = {"Authorization": f"{faker.uuid4()}"}

        resposta = requests.post(
            produtos_url, json={
                "nome": produto.nome,
                "preco": produto.preco,
                "descricao": produto.descricao,
                "quantidade": produto.quantidade
            }, headers=headers)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 401
        assert resposta_de_sucesso["message"] == "Token de acesso ausente, inválido, expirado ou usuário do token não existe mais"

    def test_cadastrar_produto_non_admin(self, produtos_url, cadastrar_usuario, login_url):
        usuario = cadastrar_usuario(administrador="false")
        resposta = requests.post(login_url, json={
            "email": usuario["email"],
            "password": usuario["password"]
        })
        resposta_de_sucesso = resposta.json()

        produto = Produto()

        headers = {"Authorization": f'{resposta_de_sucesso["authorization"]}'}

        resposta = requests.post(
            produtos_url, json={
                "nome": produto.nome,
                "preco": produto.preco,
                "descricao": produto.descricao,
                "quantidade": produto.quantidade
            }, headers=headers)

        resposta_de_sucesso = resposta.json()
        print(resposta_de_sucesso)
        assert resposta.status_code == 403
        assert resposta_de_sucesso["message"] == "Rota exclusiva para administradores"

    def test_editar_produto(self, cadastrar_produto, produtos_url, get_auth_token):
        produto = cadastrar_produto()
        produto_modificado = copy(produto)
        produto_modificado["preco"] = random.randint(10, 30000)

        headers = {"Authorization": f"{get_auth_token}"}

        resposta = requests.put(
            produtos_url + f'/{produto["_id"]}', json={
                "nome": produto_modificado["nome"],
                "preco": produto_modificado["preco"],
                "descricao": produto_modificado["descricao"],
                "quantidade": produto_modificado["quantidade"]
            }, headers=headers)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 200
        assert resposta_de_sucesso["message"] == "Registro alterado com sucesso"

        query = f'?_id={produto["_id"]}'
        resposta = requests.get(produtos_url + query)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 200
        assert resposta_de_sucesso["produtos"][0] == produto_modificado

    def test_editar_criando_produto(self, faker, produtos_url, get_auth_token):
        produto = Produto()
        produto_id = faker.uuid4()

        headers = {"Authorization": f"{get_auth_token}"}

        resposta = requests.put(
            produtos_url + f'/{produto_id}', json={
                "nome": produto.nome,
                "preco": produto.preco,
                "descricao": produto.descricao,
                "quantidade": produto.quantidade
            }, headers=headers)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 201
        assert resposta_de_sucesso["message"] == "Cadastro realizado com sucesso"

    def test_editar_criando_produto_nome_existente(self, faker, cadastrar_produto, produtos_url, get_auth_token):
        produto = cadastrar_produto()
        produto_modificado = copy(produto)
        produto_modificado_id = faker.uuid4()
        produto_modificado["preco"] = random.randint(10, 30000)

        headers = {"Authorization": f"{get_auth_token}"}

        resposta = requests.put(
            produtos_url + f'/{produto_modificado_id}', json={
                "nome": produto_modificado["nome"],
                "preco": produto_modificado["preco"],
                "descricao": produto_modificado["descricao"],
                "quantidade": produto_modificado["quantidade"]
            }, headers=headers)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 400
        assert resposta_de_sucesso["message"] == "Já existe produto com esse nome"

    def test_editar_produto_com_token_invalido(self, faker, cadastrar_produto, produtos_url):
        produto = cadastrar_produto()
        produto_modificado = copy(produto)
        produto_modificado["preco"] = random.randint(10, 30000)

        headers = {"Authorization": f"{faker.uuid4()}"}

        resposta = requests.put(
            produtos_url + f'/{produto["_id"]}', json={
                "nome": produto_modificado["nome"],
                "preco": produto_modificado["preco"],
                "descricao": produto_modificado["descricao"],
                "quantidade": produto_modificado["quantidade"]
            }, headers=headers)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 401
        assert resposta_de_sucesso["message"] == "Token de acesso ausente, inválido, expirado ou usuário do token não existe mais"

    def test_editar_produto_non_admin(self, cadastrar_usuario, login_url, cadastrar_produto, produtos_url):
        usuario = cadastrar_usuario(administrador="false")
        resposta = requests.post(login_url, json={
            "email": usuario["email"],
            "password": usuario["password"]
        })

        resposta_de_sucesso = resposta.json()

        produto = cadastrar_produto()
        produto_modificado = copy(produto)
        produto_modificado["preco"] = random.randint(10, 30000)

        headers = {"Authorization": f"{resposta_de_sucesso['authorization']}"}

        resposta = requests.put(
            produtos_url + f'/{produto["_id"]}', json={
                "nome": produto_modificado["nome"],
                "preco": produto_modificado["preco"],
                "descricao": produto_modificado["descricao"],
                "quantidade": produto_modificado["quantidade"]
            }, headers=headers)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 403
        assert resposta_de_sucesso["message"] == "Rota exclusiva para administradores"

    def test_delete_produto(self, cadastrar_produto, produtos_url, get_auth_token):
        produto = cadastrar_produto()

        headers = {"Authorization": f"{get_auth_token}"}

        resposta = requests.delete(
            produtos_url + f'/{produto["_id"]}', headers=headers)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 200
        assert resposta_de_sucesso["message"] == "Registro excluído com sucesso"

    def test_delete_produto_inexistente(self, faker, produtos_url, get_auth_token):
        headers = {"Authorization": f"{get_auth_token}"}

        resposta = requests.delete(
            produtos_url + f'/{faker.uuid4()}', headers=headers)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 200
        assert resposta_de_sucesso["message"] == "Nenhum registro excluído"

    # TODO: Aguardar teste suite de carrinho
    def test_delete_produto_com_carrinho(self):
        print("Não implementado ainda")
        assert True == False

    def test_editar_produto_com_token_invalido(self, faker, cadastrar_produto, produtos_url):
        produto = cadastrar_produto()

        headers = {"Authorization": f"{faker.uuid4()}"}

        resposta = requests.delete(
            produtos_url + f'/{produto["_id"]}', headers=headers)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 401
        assert resposta_de_sucesso["message"] == "Token de acesso ausente, inválido, expirado ou usuário do token não existe mais"

    def test_delete_produto_non_admin(self, cadastrar_usuario, login_url, cadastrar_produto, produtos_url):
        usuario = cadastrar_usuario(administrador="false")
        resposta = requests.post(login_url, json={
            "email": usuario["email"],
            "password": usuario["password"]
        })

        resposta_de_sucesso = resposta.json()

        produto = cadastrar_produto()

        headers = {"Authorization": f"{resposta_de_sucesso['authorization']}"}

        resposta = requests.delete(
            produtos_url + f'/{produto["_id"]}', headers=headers)

        resposta_de_sucesso = resposta.json()
        assert resposta.status_code == 403
        assert resposta_de_sucesso["message"] == "Rota exclusiva para administradores"
