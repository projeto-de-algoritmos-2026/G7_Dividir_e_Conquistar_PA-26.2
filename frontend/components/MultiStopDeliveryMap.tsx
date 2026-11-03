'use client';

import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { OSMGraph } from '../utils/osmGraph';

export interface MapStop {
    stopIndex: number; // 0 para Origem, 1, 2, 3... para clientes
    orderId?: number;
    label: string;
    customerName?: string;
    cep?: string;
    address?: string;
    lat: number;
    lon: number;
    arrivalFormatted?: string;
    deadlineFormatted?: string;
    latenessMinutes?: number;
    isDelayed?: boolean;
}

interface MultiStopDeliveryMapProps {
    graph?: OSMGraph | null;
    stops: MapStop[];
    continuousPathNodeIds?: number[];
    continuousCoordinates?: [number, number][];
    visitedEdges?: { u: number; v: number }[];
    activeStopIndex?: number | null;
    onSelectStop?: (stopIndex: number) => void;
    closestPairCoords?: [number, number][];
}

export default function MultiStopDeliveryMap({
    graph,
    stops,
    continuousPathNodeIds,
    continuousCoordinates,
    visitedEdges,
    activeStopIndex,
    onSelectStop,
    closestPairCoords
}: MultiStopDeliveryMapProps) {
    const mapRef = useRef<HTMLDivElement>(null);
    const leafletMap = useRef<L.Map | null>(null);
    const markersRef = useRef<Record<number, L.Marker>>({});
    const polylineRef = useRef<L.Polyline | null>(null);
    const timeouts = useRef<NodeJS.Timeout[]>([]);

    useEffect(() => {
        // Fix Leaflet icons in Next.js
        delete (L.Icon.Default.prototype as any)._getIconUrl;
        L.Icon.Default.mergeOptions({
            iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
            iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
        });

        if (!mapRef.current) return;

        if (!leafletMap.current) {
            leafletMap.current = L.map(mapRef.current, {
                zoomControl: true,
            }).setView([-15.7975, -47.8919], 13);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(leafletMap.current);
        }

        const map = leafletMap.current;

        // Limpa timeouts anteriores
        timeouts.current.forEach(clearTimeout);
        timeouts.current = [];

        // Limpa layers anteriores
        map.eachLayer((layer) => {
            if (layer instanceof L.Polyline || layer instanceof L.Marker || layer instanceof L.CircleMarker) {
                map.removeLayer(layer);
            }
        });
        markersRef.current = {};

        const hasStops = stops && stops.length > 0;
        const hasClosestPair = closestPairCoords && closestPairCoords.length === 2;

        if (!hasStops && !hasClosestPair) return;

        const bounds = L.latLngBounds([]);

        // 1. Se houver o Par Mais Próximo (Entregas Gêmeas), desenha a linha laranja tracejada
        if (hasClosestPair) {
            const twinLine = L.polyline(closestPairCoords, {
                color: '#F59E0B',
                weight: 5,
                dashArray: '10, 10',
                opacity: 1
            }).addTo(map);

            closestPairCoords.forEach((coord, idx) => {
                bounds.extend(coord);
                L.circleMarker(coord, {
                    radius: 10,
                    fillColor: '#F59E0B',
                    color: '#FFFFFF',
                    weight: 3,
                    fillOpacity: 0.95
                })
                .bindPopup(`<strong>⚡ Entrega Gêmea #${idx + 1}</strong><br/>Par mais próximo encontrado!`)
                .addTo(map);
            });

            if (!hasStops) {
                map.fitBounds(twinLine.getBounds(), { padding: [80, 80], maxZoom: 15 });
                return;
            }
        }

        // 2. Cria marcadores numerados personalizados para cada parada
        stops.forEach((stop) => {
            bounds.extend([stop.lat, stop.lon]);

            const isOrigin = stop.stopIndex === 0;
            const isDelayed = stop.isDelayed;

            // Cores e estilos do badge
            const bgClass = isOrigin
                ? 'bg-[#17181A] text-white border-2 border-[#6032F6]'
                : isDelayed
                ? 'bg-rose-600 text-white border-2 border-white'
                : 'bg-[#6032F6] text-white border-2 border-white';

            const badgeText = isOrigin ? 'ORIGEM' : `${stop.stopIndex}`;
            const subLabel = isOrigin ? 'Depósito' : stop.customerName || `Pedido #${stop.orderId}`;

            const customHtml = `
                <div class="group relative flex flex-col items-center cursor-pointer select-none transition-transform hover:scale-110">
                    <div class="px-2.5 py-1 rounded-full shadow-xl font-black text-xs flex items-center justify-center gap-1 ${bgClass} transition-all">
                        ${isOrigin ? '🏭' : '📦'} <span>${badgeText}</span>
                    </div>
                    <div class="w-2 h-2 rotate-45 -mt-1 ${isOrigin ? 'bg-[#17181A]' : isDelayed ? 'bg-rose-600' : 'bg-[#6032F6]'} shadow-sm"></div>
                    <div class="mt-1 px-2 py-0.5 rounded-md bg-[#17181A]/90 text-white font-bold text-[10px] whitespace-nowrap shadow-md hidden sm:block">
                        ${subLabel}
                    </div>
                </div>
            `;

            const icon = L.divIcon({
                className: 'custom-stop-marker',
                html: customHtml,
                iconSize: [80, 50],
                iconAnchor: [40, 25],
                popupAnchor: [0, -25]
            });

            const popupContent = `
                <div style="font-family: sans-serif; padding: 4px; min-width: 180px;">
                    <div style="font-weight: 900; font-size: 13px; text-transform: uppercase; color: #17181A; margin-bottom: 4px;">
                        ${isOrigin ? 'Ponto de Partida (Depósito)' : `Parada #${stop.stopIndex} - ${stop.customerName || `Pedido #${stop.orderId}`}`}
                    </div>
                    <div style="font-size: 11px; color: #666; margin-bottom: 6px;">
                        ${stop.address || stop.cep || ''}
                    </div>
                    ${!isOrigin ? `
                    <div style="background: #F5F2EB; border-radius: 8px; padding: 6px 8px; font-size: 11px; margin-top: 4px;">
                        <div><strong>Chegada Prevista:</strong> ${stop.arrivalFormatted || '--:--'}</div>
                        <div><strong>Prazo (Deadline):</strong> ${stop.deadlineFormatted || '--:--'}</div>
                        <div style="margin-top: 3px; font-weight: bold; color: ${isDelayed ? '#DC2626' : '#16A34A'};">
                            ${isDelayed ? `⚠️ Atraso: ${stop.latenessMinutes} min` : '✅ Dentro do prazo'}
                        </div>
                    </div>
                    ` : `
                    <div style="background: #F5F2EB; border-radius: 8px; padding: 6px 8px; font-size: 11px;">
                        <div><strong>Saída do Lote:</strong> ${stop.arrivalFormatted || '09:00'}</div>
                    </div>
                    `}
                </div>
            `;

            const marker = L.marker([stop.lat, stop.lon], { icon })
                .addTo(map)
                .bindPopup(popupContent);

            marker.on('click', () => {
                if (onSelectStop) onSelectStop(stop.stopIndex);
            });

            markersRef.current[stop.stopIndex] = marker;
        });

        // 3. Extrai coordenadas da Rota Contínua
        let latlngs: [number, number][] = [];

        if (continuousCoordinates && continuousCoordinates.length > 0) {
            latlngs = continuousCoordinates;
        } else if (graph && continuousPathNodeIds && continuousPathNodeIds.length > 0) {
            latlngs = continuousPathNodeIds
                .map((nodeId) => {
                    const node = graph.nodes[nodeId];
                    return node ? ([node.lat, node.lon] as [number, number]) : null;
                })
                .filter((coord): coord is [number, number] => coord !== null);
        } else if (stops.length > 1) {
            latlngs = stops.map(s => [s.lat, s.lon]);
        }

        // Desenha a Rota Contínua ligando a cadeia de entregas
        if (latlngs.length > 0) {
            L.polyline(latlngs, {
                color: '#17181A',
                weight: 8,
                opacity: 0.25,
                lineCap: 'round',
                lineJoin: 'round'
            }).addTo(map);

            const routeLine = L.polyline(latlngs, {
                color: '#6032F6',
                weight: 5,
                opacity: 0.95,
                lineCap: 'round',
                lineJoin: 'round'
            }).addTo(map);

            polylineRef.current = routeLine;

            map.fitBounds(routeLine.getBounds(), { padding: [60, 60] });
        } else if (bounds.isValid()) {
            map.fitBounds(bounds, { padding: [50, 50] });
        }

        // Se houver arestas exploradas (animação de busca do algoritmo de rota)
        if (visitedEdges && visitedEdges.length > 0 && graph) {
            const batch = Math.max(1, Math.ceil(visitedEdges.length / 30));
            for (let i = 0; i < visitedEdges.length; i += batch) {
                const chunk = visitedEdges.slice(i, i + batch);
                const timeout = setTimeout(() => {
                    const lines = chunk
                        .map(e => {
                            const u = graph.nodes[e.u];
                            const v = graph.nodes[e.v];
                            if (u && v) return [[u.lat, u.lon], [v.lat, v.lon]] as [[number, number], [number, number]];
                            return null;
                        })
                        .filter(Boolean) as [[number, number], [number, number]][];

                    if (lines.length > 0) {
                        L.polyline(lines, { color: '#3B82F6', weight: 2, opacity: 0.3 }).addTo(map);
                    }
                }, (i / visitedEdges.length) * 1000);
                timeouts.current.push(timeout);
            }
        }

    }, [stops, graph, continuousPathNodeIds, continuousCoordinates, visitedEdges, closestPairCoords]);

    // Efeito para focar quando o usuário clica em uma parada na timeline
    useEffect(() => {
        if (activeStopIndex !== undefined && activeStopIndex !== null && leafletMap.current) {
            const marker = markersRef.current[activeStopIndex];
            if (marker) {
                leafletMap.current.panTo(marker.getLatLng(), { animate: true, duration: 0.8 });
                marker.openPopup();
            }
        }
    }, [activeStopIndex]);

    return (
        <div className="relative w-full h-full min-h-[420px] rounded-3xl overflow-hidden shadow-inner bg-[#EBE7DD]">
            <div ref={mapRef} className="w-full h-full min-h-[420px] z-0" />
        </div>
    );
}