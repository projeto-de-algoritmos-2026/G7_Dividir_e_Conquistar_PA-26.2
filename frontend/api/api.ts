const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

function getAuthHeaders() {
    const token = typeof window !== 'undefined' ? localStorage.getItem('stockio_token') : null;
    return {
        "Content-Type": "application/json",
        ...(token ? { "Authorization": `Bearer ${token}` } : {})
    };
}

export async function getAllParentCategories() {
    try {
        // Ajuste a rota se necessário de acordo com seu backend FastAPI
        const res = await fetch(`${BASE_URL}/api/categories?parent=true`);
        if (!res.ok) return [];
        return await res.json();
    } catch (e) {
        console.error(e);
        return [];
    }
}

export async function getChildCategories(parentId: number) {
    try {
        const res = await fetch(`${BASE_URL}/api/categories/${parentId}/children`);
        if (!res.ok) return [];
        return await res.json();
    } catch (e) {
        console.error(e);
        return [];
    }
}

export async function getAllProducts() {
    try {
        const res = await fetch(`${BASE_URL}/api/products`);
        if (!res.ok) return [];
        return await res.json();
    } catch (e) {
        console.error(e);
        return [];
    }
}

export async function getProductsById(productId: number | string) {
    try {
        const res = await fetch(`${BASE_URL}/api/products/${productId}`);
        if (!res.ok) return null;
        return await res.json();
    } catch (e) {
        console.error(e);
        return null;
    }
}

export async function getUserById(userId: string | number) {
    try {
        const res = await fetch(`${BASE_URL}/api/users/${userId}`, {
            headers: getAuthHeaders()
        });
        if (!res.ok) return null;
        return await res.json();
    } catch (e) {
        console.error(e);
        return null;
    }
}

export async function processCheckout(payload: { items: any[], cep: string, user_id?: string | null }) {
    try {
        const res = await fetch(`${BASE_URL}/api/checkout`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error("Checkout failed");
        return await res.json();
    } catch (e) {
        console.error(e);
        throw e;
    }
}

export async function getAllOrders() {
    try {
        const res = await fetch(`${BASE_URL}/api/orders`, {
            headers: getAuthHeaders()
        });
        if (!res.ok) return [];
        return await res.json();
    } catch (e) {
        console.error(e);
        return [];
    }
}

export async function getOrderById(orderId: string | number) {
    try {
        const res = await fetch(`${BASE_URL}/api/orders/${orderId}`, {
            headers: getAuthHeaders()
        });
        if (!res.ok) return null;
        return await res.json();
    } catch (e) {
        console.error(e);
        return null;
    }
}

export async function calculateRouteAPI(graph: any, startNode: number, endNode: number, algorithm: string) {
    try {
        const payload = {
            graph,
            startNode,
            endNode,
            algorithm
        };
        const res = await fetch(`${BASE_URL}/api/routes/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        if (!res.ok) return null;
        return await res.json();
    } catch (e) {
        console.error(e);
        return null;
    }
}

export async function calculateMinimizeLatenessAPI(payload: {
    orders: any[];
    startTime?: string;
    segmentDurationsMinutes?: number[];
    serviceTimeMinutes?: number;
}) {
    try {
        const res = await fetch(`${BASE_URL}/api/schedule/minimize-lateness`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error("Falha ao calcular Minimize Lateness");
        return await res.json();
    } catch (e) {
        console.error("Erro na API de Minimize Lateness:", e);
        return null;
    }
}

export interface ManualRouteEvaluation {
    idealOrderIds: number[];
    manualOrderIds: number[];
    inversions: number;
    maxInversions: number;
    efficiencyScore: number;
    riskLevel: "perfect" | "low" | "moderate" | "high";
}

export async function evaluateManualRouteAPI(payload: {
    orders: { id: number; deadline?: string }[];
    manualOrderIds: number[];
    startTime: string;
    segmentDurationsMinutes: number[];
    serviceTimeMinutes: number;
}) {
    const res = await fetch(`${BASE_URL}/api/schedule/count-inversions`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
    });
    if (!res.ok) {
        throw new Error("Não foi possível avaliar a fila manual. Tente novamente.");
    }
    return await res.json();
}

export async function compareSchedulingStrategiesAPI(payload: {
    orders: any[];
    startTime?: string;
    durationsMap?: Record<number, number>;
    serviceTimeMinutes?: number;
}) {
    try {
        const res = await fetch(`${BASE_URL}/api/schedule/compare`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error("Falha ao comparar estratégias");
        return await res.json();
    } catch (e) {
        console.error("Erro na API de comparação:", e);
        return null;
    }
}

export async function calculateChainRouteAPI(payload: {
    graph: any;
    stopNodeIds: number[];
    algorithm?: string;
    speedKmh?: number;
}) {
    try {
        const res = await fetch(`${BASE_URL}/api/routes/chain-calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                graph: payload.graph,
                stopNodeIds: payload.stopNodeIds,
                algorithm: payload.algorithm || "dijkstra",
                speedKmh: payload.speedKmh || 30.0
            })
        });
        if (!res.ok) return null;
        return await res.json();
    } catch (e) {
        console.error("Erro na API de Rota em Cadeia:", e);
        return null;
    }
}

export interface SelectingBreakpointsResult {
    possible: boolean;
    message?: string | null;
    breakpoints: number[];
    numberOfStops: number;
    totalDistanceMeters: number;
    capacityMeters: number;
}

export async function calculateBreakpointsAPI(payload: {
    graph: any;
    path: number[];
    capacityMeters: number;
    transport: string;
}): Promise<SelectingBreakpointsResult | null> {
    try {
        const res = await fetch(`${BASE_URL}/api/routes/select-breakpoints`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!res.ok) return null;

        return await res.json();
    } catch (e) {
        console.error("Erro na API de Selecting Breakpoints:", e);
        return null;
    }
}

