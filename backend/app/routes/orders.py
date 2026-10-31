from fastapi import APIRouter, HTTPException
from app.database import db as prisma
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/api",
    tags=["Orders and Checkout"]
)

class OrderItemInput(BaseModel):
    id: int
    quantity: int

class CheckoutPayload(BaseModel):
    items: List[OrderItemInput]
    cep: str
    user_id: Optional[str] = None
    deadline: Optional[str] = None

# Pedidos de demonstração resilientes com prazos realistas
DEMO_ORDERS = [
    {
        "id": 101,
        "userId": "usr-01",
        "customerName": "Mariana Silva",
        "cep": "70710-500",
        "address": "SHCGN 702/703 Bloco B - Asa Norte, Brasília/DF",
        "totalPrice": 499.90,
        "createdAt": (datetime.now() - timedelta(minutes=60)).isoformat(),
        "deadline": (datetime.now() + timedelta(minutes=35)).replace(microsecond=0).isoformat(),
        "items": [
            {
                "id": 1,
                "productId": 1,
                "quantity": 1,
                "price": 499.90,
                "product": {"name": "Tênis Esportivo Nike Zoom", "price": 499.90}
            }
        ]
    },
    {
        "id": 102,
        "userId": "usr-02",
        "customerName": "Lucas Mendes",
        "cep": "70040-010",
        "address": "SBS Quadra 2 Bloco E - Asa Sul, Brasília/DF",
        "totalPrice": 650.00,
        "createdAt": (datetime.now() - timedelta(minutes=45)).isoformat(),
        "deadline": (datetime.now() + timedelta(minutes=20)).replace(microsecond=0).isoformat(),
        "items": [
            {
                "id": 2,
                "productId": 5,
                "quantity": 1,
                "price": 650.00,
                "product": {"name": "Teclado Mecânico Keychron K2", "price": 650.00}
            }
        ]
    },
    {
        "id": 103,
        "userId": "usr-03",
        "customerName": "Beatriz Costa",
        "cep": "70070-600",
        "address": "Setor de Autarquias Sul Quadra 3 - Brasília/DF",
        "totalPrice": 1899.00,
        "createdAt": (datetime.now() - timedelta(minutes=30)).isoformat(),
        "deadline": (datetime.now() + timedelta(minutes=65)).replace(microsecond=0).isoformat(),
        "items": [
            {
                "id": 3,
                "productId": 2,
                "quantity": 1,
                "price": 1899.00,
                "product": {"name": "Headphone Sony WH-1000XM4", "price": 1899.00}
            }
        ]
    },
    {
        "id": 104,
        "userId": "usr-04",
        "customerName": "Rodrigo Alves",
        "cep": "70390-020",
        "address": "SEPS 702/902 Ed. Lex - Asa Sul, Brasília/DF",
        "totalPrice": 249.90,
        "createdAt": (datetime.now() - timedelta(minutes=25)).isoformat(),
        "deadline": (datetime.now() + timedelta(minutes=50)).replace(microsecond=0).isoformat(),
        "items": [
            {
                "id": 4,
                "productId": 6,
                "quantity": 1,
                "price": 249.90,
                "product": {"name": "Mochila Dell Pro Slim 15", "price": 249.90}
            }
        ]
    },
    {
        "id": 105,
        "userId": "usr-05",
        "customerName": "Camila Rocha",
        "cep": "70670-400",
        "address": "CCSW 04 Lote 3 - Sudoeste, Brasília/DF",
        "totalPrice": 1250.00,
        "createdAt": (datetime.now() - timedelta(minutes=15)).isoformat(),
        "deadline": (datetime.now() + timedelta(minutes=90)).replace(microsecond=0).isoformat(),
        "items": [
            {
                "id": 5,
                "productId": 7,
                "quantity": 1,
                "price": 1250.00,
                "product": {"name": "Cadeira Gamer ThunderX3", "price": 1250.00}
            }
        ]
    }
]

@router.post("/checkout")
async def process_checkout(payload: CheckoutPayload):
    """
    Processa a finalização de uma compra simulada.
    """
    total_price = 0
    valid_items = []

    try:
        if prisma.is_connected():
            for item in payload.items:
                product = await prisma.product.find_unique(where={"id": item.id})
                if product:
                    total_price += product.price * item.quantity
                    valid_items.append({
                        "productId": product.id,
                        "quantity": item.quantity,
                        "price": product.price
                    })

            order = await prisma.order.create(
                data={
                    "userId": payload.user_id,
                    "cep": payload.cep,
                    "totalPrice": total_price,
                    "items": {
                        "create": valid_items
                    }
                },
                include={
                    "items": True
                }
            )
            return {"message": "Compra simulada com sucesso", "order_id": order.id}
    except Exception as e:
        print(f"Erro no checkout no Prisma: {e}. Usando fallback em memória.")

    # Fallback se banco offline
    new_id = len(DEMO_ORDERS) + 101
    new_order = {
        "id": new_id,
        "userId": payload.user_id or "usr-guest",
        "customerName": f"Cliente #{new_id}",
        "cep": payload.cep,
        "address": f"CEP {payload.cep}",
        "totalPrice": 299.90,
        "createdAt": datetime.now().isoformat(),
        "deadline": (datetime.now() + timedelta(minutes=45)).replace(microsecond=0).isoformat(),
        "items": [{"id": 1, "productId": 1, "quantity": 1, "price": 299.90, "product": {"name": "Produto Selecionado"}}]
    }
    DEMO_ORDERS.insert(0, new_order)
    return {"message": "Compra simulada com sucesso", "order_id": new_id}

@router.get("/orders")
async def list_orders():
    """
    Lista todos os pedidos registrados enriquecidos com prazo limite (deadline).
    """
    try:
        if prisma.is_connected():
            orders = await prisma.order.find_many(
                include={
                    "items": {
                        "include": {
                            "product": True
                        }
                    }
                },
                order={"createdAt": "desc"}
            )
            if orders and len(orders) > 0:
                result = []
                for idx, o in enumerate(orders):
                    o_dict = o.model_dump() if hasattr(o, "model_dump") else dict(o)
                    created = o_dict.get("createdAt")
                    if isinstance(created, str):
                        created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    elif isinstance(created, datetime):
                        created_dt = created
                    else:
                        created_dt = datetime.now()

                    now = datetime.now()
                    # Atribui deadline para o dia de hoje, para simulação consistente do algoritmo
                    if created_dt.date() < now.date():
                        deadline_dt = datetime(now.year, now.month, now.day, created_dt.hour, created_dt.minute, 0)
                        if deadline_dt < now:
                            deadline_dt = now + timedelta(minutes=45 + (idx * 30))
                    else:
                        deadline_dt = created_dt + timedelta(minutes=45 + (idx * 30))

                    o_dict["deadline"] = deadline_dt.replace(microsecond=0).isoformat()
                    o_dict["customerName"] = f"Cliente #{o_dict.get('id')}"
                    result.append(o_dict)
                return result
    except Exception as e:
        print(f"Erro ao listar pedidos do Prisma: {e}. Utilizando dados de demonstração.")

    # Retorna DEMO_ORDERS atualizados com base no horário presente
    now = datetime.now()
    offsets = [35, 20, 65, 50, 90]
    for idx, demo in enumerate(DEMO_ORDERS):
        offset = offsets[idx % len(offsets)]
        demo["deadline"] = (now + timedelta(minutes=offset)).replace(microsecond=0).isoformat()

    return DEMO_ORDERS

@router.get("/orders/{order_id}")
async def get_order(order_id: int):
    """
    Busca um pedido específico pelo ID.
    """
    try:
        if prisma.is_connected():
            order = await prisma.order.find_unique(
                where={"id": order_id},
                include={
                    "items": {
                        "include": {
                            "product": True
                        }
                    }
                }
            )
            if order:
                o_dict = order.model_dump() if hasattr(order, "model_dump") else dict(order)
                o_dict["deadline"] = (datetime.now() + timedelta(minutes=45)).isoformat()
                return o_dict
    except Exception as e:
        print(f"Erro ao buscar pedido {order_id}: {e}")

    for demo in DEMO_ORDERS:
        if demo["id"] == order_id:
            return demo

    raise HTTPException(status_code=404, detail="Pedido não encontrado")
