import collections
import heapq
import datetime

# Pesos usados para calcular a prioridade conforme o tipo de vegetação
PESOS_VEGETACAO = {
    "cerrado": 1.2,
    "mata_atlantica": 1.5,
    "pantanal": 2.0,
    "floresta_amazonica": 1.8,
    "caatinga": 1.0,
    "pampa": 1.1,
    "outros": 1.0
}

# Ações recomendadas para cada nível de gravidade (1 a 10)
ACOES_POR_GRAVIDADE = {
    1: ["Monitorar foco", "Notificar brigada local de prontidão leve"],
    2: ["Enviar drone de reconhecimento adicional", "Preparar equipe para possível envio"],
    3: ["Deslocar equipe pequena", "Criar aceiro preventivo se área de risco"],
    4: ["Aplicar barreira de contenção química (água/retardante)", "Criar aceiro extenso"],
    5: ["Deslocar múltiplas equipes", "Solicitar apoio aéreo (se disponível e necessário)"],
    6: ["Evacuação de áreas próximas (se houver risco)", "Combate direto intensivo"],
    7: ["Combate direto com todos os recursos disponíveis", "Solicitar reforços de outras regiões/estados"],
    8: ["Estabelecer posto de comando avançado", "Logística de guerra contra o fogo"],
    9: ["Priorizar defesa de vidas e infraestrutura crítica", "Considerar táticas de fogo contra fogo (controlado)"],
    10: ["Ações de rescaldo e prevenção de reignição por longo período", "Avaliação de danos em larga escala"],
}

# Áreas em que a 3M Drones atua
AREA_ATUACAO_3M_DRONES = [
    "Zona Norte", "Mata Alta", "Vila Verde", "Parque Estadual", "Represa",
    "Aeroporto Regional", "Fazenda Boa Esperanca", "Comunidade Ribeirinha",
    "Serra do Mirante", "Vale Escondido", "Posto Rota101", "Escola Pinheiral",
    "Centro Pesquisas", "Vila Pescadores", "Subestacao Eletrica", "Antena MorroAlto",
    "Refugio Ecologico"
]

# Ponto base da 3M Drones
BASE_3M_DRONES = "Base Central"

# Mapa representando os locais e conexões com custos (grafo ponderado)
MAPA_GRAFOS = {
    "Base Central": {
        "Zona Norte": 10, "Vila Verde": 5, "Represa": 8, "Mata Alta": 12,
        "Aeroporto Regional": 20, "Subestacao Eletrica": 12
    },
    "Zona Norte": {
        "Base Central": 10, "Mata Alta": 7, "Area Industrial": 15,
        "Aeroporto Regional": 8, "Posto Rota101": 10
    },
    "Vila Verde": {
        "Base Central": 5, "Mata Alta": 3, "Zona Residencial Sul": 6,
        "Escola Pinheiral": 7, "Vila Pescadores": 18
    },
    "Mata Alta": {
        "Zona Norte": 7, "Vila Verde": 3, "Parque Estadual": 4, "Base Central": 12,
        "Serra do Mirante": 9, "Vale Escondido": 14
    },
    "Represa": {
        "Base Central": 8, "Parque Estadual": 11,
        "Comunidade Ribeirinha": 6, "Fazenda Boa Esperanca": 16
    },
    "Area Industrial": {
        "Zona Norte": 15,
        "Subestacao Eletrica": 5
    },
    "Zona Residencial Sul": {
        "Vila Verde": 6,
        "Escola Pinheiral": 4
    },
    "Parque Estadual": {
        "Mata Alta": 4, "Represa": 11,
        "Serra do Mirante": 5, "Refugio Ecologico": 10
    },
    "Aeroporto Regional": {
        "Base Central": 20, "Zona Norte": 8,
        "Posto Rota101": 12, "Centro Logistico": 18
    },
    "Fazenda Boa Esperanca": {
        "Represa": 16, "Comunidade Ribeirinha": 7,
        "Vale Escondido": 22, "Armazem Central": 25
    },
    "Comunidade Ribeirinha": {
        "Represa": 6, "Fazenda Boa Esperanca": 7,
        "Vila Pescadores": 15
    },
    "Serra do Mirante": {
        "Mata Alta": 9, "Parque Estadual": 5,
        "Antena MorroAlto": 3, "Observatorio": 6
    },
    "Vale Escondido": {
        "Mata Alta": 14, "Fazenda Boa Esperanca": 22,
        "Refugio Ecologico": 18, "Caverna Perdida": 10
    },
    "Posto Rota101": {
        
        "Zona Norte": 10, "Aeroporto Regional": 12,
        "Centro Pesquisas": 9, "Oficina Mecanica": 7
    },
    "Escola Pinheiral": {
        "Vila Verde": 7, "Zona Residencial Sul": 4,
        "Praca Central Vila": 5
    },
    "Centro Pesquisas": {
        "Posto Rota101": 9, "Subestacao Eletrica": 11,
        "Antena MorroAlto": 13, "Universidade Local": 15
    },
    "Vila Pescadores": {
        "Vila Verde": 18, "Comunidade Ribeirinha": 15,
        "Estaleiro": 8
    },
    "Subestacao Eletrica": {
        "Base Central": 12, "Area Industrial": 5,
        "Centro Pesquisas": 11, "Torre de Energia": 4
    },
    "Antena MorroAlto": {
        "Serra do Mirante": 3, "Centro Pesquisas": 13,
        "Estacao Meteorologica": 5
    },
    "Refugio Ecologico": {
        "Parque Estadual": 10, "Vale Escondido": 18,
        "Trilha das Cachoeiras": 7
    },
    "Centro Logistico": {"Aeroporto Regional": 18},
    "Armazem Central": {"Fazenda Boa Esperanca": 25},
    "Observatorio": {"Serra do Mirante": 6},
    "Caverna Perdida": {"Vale Escondido": 10},
    "Oficina Mecanica": {"Posto Rota101": 7},
    "Praca Central Vila": {"Escola Pinheiral": 5},
    "Universidade Local": {"Centro Pesquisas": 15},
    "Estaleiro": {"Vila Pescadores": 8},
    "Torre de Energia": {"Subestacao Eletrica": 4},
    "Estacao Meteorologica": {"Antena MorroAlto": 5},
    "Trilha das Cachoeiras": {"Refugio Ecologico": 7}
}

# Informações das equipes disponíveis
EQUIPES = {
    "equipe_alpha": {"id": "equipe_alpha", "nome": "Alpha Drones", "base": "Base Central", "status": "disponivel", "especialidade_area": ["Zona Norte", "Mata Alta", "Aeroporto Regional"]},
    "equipe_bravo": {"id": "equipe_bravo", "nome": "Bravo Resgate", "base": "Vila Verde", "status": "disponivel", "especialidade_area": ["Vila Verde", "Parque Estadual", "Represa", "Escola Pinheiral"]},
    "equipe_charlie": {"id": "equipe_charlie", "nome": "Charlie Vigilância", "base": "Base Central", "status": "disponivel", "especialidade_area": []},
    "equipe_delta": {"id": "equipe_delta", "nome": "Delta Rápida", "base": "Posto Rota101", "status": "disponivel", "especialidade_area": ["Posto Rota101", "Centro Pesquisas", "Area Industrial"]}
}

# Hierarquia de regiões representada como árvore
HIERARQUIA_REGIAO = {
    "Estado Exemplo": {
        "Municipio Capital": {
            "Zona Norte": {}, "Vila Verde": {}, "Area Industrial": {}, "Aeroporto Regional": {}
        },
        "Municipio Interior": {
            "Mata Alta": {}, "Parque Estadual": {}, "Represa": {}, "Fazenda Boa Esperanca": {}, "Serra do Mirante": {}
        },
        "Municipio Litoraneo": {
            "Vila Pescadores": {}, "Comunidade Ribeirinha": {}
        }
    }
}

# Filas e estruturas de controle de chamadas e histórico
fila_chamadas_chegada = collections.deque()     # Fila FIFO    
fila_prioridade_chamadas = []                   # Heap de prioridade
historico_acoes_equipes = {}                    # Pilhas por equipe
areas_afetadas_status = {}                      # Lista ligada por área
registro_log_sistema = []                       # Log geral do sistema
id_chamada_counter = 0                          # Contador incremental de ID

# Função para registrar uma entrada no log
def registrar_log(mensagem):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entrada_log = f"[{timestamp}] {mensagem}"
    registro_log_sistema.append(entrada_log)
    print(entrada_log)

# Calcula prioridade com base na severidade e tipo de vegetação
def calcular_prioridade(chamada):
    severidade = chamada["severidade"]
    tipo_vegetacao = chamada["tipo_vegetacao"].lower()
    peso_veg = PESOS_VEGETACAO.get(tipo_vegetacao, 1.0)
    prioridade = severidade * peso_veg
    return prioridade

# Algoritmo de Dijkstra para encontrar o caminho mais curto
# Retorna o caminho e a distância total
def dijkstra(grafo, origem, destino):
    if origem not in grafo or destino not in grafo:
        return None, float('inf')

    distancias = {vertice: float('inf') for vertice in grafo}
    antecessores = {vertice: None for vertice in grafo}
    distancias[origem] = 0

    pq = [(0, origem)] 

    while pq:
        dist_atual, u = heapq.heappop(pq)

        if dist_atual > distancias[u]:
            continue

        if u == destino:
            break

        for vizinho, peso in grafo.get(u, {}).items():
            if vizinho not in distancias: continue

            nova_distancia = distancias[u] + peso
            if nova_distancia < distancias[vizinho]:
                distancias[vizinho] = nova_distancia
                antecessores[vizinho] = u
                heapq.heappush(pq, (nova_distancia, vizinho))

    caminho = []
    atual = destino
    if distancias[atual] == float('inf'): 
        return None, float('inf')

    while atual is not None:
        caminho.append(atual)
        atual = antecessores[atual]
    caminho.reverse()

    return caminho, distancias[destino]

# Retorna ações recomendadas para determinada severidade
def definir_acoes_por_severidade(severidade):
    severidade = max(1, min(10, severidade))
    while severidade > 0:
        if severidade in ACOES_POR_GRAVIDADE:
            return ACOES_POR_GRAVIDADE[severidade]
        severidade -= 1
    return ["Nenhuma ação específica definida para esta severidade."]

# Escolhe a melhor equipe disponível para determinado local
def designar_equipe(local_foco):
    equipes_disponiveis = [eq_id for eq_id, eq_data in EQUIPES.items() if eq_data["status"] == "disponivel"]

    if not equipes_disponiveis:
        return None

    melhor_equipe = None
    menor_tempo_deslocamento = float('inf')

    for eq_id in equipes_disponiveis:
        equipe = EQUIPES[eq_id]
        if local_foco not in MAPA_GRAFOS: continue

        if local_foco in equipe["especialidade_area"]:
            _, tempo = dijkstra(MAPA_GRAFOS, equipe["base"], local_foco)
            if tempo < menor_tempo_deslocamento:
                menor_tempo_deslocamento = tempo
                melhor_equipe = eq_id

    if not melhor_equipe:
        for eq_id in equipes_disponiveis:
            equipe = EQUIPES[eq_id]
            if local_foco not in MAPA_GRAFOS: continue

            if not equipe["especialidade_area"] or local_foco not in equipe["especialidade_area"]:
                _, tempo = dijkstra(MAPA_GRAFOS, equipe["base"], local_foco)
                if tempo < menor_tempo_deslocamento:
                    menor_tempo_deslocamento = tempo
                    melhor_equipe = eq_id

    if melhor_equipe:
        return EQUIPES[melhor_equipe]
    return None

# Empilha uma nova ação no histórico da equipe
def registrar_acao_na_pilha_equipe(equipe_id, ocorrencia_id, acao_realizada):
    if equipe_id not in historico_acoes_equipes:
        historico_acoes_equipes[equipe_id] = [] 

    registro_acao = {
        "ocorrencia_id": ocorrencia_id,
        "acao": acao_realizada,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    historico_acoes_equipes[equipe_id].append(registro_acao) 
    registrar_log(f"Ação '{acao_realizada}' registrada para equipe {equipe_id} referente à ocorrência {ocorrencia_id}.")

# Atualiza o status de uma área afetada e registra o evento
def atualizar_status_area(local_nome, novo_status, ocorrencia_id_relacionada):
    if local_nome not in areas_afetadas_status:
        areas_afetadas_status[local_nome] = {
            "status": "monitoramento",
            "ocorrencias_ids": [],
            "historico_status": [] 
        }

    area = areas_afetadas_status[local_nome]
    area["status"] = novo_status
    if ocorrencia_id_relacionada not in area["ocorrencias_ids"]:
        area["ocorrencias_ids"].append(ocorrencia_id_relacionada)

    area["historico_status"].append({
        "status": novo_status,
        "ocorrencia_id": ocorrencia_id_relacionada,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    registrar_log(f"Status da área '{local_nome}' atualizado para '{novo_status}' devido à ocorrência {ocorrencia_id_relacionada}.")

# Impressão recursiva de uma árvore (usada para hierarquia)
def _imprimir_hierarquia(item_hierarquia, nivel=0):
    prefixo = "  " * nivel

    if isinstance(item_hierarquia, dict):
        for chave, valor in item_hierarquia.items():
            print(f"{prefixo}- {chave}:")
            _imprimir_hierarquia(valor, nivel + 1)

    elif isinstance(item_hierarquia, list):
        for i, sub_item in enumerate(item_hierarquia):
            _imprimir_hierarquia(sub_item, nivel + 0)

    elif isinstance(item_hierarquia, str):
         print(f"{prefixo}- {item_hierarquia}")

def visualizar_hierarquia_regiao():
    print("\n--- Hierarquia da Região (Representação de Árvore) ---")
    _imprimir_hierarquia(HIERARQUIA_REGIAO)

# Consultas específicas de área afetada com histórico (lista ligada)
def menu_consultar_status_area():
    print("\n--- Consultar Status de Área Afetada ---")
    local_consulta = input("Digite o nome do local para consulta (ex: Zona Norte): ").strip()

    if local_consulta in areas_afetadas_status:
        area_info = areas_afetadas_status[local_consulta]
        print(f"\nInformações da Área: {local_consulta}")
        print(f"  Status Atual: {area_info['status']}")
        print(f"  Ocorrências Registradas (IDs): {area_info['ocorrencias_ids']}")
        print(f"  Histórico de Status (Lista Ligada de Eventos):")
        if area_info['historico_status']:
            for hist_entry in area_info['historico_status']:
                print(f"    - Status: {hist_entry['status']}, Ocorrência ID: {hist_entry['ocorrencia_id']}, Data: {hist_entry['timestamp']}")
        else:
            print("    Nenhum histórico de status registrado para esta área.")
    else:
        print(f"Nenhuma informação encontrada para a área '{local_consulta}'.")

# Consulta do histórico de ações de uma equipe (pilha)
def menu_consultar_historico_equipe():
    print("\n--- Consultar Histórico de Ações por Equipe (Pilhas) ---")
    print("Equipes disponíveis:", ", ".join(EQUIPES.keys()))
    equipe_id_consulta = input("Digite o ID da equipe para consulta (ex: equipe_alpha): ").strip()

    if equipe_id_consulta in historico_acoes_equipes and historico_acoes_equipes[equipe_id_consulta]:
        print(f"\nHistórico de Ações da Equipe: {EQUIPES[equipe_id_consulta]['nome']} (ID: {equipe_id_consulta})")
        for i, acao_log in enumerate(reversed(historico_acoes_equipes[equipe_id_consulta])):
            print(f"  {len(historico_acoes_equipes[equipe_id_consulta]) - i}. Ocorrência ID: {acao_log['ocorrencia_id']}, Ação: '{acao_log['acao']}', Data: {acao_log['timestamp']}")
    elif equipe_id_consulta in EQUIPES:
        print(f"Nenhum histórico de ações registrado para a equipe '{EQUIPES[equipe_id_consulta]['nome']}'.")
    else:
        print(f"Equipe com ID '{equipe_id_consulta}' não encontrada.")

# Mostra a fila de prioridade atual (heap)
def menu_visualizar_fila_prioridade():
    print("\n--- Visualizar Fila de Prioridade de Chamadas (Heaps) ---")
    if not fila_prioridade_chamadas:
        print("A fila de prioridade está vazia.")
        return

    print("Chamadas na fila (da maior para a menor prioridade):")
    copia_fila_prioridade = heapq.nsmallest(len(fila_prioridade_chamadas), fila_prioridade_chamadas)

    for neg_prioridade, _, chamada_obj in copia_fila_prioridade:
        prioridade_real = -neg_prioridade
        print(f"  ID: {chamada_obj['id']}, Local: {chamada_obj['local']}, "
              f"Severidade: {chamada_obj['severidade']}, Vegetação: {chamada_obj['tipo_vegetacao']}, "
              f"Prioridade: {prioridade_real:.2f}")
    if fila_prioridade_chamadas:
        print(f"\nPróxima a ser atendida (topo da heap): ID {fila_prioridade_chamadas[0][2]['id']}, Prioridade: {-fila_prioridade_chamadas[0][0]:.2f}")

# Menu com consultas ao grafo de locais e rotas (Dijkstra)
def menu_consultas_mapa():
    """Menu para realizar consultas específicas no grafo MAPA_GRAFOS."""
    print("\n--- Consultas ao Mapa (Grafo) ---")
    print("Mapa Atual (Conexões da Base Central como exemplo):\n")
    if BASE_3M_DRONES in MAPA_GRAFOS:
        for destino, custo in MAPA_GRAFOS[BASE_3M_DRONES].items():
            print(f"  Base Central -> {destino}: {custo}")
    else:
        print(f"  Base 3M Drones ('{BASE_3M_DRONES}') não encontrada no mapa.")

    while True:
        print("\nOpções de Consulta ao Mapa:")
        print("1. Menor distância entre dois pontos")
        print("2. Local mais perto da Base 3M Drones (dentro da área de atuação)")
        print("3. Todos os locais por ordem de proximidade da Base 3M Drones")
        print("4. Visualizar o mapa completo")
        print("0. Voltar ao menu principal")

        sub_escolha = input("Escolha uma opção: ").strip()

        if sub_escolha == '1':
            origem = input("Digite o local de origem: ").strip()
            destino = input("Digite o local de destino: ").strip()
            if origem in MAPA_GRAFOS and destino in MAPA_GRAFOS:
                caminho, custo = dijkstra(MAPA_GRAFOS, origem, destino)
                if caminho:
                    print(f"  Menor caminho de '{origem}' para '{destino}': {' -> '.join(caminho)} (Custo: {custo})")
                else:
                    print(f"  Não foi possível encontrar caminho de '{origem}' para '{destino}'.")
            else:
                print(f"  Erro: Local de origem ('{origem}') ou destino ('{destino}') não existem no mapa.")

        elif sub_escolha == '2':
            print(f"\n  Procurando local mais perto da '{BASE_3M_DRONES}' (dentro da área de atuação):")
            if BASE_3M_DRONES not in MAPA_GRAFOS:
                print(f"  Erro: Base '{BASE_3M_DRONES}' não definida no mapa.")
            else:
                mais_perto = None
                menor_dist = float('inf')
                for local in AREA_ATUACAO_3M_DRONES:
                    if local == BASE_3M_DRONES: continue
                    if local not in MAPA_GRAFOS: continue

                    _, dist = dijkstra(MAPA_GRAFOS, BASE_3M_DRONES, local)
                    if dist < menor_dist:
                        menor_dist = dist
                        mais_perto = local

                if mais_perto:
                    print(f"  O local mais perto da '{BASE_3M_DRONES}' na área de atuação é '{mais_perto}' (Distância: {menor_dist}).")
                else:
                    print(f"  Não foi possível determinar o local mais perto ou não há outros locais na área de atuação.")

        elif sub_escolha == '3':
            print(f"\n  Todos os locais por ordem de proximidade da '{BASE_3M_DRONES}':")
            if BASE_3M_DRONES not in MAPA_GRAFOS:
                print(f"  Erro: Base '{BASE_3M_DRONES}' não definida no mapa.")
            else:
                distancias_da_base = []
                for local in MAPA_GRAFOS.keys():
                    if local == BASE_3M_DRONES: continue
                    caminho, dist = dijkstra(MAPA_GRAFOS, BASE_3M_DRONES, local)

                    if caminho:
                        distancias_da_base.append((local, dist, caminho))


                distancias_da_base.sort(key=lambda x: x[1])

                if distancias_da_base:
                    for local, dist, rota in distancias_da_base:
                        print(f"  - {local}: Distância {dist} (Rota: {' -> '.join(rota)})")
                else:
                    print(f"  Não foi possível calcular distâncias a partir da '{BASE_3M_DRONES}'.")

        elif sub_escolha == '4':
            print("\n--- Mapa Completo (Conexões) ---")
            for origem, destinos in MAPA_GRAFOS.items():
                print(f"De '{origem}':")
                if destinos:
                    for destino, custo in destinos.items():
                        print(f"  -> '{destino}' (Custo: {custo})")
                else:
                    print("  (Nenhuma conexão de saída listada)")

        elif sub_escolha == '0':
            break
        else:
            print("Opção de consulta inválida.")

# Busca binária para encontrar uma chamada pelo ID (fila ordenada)
def menu_busca_binaria_chamada():
    print("\n--- Buscar Chamada por ID (Busca Binária) ---")
    if not fila_chamadas_chegada:
        print("Nenhuma chamada registrada para busca.")
        return

    lista_ids = sorted([chamada['id'] for chamada in fila_chamadas_chegada])
    print(f"IDs de chamadas disponíveis: {lista_ids}")

    try:
        alvo_id = int(input("Digite o ID da chamada que deseja buscar: ").strip())
    except ValueError:
        print("Entrada inválida. Por favor, digite um número inteiro.")
        return

    inicio = 0
    termino = len(lista_ids) - 1
    encontrado = False

    while inicio <= termino:
        meio = (inicio + termino) // 2
        id_atual = lista_ids[meio]
        print(f"Começo: {inicio}, Fim: {termino}, Meio: {meio}, ID Verificado: {id_atual}")

        if id_atual == alvo_id:
            print(f"\nAlvo {alvo_id} encontrado no índice: {meio} da lista de IDs ordenada.")
            chamada_encontrada = next((c for c in fila_chamadas_chegada if c['id'] == alvo_id), None)
            if chamada_encontrada:
                print(f"Detalhes da Chamada ID {alvo_id}: {chamada_encontrada}")
            encontrado = True
            break
        elif id_atual < alvo_id:
            inicio = meio + 1
        else:
            termino = meio - 1

    if not encontrado:
        print(f"Chamada com ID {alvo_id} não encontrada.")

# Simula gerenciamento de recursos com FIFO
def menu_processar_recursos_fifo():
    print("\n--- Gerenciar Recursos (FIFO) ---")
    recursos_disponiveis = collections.deque(["drone_extra", "equipe_suporte", "caminhao_agua", "kit_primeiros_socorros"])

    print(f"Recursos iniciais na fila: {list(recursos_disponiveis)}")

    while True:
        print("\nOpções de Recurso (FIFO):")
        print("1. Adicionar recurso")
        print("2. Despachar próximo recurso")
        print("0. Voltar ao menu principal")

        escolha_recurso = input("Escolha uma opção: ").strip()

        if escolha_recurso == '1':
            novo_recurso = input("Digite o nome do recurso a adicionar: ").strip()
            if novo_recurso:
                recursos_disponiveis.append(novo_recurso)
                print(f"Recurso '{novo_recurso}' adicionado à fila. Fila atual: {list(recursos_disponiveis)}")
            else:
                print("Nome do recurso não pode ser vazio.")
        elif escolha_recurso == '2':
            if recursos_disponiveis:
                recurso_despachado = recursos_disponiveis.popleft() 
                print(f"Recurso '{recurso_despachado}' despachado. Fila atual: {list(recursos_disponiveis)}")
            else:
                print("Fila de recursos vazia.")
        elif escolha_recurso == '0':
            break
        else:
            print("Opção inválida.")

# Registra eventos importantes com pilha LIFO
def menu_registrar_eventos_lifo():
    print("\n--- Registro de Eventos Importantes (LIFO - Pilha) ---")
    eventos_recentes = []

    print("Eventos registrados na pilha (último no topo):")
    if not eventos_recentes:
        print("Nenhum evento registrado.")
    else:
        for i, evento in enumerate(reversed(eventos_recentes)):
            print(f"  {len(eventos_recentes) - i}. {evento}")

    while True:
        print("\nOpções de Evento (LIFO):")
        print("1. Adicionar novo evento")
        print("2. Reverter último evento (desfazer/revisar)")
        print("0. Voltar ao menu principal")

        escolha_evento = input("Escolha uma opção: ").strip()

        if escolha_evento == '1':
            novo_evento = input("Descreva o novo evento: ").strip()
            if novo_evento:
                eventos_recentes.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {novo_evento}") 
                print(f"Evento adicionado. Pilha atual: {eventos_recentes[-1] if eventos_recentes else 'Vazia'}")
            else:
                print("Descrição do evento não pode ser vazia.")
        elif escolha_evento == '2':
            if eventos_recentes:
                evento_revertido = eventos_recentes.pop() 
                print(f"Último evento revertido: '{evento_revertido}'. Pilha atual: {eventos_recentes[-1] if eventos_recentes else 'Vazia'}")
            else:
                print("Pilha de eventos vazia. Nada para reverter.")
        elif escolha_evento == '0':
            break
        else:
            print("Opção inválida. Tente novamente.")