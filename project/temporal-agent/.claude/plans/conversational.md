# Plano: Workflow Conversacional com Signals

## Context

O usuário quer simular um comportamento conversacional — o workflow precisa ficar **vivo** entre mensagens do usuário, manter um histórico, e usar Faker para gerar respostas enquanto a integração com LLM não está pronta.

A investigação no `repos/temporal-ai-agent` revelou o padrão exato a seguir.

---

## Como o projeto de referência resolve isso

### O problema: workflows morrem quando `run()` retorna

Um workflow comum executa e termina. Para uma conversa, ele precisa **esperar** indefinidamente por novas mensagens.

### Solução: `while True` + `wait_condition` + Signals

```
Workflow (vivo indefinidamente)
│
│  while True:
│      await wait_condition(tem mensagem na fila?)
│      ← fica suspenso aqui, sem consumir CPU
│
│  quando chega um signal →
│      prompt_queue.append(mensagem)
│      wait_condition acorda
│      processa → chama activity Faker
│      adiciona resposta ao histórico
│      volta ao topo do loop
```

**Signals** são eventos enviados pelo cliente a um workflow **em execução**. O Temporal entrega o signal, o workflow acorda, processa, e volta a dormir.

### Session ID = Workflow ID

Não é preciso banco de sessões. O próprio ID do workflow no Temporal identifica a conversa. O cliente gera um UUID ao iniciar a sessão e usa ele em todas as chamadas subsequentes.

### `start_workflow` com `start_signal` — início idempotente

O projeto de referência usa um truque elegante:
```python
client.start_workflow(..., start_signal="user_message", start_signal_args=["Oi"])
```
- Se o workflow **não existe** → inicia e entrega o signal imediatamente
- Se o workflow **já existe** → apenas entrega o signal

Assim a API nunca precisa verificar se o workflow está rodando.

---

## Arquivos a criar/modificar

### 1. `libs/temporal_core/activities/chat.py` ← NOVO
Activity que usa Faker para gerar uma resposta:
```python
@activity.defn
async def generate_response(message: str) -> str:
    fake = Faker('pt_BR')
    return fake.sentence()
```

### 2. `libs/temporal_core/workflows/chat.py` ← NOVO
```python
@workflow.defn
class ChatWorkflow:
    def __init__(self):
        self.message_queue: list[str] = []
        self.session_ended = False
        self.history: list[dict] = []

    @workflow.run
    async def run(self) -> list[dict]:
        while not self.session_ended:
            await workflow.wait_condition(
                lambda: bool(self.message_queue) or self.session_ended
            )
            if self.message_queue:
                message = self.message_queue.pop(0)
                self.history.append({"role": "user", "content": message})
                response = await workflow.execute_activity(
                    generate_response, message,
                    start_to_close_timeout=timedelta(seconds=10)
                )
                self.history.append({"role": "assistant", "content": response})
        return self.history

    @workflow.signal
    async def user_message(self, message: str) -> None:
        self.message_queue.append(message)

    @workflow.signal
    async def end_session(self) -> None:
        self.session_ended = True

    @workflow.query
    def get_history(self) -> list[dict]:
        return self.history
```

### 3. `libs/temporal_core/worker/main.py` ← MODIFICAR
Registrar `ChatWorkflow` e `generate_response`.

### 4. `libs/temporal_core/Dockerfile` ← MODIFICAR
Adicionar `COPY activities/ ./activities/` já existe, mas verificar se `chat.py` é copiado automaticamente (sim, copia toda a pasta).

### 5. `libs/api/main.py` ← MODIFICAR
Três novos endpoints:

| Método | Rota | Ação |
|--------|------|------|
| `POST` | `/chat/{session_id}` | Envia mensagem (start_signal se não existe) |
| `POST` | `/chat/{session_id}/end` | Encerra a sessão |
| `GET`  | `/chat/{session_id}/history` | Busca histórico via query |

Payload do POST:
```json
{ "message": "Olá, tudo bem?" }
```

---

## Dependência nova

`faker` precisa ser adicionado ao `pyproject.toml` de `temporal_core`.

---

## Fluxo completo esperado

```
POST /chat/abc-123   {"message": "Oi"}
  → start_workflow(id="abc-123", start_signal="user_message", args=["Oi"])
  → workflow inicia, acorda, chama activity Faker, dorme

POST /chat/abc-123   {"message": "E aí?"}
  → signal "user_message" entregue ao workflow já rodando
  → workflow acorda, chama activity Faker, dorme

GET /chat/abc-123/history
  → query "get_history" no workflow running
  → retorna [{role: user, ...}, {role: assistant, ...}, ...]

POST /chat/abc-123/end
  → signal "end_session"
  → workflow sai do loop, retorna histórico, termina (status: Completed)
```

---

## Verificação

```bash
make up
# Sessão 1
make workflow chat abc-123 "Oi"
make workflow chat abc-123 "Como vai?"
curl http://localhost:8000/chat/abc-123/history
make workflow end abc-123

# Conferir no Temporal UI: http://localhost:8080
# workflow abc-123 deve aparecer como Running até o end, depois Completed
```

---

## Arquivos críticos de referência

- `repos/temporal-ai-agent/workflows/agent_goal_workflow.py` — padrão `while True` + `wait_condition` + signals
- `repos/temporal-ai-agent/api/main.py` — uso de `start_signal` para início idempotente
