import datetime # Para datas e horas.
import heapq 

# Importa tudo que precisamos de 'data_structures.py'.
from data_structures import (
    PESOS_VEGETACAO, ACOES_POR_GRAVIDADE, MAPA_GRAFOS, EQUIPES,
    AREA_ATUACAO_3M_DRONES, BASE_3M_DRONES, HIERARQUIA_REGIAO,
    fila_chamadas_chegada, fila_prioridade_chamadas, historico_acoes_equipes,
    areas_afetadas_status, registro_log_sistema, id_chamada_counter, 
    registrar_log, calcular_prioridade, dijkstra, definir_acoes_por_severidade,
    designar_equipe, registrar_acao_na_pilha_equipe, atualizar_status_area,
    visualizar_hierarquia_regiao, 
    menu_consultar_status_area,
    menu_consultar_historico_equipe,
    menu_visualizar_fila_prioridade,
    menu_consultas_mapa,
    menu_busca_binaria_chamada,
    menu_processar_recursos_fifo,
    menu_registrar_eventos_lifo
)

# Isso garante que o ID continue único e sincronizado com o de data_structures.py.
_id_chamada_counter_global = id_chamada_counter 

def menu_adicionar_chamada(): # Adiciona nova chamada de emergência.
    global _id_chamada_counter_global # Acessa o contador global.
    print("\n--- Adicionar Nova Chamada de Emergência ---")
    local = input(f"Local do foco (ex: Zona Norte, entre {list(MAPA_GRAFOS.keys())}): ").strip() # Pede o local.
    if not local: # Valida o local.
        print("Local não pode ser vazio.")
        return
    if local not in MAPA_GRAFOS: # Avisa se local não está no mapa.
        print(f"AVISO: Local '{local}' não está definido no mapa. O atendimento pode falhar.")
    while True: # Pede e valida severidade.
        try:
            severidade = int(input("Severidade do foco (1-10): "))
            if 1 <= severidade <= 10: break
            else: print("Severidade deve ser entre 1 e 10.")
        except ValueError: print("Entrada inválida. Por favor, insira um número para severidade.")
    print("Tipos de vegetação disponíveis:", ", ".join(PESOS_VEGETACAO.keys())) # Tipos de vegetação.
    tipo_vegetacao = input("Tipo de vegetação (ex: cerrado, mata_atlantica): ").strip().lower() # Pede vegetação.
    if tipo_vegetacao not in PESOS_VEGETACAO: # Padrão se não reconhecido.
        print(f"Tipo de vegetação '{tipo_vegetacao}' não reconhecido. Usando peso padrão 'outros'.")
        tipo_vegetacao = "outros"

    clima = input("Condições climáticas no local (ex: seco, úmido, ventoso): ").strip() # Pede o clima.
    if not clima: clima = "não informado"

    _id_chamada_counter_global += 1 # Novo ID.
    nova_chamada = { # Cria a nova chamada.
        "id": _id_chamada_counter_global, "local": local, "severidade": severidade,
        "tipo_vegetacao": tipo_vegetacao, "clima": clima,
        "timestamp_criacao": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    fila_chamadas_chegada.append(nova_chamada) # Adiciona na fila (FIFO).
    prioridade = calcular_prioridade(nova_chamada) # Calcula prioridade.
    heapq.heappush(fila_prioridade_chamadas, (-prioridade, nova_chamada['id'], nova_chamada)) # Adiciona na heap.
    registrar_log(f"Chamada ID {nova_chamada['id']} (Prioridade: {prioridade:.2f}) adicionada às filas.") # Log.
    if nova_chamada['local'] in MAPA_GRAFOS and nova_chamada['local'] in AREA_ATUACAO_3M_DRONES: # Atualiza status da área.
        if nova_chamada['local'] not in areas_afetadas_status or areas_afetadas_status[nova_chamada['local']]['status'] != "ativo":
            atualizar_status_area(nova_chamada['local'], "ativo", nova_chamada['id'])
    print(f"Chamada ID {nova_chamada['id']} registrada com sucesso.")

def menu_atender_proxima_ocorrencia(): # Atende a ocorrência mais urgente.
    print("\n--- Atender Próxima Ocorrência Prioritária ---")
    if not fila_prioridade_chamadas: # Sem chamadas na fila.
        print("Nenhuma chamada na fila de prioridade para atender.")
        return
    neg_prioridade, _, chamada = heapq.heappop(fila_prioridade_chamadas) # Pega da heap.
    prioridade_real = -neg_prioridade # Prioridade real.
    registrar_log(f"Processando chamada ID {chamada['id']} (Prioridade: {prioridade_real:.2f}) do local '{chamada['local']}'.") # Log.
    if chamada["local"] not in MAPA_GRAFOS: # Local não no mapa.
        registrar_log(f"ERRO: Local '{chamada['local']}' da ocorrência ID {chamada['id']} não existe no MAPA_GRAFOS. Não é possível atender.")
        return
    if chamada["local"] not in AREA_ATUACAO_3M_DRONES: # Local fora da área.
        registrar_log(f"Chamada ID {chamada['id']} para o local '{chamada['local']}' está fora da área de atuação da 3M Drones. Ocorrência não será atendida por esta equipe.")
        atualizar_status_area(chamada['local'], "fora_de_area", chamada['id'])
        return
    equipe_designada = designar_equipe(chamada["local"]) # Designa equipe.
    if not equipe_designada: # Sem equipe disponível, volta para fila.
        registrar_log(f"Nenhuma equipe disponível ou adequada para atender a chamada ID {chamada['id']} no local '{chamada['local']}'. Recolocando na fila.")
        heapq.heappush(fila_prioridade_chamadas, (neg_prioridade, chamada['id'], chamada)) 
        return

    EQUIPES[equipe_designada["id"]]["status"] = "em_missao" # Equipe em missão.
    registrar_log(f"Equipe {equipe_designada['nome']} (ID: {equipe_designada['id']}) designada para a chamada ID {chamada['id']}.") # Log.
    rota_calculada, tempo_estimado = dijkstra(MAPA_GRAFOS, equipe_designada["base"], chamada["local"]) # Calcula rota (Grafos).

    if rota_calculada is None: # Rota não calculada.
        registrar_log(f"Não foi possível calcular a rota para a chamada ID {chamada['id']}. Verifique o mapa.")
        EQUIPES[equipe_designada["id"]]["status"] = "disponivel" # Equipe disponível.
        heapq.heappush(fila_prioridade_chamadas, (neg_prioridade, chamada['id'], chamada)) # Volta para fila.
        return
    
    acoes_recomendadas = definir_acoes_por_severidade(chamada["severidade"]) # Ações por severidade.
    for acao in acoes_recomendadas: # Registra ações (Pilhas).
        registrar_acao_na_pilha_equipe(equipe_designada["id"], chamada["id"], acao) 
    atualizar_status_area(chamada["local"], "controle_em_andamento", chamada["id"]) # Atualiza status da área (Lista Ligada).

    print("\n--- Relatório de Atendimento da Ocorrência ---") # Relatório de atendimento.
    print(f"Ocorrência ID: {chamada['id']}")
    print(f"Local do Foco: {chamada['local']}")
    print(f"Prioridade Calculada: {prioridade_real:.2f}")
    print(f"Equipe Designada: {equipe_designada['nome']}")
    print(f"Base da Equipe: {equipe_designada['base']}")
    print(f"Ações Recomendadas: {', '.join(acoes_recomendadas)}")
    print(f"Rota Otimizada: {' -> '.join(rota_calculada)}")
    print(f"Tempo Estimado de Deslocamento: {tempo_estimado} min")
    print(f"Status da Área Atual: {areas_afetadas_status[chamada['local']]['status']}")
    registrar_log(f"Atendimento da chamada ID {chamada['id']} iniciado. Relatório gerado.")

def main(): # Função principal do sistema.
    registrar_log("Sistema de Gerenciamento de Incêndios 3M Drones iniciado.") # Inicia log.
    while True: # Loop do menu principal.
        print("\n--- Sistema de Gerenciamento de Incêndios 3M Drones ---")
        # Opções do menu.
        print("1. Adicionar Nova Chamada de Emergência")
        print("2. Atender Próxima Ocorrência Prioritária")
        print("3. Consultar Status de Área Afetada (Lista Ligada de Eventos)")
        print("4. Consultar Histórico de Ações por Equipe (Pilhas)")
        print("5. Visualizar Fila de Prioridade de Chamadas (Heaps)")
        print("6. Visualizar Hierarquia da Região (Árvores)")
        print("7. Visualizar Log do Sistema")
        print("8. Consultas ao Mapa (Grafos)")
        print("9. Buscar Chamada por ID (Busca Binária)")
        print("10. Gerenciar Recursos (FIFO)")
        print("11. Registrar Eventos Importantes (LIFO)")
        print("0. Sair")

        escolha = input("Escolha uma opção: ").strip() # Pega a escolha.

        # Direciona para a função escolhida.
        if escolha == '1': menu_adicionar_chamada()
        elif escolha == '2': menu_atender_proxima_ocorrencia()
        elif escolha == '3': menu_consultar_status_area() 
        elif escolha == '4': menu_consultar_historico_equipe() 
        elif escolha == '5': menu_visualizar_fila_prioridade() 
        elif escolha == '6': visualizar_hierarquia_regiao()
        elif escolha == '7': 
            print("\n--- Log do Sistema ---")
            if registro_log_sistema: # Mostra o log.
                for entrada in registro_log_sistema: print(entrada)
            else: print("Log do sistema está vazio.")
        elif escolha == '8': menu_consultas_mapa() 
        elif escolha == '9': menu_busca_binaria_chamada() 
        elif escolha == '10': menu_processar_recursos_fifo() 
        elif escolha == '11': menu_registrar_eventos_lifo() 
        elif escolha == '0':
            registrar_log("Sistema de Gerenciamento de Incêndios 3M Drones finalizado.") # Log final.
            print("Saindo do sistema. Até logo!")
            break # Sai do programa.
        else: print("Opção inválida. Tente novamente.")

if __name__ == "__main__": # Inicia o programa aqui.
    main() # Inicia o menu.