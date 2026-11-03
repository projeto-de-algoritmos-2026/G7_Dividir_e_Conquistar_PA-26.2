# STOCK.IO - Backend em Python com FastAPI & Supabase

API REST assíncrona desenvolvida em **Python (FastAPI)** integrada ao banco de dados e autenticação do **Supabase**.

---

## 🚀 Como Executar o Backend

### 1. Instalar Dependências
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar o Supabase (.env)
Copie o arquivo `.env.example` para `.env` e adicione suas credenciais obtidas no painel do Supabase (*Project Settings -> API*):
```env
SUPABASE_URL=https://<seu-projeto>.supabase.co
SUPABASE_KEY=<sua-anon-key-ou-service-role-key>
```

### 3. Iniciar o Servidor
```bash
uvicorn app.main:app --reload --port 8000
```

---

## 📚 Documentação da API

- **Swagger UI Interativo**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📌 Endpoints Principais

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/auth/register` | Registro de novos usuários com nome completo, email e senha |
| `POST` | `/api/auth/login` | Autenticação de usuário com email e senha |
| `GET` | `/api/auth/health` | Verificação do status do servidor e Supabase |
| `POST` | `/api/schedule/count-inversions` | Avalia a fila manual e recalcula seu cronograma sem reordenar os pedidos |

## Avaliador de Rota Manual

Na tela `/delivery/batchOrder`, gere o lote com Minimize Lateness e use as setas
da Fila Manual para alterar a ordem. O mapa e os horários acompanham a nova fila.
O comando **Restaurar Fila Ideal** recupera a sequência EDF original.

O algoritmo em `app/algoritmos/count_inversions.py` mapeia os IDs para suas posições
na fila EDF e conta inversões por merge sort: tempo O(n log n), memória O(n).
Deadlines empatados mantêm a ordem estável da fila EDF existente.

Para n pedidos, o máximo de inversões é n(n-1)/2. O score é
`100 * (1 - inversoes / maximo)`; lotes vazios ou unitários recebem 100%.
Zero inversões significa **Rota Perfeita** em relação à fila de referência.
Entre os demais casos, até 1/3 do máximo é risco baixo; até 2/3, moderado;
acima disso, alto. Essa classificação é uma heurística de desvio da ordem EDF,
não uma probabilidade de atraso nem garantia de entrega no prazo.
Os atrasos em minutos são calculados separadamente pelos tempos de cada trecho.

O endpoint recebe `orders`, `manualOrderIds`, `startTime`,
`segmentDurationsMinutes` e `serviceTimeMinutes` (opcional, padrão 5).
Retorna `idealOrderIds`, `manualOrderIds`, `inversions`, `maxInversions`,
`efficiencyScore`, `riskLevel` e `scheduleResult`. Filas incompletas, IDs
duplicados/desconhecidos e durações inválidas são rejeitados com HTTP 422.

Execute os testes a partir de `backend`, com as dependências instaladas:

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
```
