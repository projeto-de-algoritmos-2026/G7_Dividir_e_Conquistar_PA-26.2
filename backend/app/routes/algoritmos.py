from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from app.algoritmos.bellman_ford import run_bellman_ford
from app.algoritmos.dijkstra import run_dijkstra
from app.algoritmos.minimize_lateness import run_minimize_lateness, compare_scheduling_strategies
from app.algoritmos.chain_route import calculate_chain_route
from app.algoritmos.selecting_breakpoints import run_selecting_breakpoints
from app.algoritmos.count_inversions import evaluate_manual_route
from app.algoritmos.minimize_lateness import calculate_schedule_lateness, parse_iso_datetime
from math import isfinite

router = APIRouter(
    prefix="/api",
    tags=["Algoritmos"]
)

class GraphNode(BaseModel):
    lat: float
    lon: float

class GraphEdge(BaseModel):
    target: int
    distance: float

class Graph(BaseModel):
    nodes: Dict[int, GraphNode]
    edges: Dict[int, List[GraphEdge]]

class CalculateRouteRequest(BaseModel):
    graph_data: Graph = Field(alias="graph")
    start_node: int = Field(alias="startNode")
    end_node: int = Field(alias="endNode")
    algorithm: str

class VisitedEdge(BaseModel):
    u: int
    v: int

class RouteResultResponse(BaseModel):
    distances: Dict[int, float]
    predecessors: Dict[int, Optional[int]]
    path: List[int]
    totalDistance: float
    visitedEdges: List[VisitedEdge]

@router.post("/routes/calculate", response_model=RouteResultResponse)
async def calculate_route(payload: CalculateRouteRequest):
    """
    Calcula a menor rota ponto a ponto usando o algoritmo escolhido (Dijkstra ou Bellman-Ford).
    """
    if payload.algorithm not in ["bellman", "dijkstra"]:
        raise HTTPException(status_code=400, detail="Algoritmo inválido. Escolha 'bellman' ou 'dijkstra'.")

    graph_nodes = {node_id: node.model_dump() for node_id, node in payload.graph_data.nodes.items()}
    graph_edges = {node_id: [edge.model_dump() for edge in edges] for node_id, edges in payload.graph_data.edges.items()}

    if payload.algorithm == "dijkstra":
        result = run_dijkstra(graph_nodes, graph_edges, payload.start_node, payload.end_node)
    else:
        result = run_bellman_ford(graph_nodes, graph_edges, payload.start_node, payload.end_node)

    if result is None:
        raise HTTPException(status_code=404, detail="Não foi possível traçar uma rota conexa entre os pontos ou grafo contém ciclo negativo.")

    return RouteResultResponse(
        distances=result.distances,
        predecessors=result.predecessors,
        path=result.path,
        totalDistance=result.totalDistance,
        visitedEdges=[VisitedEdge(u=edge['u'], v=edge['v']) for edge in result.visitedEdges]
    )


# ----------------------------------------------------
# MINIMIZE LATENESS (MÓDULO GREED)
# ----------------------------------------------------

class OrderScheduleInput(BaseModel):
    id: int
    cep: Optional[str] = None
    customerName: Optional[str] = None
    address: Optional[str] = None
    deadline: Optional[str] = None
    createdAt: Optional[str] = None
    totalPrice: Optional[float] = None
    items: Optional[List[Any]] = None

class MinimizeLatenessRequest(BaseModel):
    orders: List[Dict[str, Any]]
    startTime: Optional[str] = None
    segmentDurationsMinutes: Optional[List[float]] = None
    serviceTimeMinutes: Optional[float] = 5.0

@router.post("/schedule/minimize-lateness")
async def schedule_minimize_lateness(payload: MinimizeLatenessRequest):
    """
    Executa o algoritmo ambicioso (Greedy) de Minimize Lateness:
    Ordena a fila de entregas pelo prazo limite (deadline) mais próximo (Earliest Deadline First - EDF),
    garantindo que o atraso máximo do lote seja o menor possível.
    Calcula os horários de partida, chegada e o atraso individual de cada parada.
    """
    try:
        result = run_minimize_lateness(
            orders=payload.orders,
            start_time_iso=payload.startTime,
            segment_durations_minutes=payload.segmentDurationsMinutes,
            service_time_minutes=payload.serviceTimeMinutes or 5.0
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar Minimize Lateness: {str(e)}")


class ManualRouteRequest(BaseModel):
    orders: List[OrderScheduleInput]
    manualOrderIds: List[int]
    startTime: str
    segmentDurationsMinutes: List[float]
    serviceTimeMinutes: float = Field(default=5.0, ge=0, allow_inf_nan=False)


@router.post("/schedule/count-inversions")
async def evaluate_manual_schedule(payload: ManualRouteRequest):
    orders = [order.model_dump(exclude_none=True) for order in payload.orders]
    try:
        evaluation = evaluate_manual_route(orders, payload.manualOrderIds)
        if (len(payload.segmentDurationsMinutes) != len(orders)
                or any(not isfinite(duration) or duration < 0 for duration in payload.segmentDurationsMinutes)):
            raise ValueError("Informe uma duracao de viagem valida para cada pedido.")
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    orders_by_id = {order["id"]: order for order in orders}
    schedule = calculate_schedule_lateness(
        ordered_orders=[orders_by_id[order_id] for order_id in payload.manualOrderIds],
        start_time=parse_iso_datetime(payload.startTime),
        segment_durations_minutes=payload.segmentDurationsMinutes,
        service_time_minutes=payload.serviceTimeMinutes,
    )
    return {**evaluation, "scheduleResult": schedule}


class CompareStrategiesRequest(BaseModel):
    orders: List[Dict[str, Any]]
    startTime: Optional[str] = None
    durationsMap: Optional[Dict[int, float]] = None
    serviceTimeMinutes: Optional[float] = 5.0

@router.post("/schedule/compare")
async def compare_strategies(payload: CompareStrategiesRequest):
    """
    Compara o algoritmo guloso (Earliest Deadline First) com outras estratégias (FIFO e SPT),
    demonstrando a optimalidade da abordagem ambiciosa para o trabalho de Projeto de Algoritmos.
    """
    try:
        result = compare_scheduling_strategies(
            orders=payload.orders,
            start_time_iso=payload.startTime,
            durations_map=payload.durationsMap,
            service_time_minutes=payload.serviceTimeMinutes or 5.0
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao comparar estratégias: {str(e)}")


# ----------------------------------------------------
# ROTA EM CADEIA (CHAIN ROUTING PARA LOTE DE ENTREGAS)
# ----------------------------------------------------

class ChainRouteRequest(BaseModel):
    graph_data: Graph = Field(alias="graph")
    stop_node_ids: List[int] = Field(alias="stopNodeIds")
    algorithm: Optional[str] = "dijkstra"
    speedKmh: Optional[float] = 30.0

@router.post("/routes/chain-calculate")
async def calculate_multi_stop_chain_route(payload: ChainRouteRequest):
    """
    Traça a rota em cadeia ligando os pontos na ordem exata da fila gerada pelo Minimize Lateness:
    Origem -> Cliente 1 -> Cliente 2 -> ... -> Cliente N.
    Executa Dijkstra ou Bellman-Ford para cada trecho consecutivo e retorna a rota contínua global.
    """
    if payload.algorithm not in ["bellman", "dijkstra"]:
        raise HTTPException(status_code=400, detail="Algoritmo inválido. Escolha 'bellman' ou 'dijkstra'.")

    graph_nodes = {node_id: node.model_dump() for node_id, node in payload.graph_data.nodes.items()}
    graph_edges = {node_id: [edge.model_dump() for edge in edges] for node_id, edges in payload.graph_data.edges.items()}

    try:
        result = calculate_chain_route(
            graph_nodes=graph_nodes,
            graph_edges=graph_edges,
            stop_node_ids=payload.stop_node_ids,
            algorithm=payload.algorithm,
            speed_kmh=payload.speedKmh or 30.0
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao traçar rota em cadeia: {str(e)}")


# ----------------------------------------------------
# SELEÇÃO DE PONTOS DE PARADA (BREAKPOINTS)
# ----------------------------------------------------

class SelectingBreakpointsRequest(BaseModel):
    graph_data: Graph = Field(alias="graph")
    path: List[int]
    capacity_meters: float = Field(alias="capacityMeters")
    transport: Optional[str] = None

class SelectingBreakpointsResponse(BaseModel):
    possible: bool
    message: Optional[str] = None
    breakpoints: List[int] = Field(default_factory=list)
    numberOfStops: int = 0
    totalDistanceMeters: float = 0.0
    capacityMeters: float


@router.post(
    "/routes/select-breakpoints",
    response_model=SelectingBreakpointsResponse
)
async def select_route_breakpoints(payload: SelectingBreakpointsRequest):
    graph_edges = {
        node_id: [edge.model_dump() for edge in edges]
        for node_id, edges in payload.graph_data.edges.items()
    }

    result = run_selecting_breakpoints(
        graph_edges=graph_edges,
        path=payload.path,
        capacity_meters=payload.capacity_meters
    )

    print("\n------ SELECTING BREAKPOINTS ------")
    print(f"Veículo selecionado: {payload.transport}")
    print(f"Autonomia: {payload.capacity_meters / 1000:.2f} km")
    print(
        f"Distância da rota: "
        f"{result.get('totalDistanceMeters', 0) / 1000:.2f} km"
    )
    print(f"Paradas necessárias: {result.get('numberOfStops', 0)}")
    print(f"Breakpoints selecionados: {result.get('breakpoints', [])}")
    print("-------------------------------------\n")

    return result
