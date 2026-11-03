from fastapi import APIRouter, HTTPException
from app.database import db as prisma

router = APIRouter(
    prefix="/api/products",
    tags=["Produtos"]
)

DEMO_PRODUCTS = [
    {
        "id": 1,
        "name": "Tênis Esportivo Nike Zoom",
        "price": 499.90,
        "stock": 25,
        "rating": 4.8,
        "created_at": "2026-01-01T00:00:00",
        "product_images": [
            {
                "id": 1,
                "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80",
                "order": 0
            }
        ]
    },
    {
        "id": 2,
        "name": "Headphone Sony WH-1000XM4",
        "price": 1899.00,
        "stock": 10,
        "rating": 4.9,
        "created_at": "2026-01-01T00:00:00",
        "product_images": [
            {
                "id": 2,
                "image_url": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=800&q=80",
                "order": 0
            }
        ]
    },
    {
        "id": 3,
        "name": "Câmera Canon EOS Rebel T7",
        "price": 2899.99,
        "stock": 5,
        "rating": 4.7,
        "created_at": "2026-01-01T00:00:00",
        "product_images": [
            {
                "id": 3,
                "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&q=80",
                "order": 0
            }
        ]
    },
    {
        "id": 4,
        "name": "Relógio Smartwatch Apple Series 8",
        "price": 3299.00,
        "stock": 15,
        "rating": 4.9,
        "created_at": "2026-01-01T00:00:00",
        "product_images": [
            {
                "id": 4,
                "image_url": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=800&q=80",
                "order": 0
            }
        ]
    },
    {
        "id": 5,
        "name": "Teclado Mecânico Keychron K2",
        "price": 650.00,
        "stock": 30,
        "rating": 4.6,
        "created_at": "2026-01-01T00:00:00",
        "product_images": [
            {
                "id": 5,
                "image_url": "https://images.unsplash.com/photo-1595225476474-87563907a212?w=800&q=80",
                "order": 0
            }
        ]
    },
    {
        "id": 6,
        "name": "Mochila Dell Pro Slim 15",
        "price": 249.90,
        "stock": 50,
        "rating": 4.5,
        "created_at": "2026-01-01T00:00:00",
        "product_images": [
            {
                "id": 6,
                "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&q=80",
                "order": 0
            }
        ]
    },
    {
        "id": 7,
        "name": "Cadeira Gamer ThunderX3",
        "price": 1250.00,
        "stock": 8,
        "rating": 4.4,
        "created_at": "2026-01-01T00:00:00",
        "product_images": [
            {
                "id": 7,
                "image_url": "https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?w=800&q=80",
                "order": 0
            }
        ]
    }
]

@router.get("")
@router.get("/")
async def get_all_products():
    """
    Retorna todos os produtos cadastrados com suas respectivas imagens.
    """
    try:
        if prisma.is_connected():
            products = await prisma.product.find_many(
                include={
                    "images": {
                        "order_by": {
                            "order": "asc"
                        }
                    }
                }
            )
            
            result = []
            for p in products:
                result.append({
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "stock": p.stock,
                    "rating": p.rating,
                    "created_at": p.createdAt.isoformat() if p.createdAt else None,
                    "product_images": [
                        {
                            "id": img.id,
                            "image_url": img.imageUrl,
                            "order": img.order
                        }
                        for img in p.images
                    ] if p.images else []
                })
            return result
    except Exception as e:
        print(f"Erro ao buscar produtos no Prisma: {e}. Usando dados de demonstração.")
    
    return DEMO_PRODUCTS

@router.get("/{product_id}")
async def get_product_by_id(product_id: int):
    """
    Retorna um produto específico pelo ID.
    """
    try:
        if prisma.is_connected():
            p = await prisma.product.find_unique(
                where={
                    "id": product_id
                },
                include={
                    "images": {
                        "order_by": {
                            "order": "asc"
                        }
                    }
                }
            )
            
            if p:
                return {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "stock": p.stock,
                    "rating": p.rating,
                    "created_at": p.createdAt.isoformat() if p.createdAt else None,
                    "product_images": [
                        {
                            "id": img.id,
                            "image_url": img.imageUrl,
                            "order": img.order
                        }
                        for img in p.images
                    ] if p.images else []
                }
    except Exception as e:
        print(f"Erro ao buscar produto {product_id} no Prisma: {e}. Usando dados de demonstração.")
        
    for p in DEMO_PRODUCTS:
        if p["id"] == product_id:
            return p

    raise HTTPException(status_code=404, detail="Produto não encontrado")
