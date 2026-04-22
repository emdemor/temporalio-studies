# Temporal 101 com Python: Ambiente Local via Docker

Este repositório contém a configuração Docker para rodar o ambiente de desenvolvimento do curso [Temporal 101 Python](https://github.com/temporalio/edu-101-python-code) de forma reproduzível, sem precisar instalar o Temporal CLI, Python ou dependências diretamente na sua máquina.

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado e em execução
- [Docker Compose](https://docs.docker.com/compose/install/) (já incluso no Docker Desktop)
- [Git](https://git-scm.com/downloads)

## Estrutura dos serviços

O `docker-compose.yml` sobe três serviços:

| Serviço | Imagem | Descrição |
|---|---|---|
| `temporal` | `temporalio/auto-setup` | Servidor Temporal em modo desenvolvimento, usando SQLite como banco de dados. Não requer PostgreSQL ou Cassandra. |
| `temporal-ui` | `temporalio/ui` | Interface web para monitorar Workflows, Activities e Workers. Acessível em `http://localhost:8080`. |
| `app` | Build local | Container Python 3.10 com as dependências do curso instaladas. Usado para rodar os exercícios. |

## Estrutura do repositório

```
temporal-io/
  workspace/          # arquivos do curso e seus exercícios (sincronizado com o container)
  Dockerfile          # imagem Python usada pelo serviço app
  docker-compose.yml  # orquestração dos serviços
  README.md
```

A pasta `workspace/` é o único lugar onde você vai trabalhar. Tudo que for criado ou editado ali aparece imediatamente dentro do container, e vice-versa.

## Primeiros passos

### 1. Clone o repositório do curso

```bash
make setup
```

Isso clona os arquivos do curso diretamente na pasta `workspace/`.

### 2. Suba o ambiente

```bash
make build
make up
```

Aguarde as mensagens de inicialização dos três serviços. O servidor Temporal leva alguns segundos para estar completamente disponível.

### 3. Acesse a interface web

Abra o navegador em `http://localhost:8080`. Você verá o Temporal Web UI, onde é possível acompanhar a execução de Workflows em tempo real.

## Comandos disponíveis

| Comando | O que faz |
|---|---|
| `make setup` | Clona o repositório do curso na pasta `workspace/` |
| `make build` | Constrói a imagem Docker do serviço Python |
| `make up` | Sobe todos os serviços (Temporal, UI e app) |
| `make down` | Para e remove todos os containers |
| `make shell` | Abre um terminal bash dentro do container Python |
| `make logs` | Acompanha os logs de todos os serviços em tempo real |
| `make restart` | Reinicia apenas o container Python |

## Rodando os exercícios do curso

Com o ambiente no ar, abra um novo terminal e acesse o container:

```bash
make shell
```

Dentro do container, o diretório `/app` é a pasta `workspace/` local. Rode os scripts normalmente:

```bash
python worker.py
```

Qualquer edição feita no editor de texto dentro de `workspace/` aparece imediatamente no container, sem precisar reiniciar nada.

## Fluxo típico de uso

Durante o curso, você usará pelo menos dois terminais simultaneamente.

**Terminal 1:** deixa o ambiente rodando.

```bash
make up
```

**Terminal 2:** executa os comandos dos exercícios.

```bash
make shell
# dentro do container:
python worker.py
```

**Terminal 3 (opcional):** para rodar o cliente ou disparar Workflows em paralelo.

```bash
make shell
# dentro do container:
python start_workflow.py
```

## Portas utilizadas

| Porta | Serviço | Uso |
|---|---|---|
| `7233` | Temporal Server | Comunicação gRPC dos Workers e Workflows com o servidor |
| `8080` | Temporal UI | Interface web de monitoramento |

Certifique-se de que essas portas não estão ocupadas por outros processos antes de subir o ambiente.

## Variável de ambiente TEMPORAL_ADDRESS

O container `app` recebe automaticamente a variável `TEMPORAL_ADDRESS=temporal:7233`. Dentro dos scripts Python do curso, sempre que precisar apontar para o servidor Temporal, use esse endereço:

```python
client = await Client.connect("temporal:7233")
```

O nome `temporal` é resolvido pelo Docker internamente para o container do servidor. Fora do Docker (caso rode scripts direto na sua máquina), o endereço seria `localhost:7233`.

## Sobre o banco de dados SQLite

O servidor Temporal sobe com `DB=sqlite`, o que significa que todos os dados de Workflow ficam armazenados em memória durante a execução. Ao rodar `docker compose down`, o histórico de Workflows é perdido. Isso é o comportamento esperado e adequado para um ambiente de aprendizado.

## Referências

- Repositório do curso: https://github.com/temporalio/edu-101-python-code
- Documentação do Temporal: https://docs.temporal.io
- Temporal Python SDK: https://github.com/temporalio/sdk-python
