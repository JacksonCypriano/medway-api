### Projeto Medway

Aqui nesse repositório temos um projeto Django básico, já configurado para uso.

Para rodar o projeto, deve-se ter o docker e ligado instalado no computador.

Para configurár o projeto, pode-se rodar o comando:

`docker compose up --build`.

Isso deve inicializá-lo na porta 8000.

Ele já vai vir com alguns modelos, alguns inclusives já populados com dados de teste, 
para facilitar o desenvolvimento.

Com o projeto rodando, para acessar o container do docker, pode-se abrir outro terminal e rodar:

`docker exec -it medway-api bash`

Uma vez dentro do container, pode-se criar um usuário/estudante com o comando:

`python manage.py createsuperuser`

E utilizar essas credenciais para acessar o admin em http://0.0.0.0:8000/admin/.


# Documentação da API de Exames

Esta documentação descreve os endpoints principais para:

1. **Criar submissão de exame (responder prova)**
2. **Consultar resultados de uma submissão**
3. **Entender a estrutura dos ViewSets e Serializers**
4. **Exemplos de payload**

---

## Endpoints

---

## Criar uma Submissão de Exame  
`POST /submissions/`

Permite que o aluno envie todas as respostas da prova de uma vez.

### Payload esperado
```json
{
  "student_name": "João",
  "exam": 1,
  "answers": [
    { "question": 10, "selected_option": 2 },
    { "question": 11, "selected_option": 1 },
    ...
  ]
}
```

Ou apenas uma resposta.
### Payload esperado
```json
{
  "student_name": "João",
  "exam": 1,
  "answers": [
    { "question": 10, "selected_option": 2 }
  ]
}
```

### Resposta
```json
{
  "id": 5,
  "student_name": "João",
  "exam": 1,
  "created_at": "2026-01-10T18:00:00Z",
  "answers": [
    { "question": 10, "selected_option": 2 },
    { "question": 11, "selected_option": 1 }
  ]
}
```

---

## Consultar o Resultado de uma Submissão  
`GET /submissions/{id}/result/`

Retorna:

- lista das questões
- alternativas selecionadas e corretas
- acertos
- percentual final

### Exemplo de resposta
```json
{
  "student_name": "João",
  "exam": 1,
  "results": [
    {
      "question": 10,
      "selected_option": 2,
      "correct_option": 2,
      "is_correct": true
    },
    {
      "question": 11,
      "selected_option": 1,
      "correct_option": 3,
      "is_correct": false
    }
  ],
  "score": {
    "correct": 1,
    "total": 2
  },
  "percentage": 50.0
}
```

---

# Exemplos de uso (curl)

### Criar submissão
```bash
curl -X POST http://localhost:8000/submissions/   -H "Content-Type: application/json"   -d '{
    "student_name": "João",
    "exam": 1,
    "answers": [{"question": 10, "selected_option": 2}]
  }'
```

### Resultado
```bash
curl http://localhost:8000/submissions/5/result/
```

---

# Documentação Automática

Se ativada:

- Swagger UI → `/api/docs/`
- ReDoc → `/api/redoc/`
- OpenAPI → `/api/schema/`

---
