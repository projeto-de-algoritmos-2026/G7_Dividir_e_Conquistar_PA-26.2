# Delivery Routing & Scheduling com Dividir e Conquistar - Stock.io

Número da Lista: 3<br>
Conteúdo da Disciplina: Dividir e Conquistar (D&C)<br>

## Alunos

| Foto | Nome | Matrícula |
| :---: | :--- | ---: |
| ![Johnnatan Salles](https://github.com/jsalless.png?size=100) | **Johnnatan Salles** | 241011330 |
| ![Julia Gabriella](https://github.com/juliagabriellafs.png?size=100) | **Julia Gabriella** | 241036142 |

## Sobre

Este projeto foi desenvolvido para a disciplina de **Projeto de Algoritmos (PA) - 2026.2**, com foco na aplicação prática do paradigma de **Dividir e Conquistar (Divide and Conquer)** em um cenário real de logística, planejamento e roteamento de entregas.

A aplicação estende o ecossistema da plataforma **stock.io**, integrando dois dos algoritmos mais consagrados de Dividir e Conquistar para resolver problemas reais de despacho:

1. **Counting Inversions (Contagem de Inversões):** Adaptado como **Avaliador de Fila Manual / Reordenamento de Entregas**. O algoritmo avalia alterações manuais feitas pelo operador na fila de pedidos em relação à ordenação ideal de prazos (*Earliest Deadline First - EDF*), calculando instantaneamente o número de inversões, o score de eficiência e a classificação de risco de atraso em tempo ótimo $O(n \log n)$.
2. **Closest Pair of Points (Par de Pontos Mais Próximos):** Adaptado como **Localizador de Entregas Gêmeas**. O algoritmo processa as coordenadas geográficas (latitude e longitude) de todos os pedidos selecionados e encontra em $O(n \log n)$ o par de clientes fisicamente mais próximos entre si, viabilizando o agrupamento de pedidos vizinhos para otimizar tempo e combustível.

Como suporte e continuidade do ecossistema:
- **Scheduling to Minimize Lateness (EDF):** Define a sequência ótima de referência com base nos prazos limites;
- **Selecting Breakpoints (Algoritmo do Caminhoneiro):** Identifica paradas necessárias para recarga conforme a autonomia do veículo;
- **Dijkstra** e **Bellman-Ford:** Motores de caminho mínimo para traçado contínuo da malha viária e cálculo de distâncias.

---

## Screenshots

![Tela Inicial](assets/1-telaInicial.png)

*Figura 1: Tela inicial da plataforma Stock.io.*

![Mapa da Cadeia de Entregas](assets/1.1-mapa_minimize.PNG)

*Figura 2: Calendário de entregas com lote de pedidos e traçado contínuo da cadeia de entregas.*

![Timeline de Entregas](assets/1.2-mapa_minimize.PNG)

*Figura 3: Timeline detalhada da fila de entregas, exibindo deslocamento, horário previsto de chegada e deadline de cada pedido.*

![Rota Perfeita - 0 inversões](assets/8-count_inversions_rota_perfeita.png)

*Figura 4: Fila Manual com Rota Perfeita — 0 / 3 inversões, Score de Eficiência de 100% (sequência idêntica à ordem ótima EDF).*

![Baixo Risco - 1 inversão](assets/9-count_inversions_baixo_risco.png)

*Figura 5: Fila Manual com Baixo Risco de Atraso — 1 / 3 inversões, Score de Eficiência de 66.7% após reordenação manual pelo operador.*

![Alto Risco - 3 inversões](assets/10-count_inversions_alto_risco.png)

*Figura 6: Fila Manual com Alto Risco de Atraso — 3 / 3 inversões, Score de Eficiência de 0% (ordem totalmente invertida em relação aos deadlines).*

![Mapa Algoritmo do Caminhoneiro](assets/2-mapa_caminhoneiro.PNG)

*Figura 7: Rota individual com os pontos de recarga selecionados pelo algoritmo Selecting Breakpoints.*

![Implementação Minimize Lateness](assets/3-minimize.PNG)

*Figura 8: Implementação da regra gulosa Earliest Deadline First utilizada como referência para a ordenação ideal.*

![Cálculo Minimize Lateness](assets/4-minimize.PNG)

*Figura 9: Cálculo do cronograma, horários de chegada e atrasos dos pedidos.*

![Implementação Selecting Breakpoints](assets/5-caminhoneiro.PNG)

*Figura 10: Estrutura inicial da implementação do Selecting Breakpoints e validação da autonomia do veículo.*

![Execução Selecting Breakpoints](assets/6-caminhoneiro.PNG)

*Figura 11: Percurso da rota e verificação dos trechos realizada pelo Algoritmo do Caminhoneiro.*

![Servidores em execução](assets/7-terminal.PNG)

*Figura 12: Frontend e backend em execução.*

---

## Tecnologias Utilizadas

O projeto está dividido em duas partes principais:

### Frontend

- **Framework:** Next.js com React
- **Linguagem:** TypeScript
- **Estilização:** TailwindCSS
- **Mapas:** Leaflet / React-Leaflet
- **Geocodificação:** ViaCEP + OpenStreetMap/Nominatim
- **Malha viária:** OpenStreetMap / Overpass API

### Backend

- **Framework:** FastAPI
- **Linguagem:** Python 3.11+
- **ORM:** Prisma
- **Banco de Dados:** PostgreSQL / Supabase
- **Algoritmos Implementados:**
  - **Dividir e Conquistar:**
    - `Counting Inversions` (baseado em Merge Sort recursivo)
    - `Closest Pair of Points` (busca em 2D com faixa $2\delta$ e Haversine)
  - **Algoritmos Gulosos:** Scheduling to Minimize Lateness (EDF) e Selecting Breakpoints
  - **Grafos / Menor Caminho:** Dijkstra e Bellman-Ford

---

## Funcionalidades e Algoritmos de Dividir e Conquistar

### 1. Counting Inversions (Avaliador de Rota Manual)

No contexto do **Calendário de Entregas & Agenda de Lotes**, o operador logístico pode reordenar manualmente os pedidos da fila (por conveniência de trânsito, preferência do motorista ou agrupamento de bairros). Contudo, cada inversão em relação à ordem ideal EDF (*Earliest Deadline First*) pode aumentar o risco de pedidos estourarem o prazo.

Para avaliar o impacto dessa reorganização sem impor uma trava rígida, foi implementado o algoritmo de **Contagem de Inversões por Dividir e Conquistar** em [`backend/app/algoritmos/count_inversions.py`](backend/app/algoritmos/count_inversions.py).

#### Fundamentação Teórica

Dada uma permutação $A = [a_1, a_2, \dots, a_n]$, um par de índices $(i, j)$ constitui uma **inversão** se:

$$
i < j \quad \text{e} \quad a_i > a_j
$$

Uma abordagem ingênua por força bruta compara todos os pares em tempo $O(n^2)$. Aplicando a estratégia de **Dividir e Conquistar** baseada no **Merge Sort**, resolvemos o problema em tempo ótimo $O(n \log n)$:

1. **Dividir:** A lista de posições relativas é particionada em duas metades: $\text{esquerda} = A[0 \dots \lfloor n/2 \rfloor - 1]$ e $\text{direita} = A[\lfloor n/2 \rfloor \dots n - 1]$;
2. **Conquistar:** Recursivamente conta o número de inversões contidas inteiramente na metade esquerda e na metade direita;
3. **Combinar (Merge):** Durante o processo de intercalação ordenada entre as metades esquerda e direita, sempre que um elemento da metade direita for menor que o elemento da metade esquerda, identifica-se que **todos os elementos restantes da metade esquerda** são estritamente maiores que ele. Portanto, acumula-se:

$$
\text{inversões} \mathrel{+}= \text{meio} - \text{esquerda}
$$

#### Recorrência e Complexidade

A relação de recorrência do algoritmo é expressa por:

$$
T(n) = 2T(n/2) + O(n)
$$

Pelo Caso 2 do **Teorema Mestre**:

$$
T(n) = \Theta(n \log n)
$$

- **Complexidade de Tempo:** $O(n \log n)$
- **Complexidade de Espaço:** $O(n)$ (buffers de ordenação auxiliar)

#### Regra de Negócio e Heurística de Risco

1. Os pedidos do lote são mapeados para suas posições de referência na fila ideal EDF $\{order\_id \mapsto position\}$;
2. A fila manual é traduzida na lista dessas posições e submetida a `count_inversions(values)`;
3. O número máximo possível de inversões para um lote de $n$ pedidos é dado por:

$$
\text{Máximo de Inversões} = \binom{n}{2} = \frac{n(n - 1)}{2}
$$

4. O **Score de Eficiência** é calculado por:

$$
\text{Score} = 100 \times \left(1 - \frac{\text{inversões}}{\text{máximo}}\right)
$$

5. Classificação do Nível de Risco:
   - **Rota Perfeita:** $0$ inversões (Score = $100\%$);
   - **Baixo Risco:** $\text{inversões} \leq \frac{1}{3} \times \text{máximo}$;
   - **Risco Moderado:** $\frac{1}{3} \times \text{máximo} < \text{inversões} \leq \frac{2}{3} \times \text{máximo}$;
   - **Alto Risco:** $\text{inversões} > \frac{2}{3} \times \text{máximo}$.

6. O botão **Restaurar Fila Ideal** na interface restaura instantaneamente a ordem EDF ótima.

---

### 2. Closest Pair of Points (Localizador de Entregas Gêmeas)

O segundo algoritmo de Dividir e Conquistar implementado foi o **Closest Pair of Points (Par de Pontos Mais Próximos)** em [`backend/app/algoritmos/closest_pair.py`](backend/app/algoritmos/closest_pair.py).

#### Aplicação Prática

Em operações de entrega expressa, identificar clientes geograficamente contíguos permite despachar ambos com o mesmo veículo ou realizar entregas em sequência imediata (*drop-offs geminados*), reduzindo substancialmente a quilometragem rodada e a emissão de poluentes.

A funcionalidade **Entregas Gêmeas** analisa a latitude e longitude dos pedidos selecionados e identifica o par de entregas com menor distância física entre si.

#### Fundamentação Teórica

Dado um conjunto $P = \{p_1, p_2, \dots, p_n\}$ de pontos no plano $2D$, queremos encontrar o par $(p_i, p_j)$ que minimiza a distância $d(p_i, p_j)$. A abordagem por força bruta exige verificar $\binom{n}{2}$ pares em tempo $O(n^2)$.

Com **Dividir e Conquistar**, a busca é realizada em tempo $O(n \log n)$:

1. **Pré-processamento / Ordenação:** Ordena-se os pontos inicialmente pela coordenada $X$ (longitude);
2. **Dividir:** Traça-se uma linha divisória vertical $L$ na mediana das coordenadas $X$, dividindo o conjunto de pontos em duas metades: $Q$ (esquerda) e $R$ (direita);
3. **Conquistar:** Calcula-se recursivamente o par mais próximo em $Q$ ($\delta_1$) e em $R$ ($\delta_2$). Define-se a menor distância preliminar como:

$$
\delta = \min(\delta_1, \delta_2)
$$

4. **Combinar:** Um par mais próximo pode ter um ponto na metade esquerda e outro na metade direita. Esse par só pode existir dentro de uma **faixa vertical central de largura $2\delta$** centrada na linha $L$, isto é:

$$
\text{faixa} = \{p \in P \mid |p.x - L.x| < \delta\}
$$

   - Os pontos das duas metades já chegam ordenados por $Y$ graças à intercalação (*merge*) em $O(n)$;
   - Para cada ponto na faixa ordenado por $Y$, **basta inspecionar no máximo os próximos 7 a 8 pontos subsequentes** na lista vertical. Essa propriedade geométrica é garantida pelo fato de que nenhum ponto da mesma metade pode estar a menos de $\delta$ de distância (princípio da casa dos pombos em caixas $\delta/2 \times \delta/2$);
   - Se for encontrada alguma distância $d(p_i, p_j) < \delta$, o par ótimo global é atualizado.

#### Medição de Distância (Euclidiana vs. Haversine)

- Durante a execução geométrica de Dividir e Conquistar no plano $2D$, é utilizada a **distância Euclidiana** sobre as coordenadas projetadas para a poda em $O(n \log n)$;
- Ao determinar o par ótimo final, o sistema calcula a distância real sobre a curvatura terrestre utilizando a **Fórmula de Haversine** (em metros e quilômetros):

$$
a = \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)
$$

$$
d = 2 R \cdot \operatorname{atan2}\left(\sqrt{a}, \sqrt{1 - a}\right)
$$

#### Logs no Terminal (Rastreamento Didático)

O backend imprime detalhadamente no terminal cada etapa da recursão, evidenciando o funcionamento do algoritmo:

```text
------ CLOSEST PAIR OF POINTS (DIVIDIR E CONQUISTAR) ------
Total de pontos analisados: 5
Ordenacao inicial por X (Longitude): #103 (-47.8921) -> #104 (-47.8895) -> #105 (-47.8820) ...
-----------------------------------------------------------
[DIVISAO - RAIZ] n=5 [#103, #104, #105, #106, #107] | Linha L (X = -47.88575)
  [CASO BASE - ESQ] Pontos: ['#103', '#104'] | Par: (#103, #104) | delta = 0.002600
  [CASO BASE - DIR] Pontos: ['#105', '#106', '#107'] | Par: (#105, #106) | delta = 0.001950
[COMBINACAO - RAIZ] Faixa (2*delta): ['#104', '#105'] | Menor par: (#104, #105) (delta = 0.001820) [Atualizado na faixa]
-----------------------------------------------------------
Par mais proximo encontrado: Pedido #104 e Pedido #105
Distancia Real (Haversine):  214.35 m (0.214 km)
Comparacoes realizadas:      7
-----------------------------------------------------------
```

---

## Comparativo Teórico de Estratégias

| Algoritmo | Paradigma | Complexidade de Tempo | Complexidade de Espaço | Aplicação no Stock.io |
| :--- | :--- | :--- | :--- | :--- |
| **Count Inversions** | **Dividir e Conquistar** | **$O(n \log n)$** | **$O(n)$** | **Avalia desvio da fila manual frente à ordem EDF ideal e calcula risco de atraso** |
| **Closest Pair of Points** | **Dividir e Conquistar** | **$O(n \log n)$** | **$O(n)$** | **Encontra par de entregas fisicamente mais próximas para despacho conjunto** |
| **Minimize Lateness** | Algoritmo Ambicioso (Greed) | $O(n \log n)$ | $O(n)$ | Ordena a fila de referência minimizando o atraso máximo ($L_{\max}$) |
| **Selecting Breakpoints** | Algoritmo Ambicioso (Greed) | $O(n)$ | $O(1)$ | Determina pontos de recarga em rota individual com veículo elétrico |
| **Dijkstra** | Algoritmo Ambicioso / Grafos | $O((V + E) \log V)$ | $O(V)$ | Traçado viário de menor caminho entre pontos consecutivos |
| **Bellman-Ford** | Programação Dinâmica / Grafos | $O(V \cdot E)$ | $O(V)$ | Menor caminho viário com suporte a custos diferenciados |

---

## Instalação e Execução

### 1. Clonando o repositório

```bash
git clone https://github.com/projeto-de-algoritmos-2026/G7_Dividir_e_Conquistar_PA-26.2.git
cd G7_Dividir_e_Conquistar_PA-26.2
```

### 2. Configurando o Backend (FastAPI)

Navegue até a pasta `backend`:

```bash
cd backend
```

#### Crie e ative o ambiente virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Instale as dependências e gere o cliente do Prisma

```bash
pip install -r requirements.txt
prisma generate
```

#### Inicie o servidor do Backend

```bash
uvicorn app.main:app --reload --port 8000
```

- API Base: [http://localhost:8000](http://localhost:8000)
- Swagger Interativo: [http://localhost:8000/docs](http://localhost:8000/docs)

#### Executando a Suíte de Testes Automatizados

Para validar o algoritmo **Count Inversions** e os endpoints:

```bash
python -m unittest discover -s tests -v
```

---

### 3. Configurando o Frontend (Next.js)

Abra outro terminal e navegue até a pasta `frontend`:

```bash
cd frontend
npm install
npm run dev
```

A aplicação estará disponível em [http://localhost:3000](http://localhost:3000).

---

## Uso do Sistema

### Credenciais de Teste

- **Entregador:** `mauricioentregador@gmail.com` | **Senha:** `mauricio123@`
- **Cliente:** `mauricio@gmail.com` | **Senha:** `mauricio123@`

---

### Como Testar os Algoritmos no Sistema Web

1. Faça login na plataforma como **entregador**.
2. Acesse a tela **Calendário de Entregas & Agenda de Lotes** (`/delivery/batchOrder`).
3. Selecione os pedidos para compor o lote e clique em **Otimizar Agenda** para gerar o traçado contínuo e a fila ideal inicial via Minimize Lateness (EDF).

#### Testando o Count Inversions (Fila Manual)
- Observe o card **Fila Manual**: inicialmente o score é de **100%** (**0 / N inversões**, badge **Rota Perfeita**).
- Clique nas setas $\uparrow$ e $\downarrow$ ao lado de qualquer pedido para alterar sua ordem.
- O sistema dispara imediatamente o endpoint `/api/schedule/count-inversions`, recalculando em tempo real:
  - O número de inversões ($k / \text{máximo}$);
  - O Score de Eficiência percentual;
  - A classificação de risco (**Baixo Risco**, **Risco Moderado** ou **Alto Risco**);
  - A rota contínua no mapa Leaflet e a quilometragem total.
- Clique em **Restaurar Fila Ideal** para restabelecer a ordem ótima.

#### Testando o Closest Pair (Entregas Gêmeas)
- No painel de pedidos, clique em **Buscar Entregas Gêmeas**.
- O sistema envia as coordenadas dos pedidos para o endpoint `/api/routes/closest-pair`.
- O algoritmo de Dividir e Conquistar identifica o par mais próximo em $O(n \log n)$, traça uma linha destacada de conexão direta entre eles no mapa e exibe uma notificação toast informando a distância exata em metros.
- No terminal do backend, acompanhe os logs com cada divisão, caso base e análise da faixa vertical $2\delta$.

---

## Vídeo de Apresentação

O vídeo demonstrativo com as explicações teóricas dos algoritmos de Dividir e Conquistar e o funcionamento prático na plataforma pode ser assistido no YouTube:

[![Vídeo da apresentação](https://img.youtube.com/vi/fEQrlEzLmXg/0.jpg)](https://youtu.be/fEQrlEzLmXg)

🔗 **Link direto:** [https://youtu.be/fEQrlEzLmXg](https://youtu.be/fEQrlEzLmXg)
