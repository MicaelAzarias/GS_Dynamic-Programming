# GS_Dynamic-Programming
# 3M Drones - Sistema Inteligente de Combate a Incêndios Florestais

Somos a 3M Drones, e temos como foco a prevenção e o tratamento de incêndios florestais, utilizando tecnologias de monitoramento, priorização e resposta emergencial para agir com rapidez e precisão em áreas críticas.

Este projeto simula um sistema de gerenciamento inteligente voltado ao combate de incêndios florestais, integrando conceitos de estruturas de dados como grafos, pilhas, filas, árvores e heaps para tomar decisões estratégicas em tempo real.

## 🎯 Objetivo

Desenvolver um sistema que:
- Registra ocorrências de incêndio com severidade, tipo de vegetação e clima.
- Calcula prioridades com base em riscos ambientais.
- Designa equipes e define rotas otimizadas até o local.
- Gera e consulta o histórico de ações e status de áreas afetadas.
- Gerencia recursos com estrutura FIFO e eventos com LIFO.
- Permite consultas ao mapa e busca eficiente de chamadas.

## 🧠 Funcionalidades

- **Chamadas de Emergência:** Registro com severidade, tipo de vegetação e condições climáticas.
- **Fila de Prioridade (Heap):** Atendimento baseado em risco calculado.
- **Designação de Equipes:** Algoritmo com base em especialidade e tempo de deslocamento (Dijkstra).
- **Ações Automatizadas:** Ações recomendadas conforme o nível de gravidade.
- **Histórico e Log:** Registro com pilhas e lista ligada por equipe e área.
- **Consultas em Grafo:** Verifica rotas, locais mais próximos e todos os caminhos possíveis.
- **Hierarquia Regional (Árvore):** Visualização da estrutura organizacional por regiões.
- **Gestão de Recursos (FIFO):** Despacho de suprimentos.
- **Eventos Importantes (LIFO):** Registro e reversão de eventos operacionais.
- **Busca Binária de Ocorrências:** Localização rápida por ID.

## 🗺️ Mapa de Áreas

O sistema usa um grafo orientado e ponderado, representando os pontos estratégicos da região. A imagem abaixo ilustra o mapa com os custos de deslocamento entre os pontos:

![Mapa dos Grafos](imagem_grafo/Imagem%20Grafos.png)

## 🛠️ Tecnologias e Conceitos Usados

- **Python 3**
- **Algoritmo de Dijkstra**
- **Estruturas de dados:** Fila (`deque`), Fila de Prioridade (`heapq`), Pilha (lista), Lista ligada (histórico), Árvore (hierarquia), Grafo (mapa)
- **Orientação a objetos (modularização com `data_structures.py`)**

## 📂 Organização dos Arquivos

- `main.py`: Interface principal e lógica de fluxo do sistema.
- `data_structures.py`: Estruturas de dados, funções auxiliares e dados simulados.
- `Imagem Grafos.png`: Representação gráfica da rede de locais e conexões.

## 🚀 Como Executar

1. Certifique-se de ter Python instalado (>= 3.7).
2. Execute o script principal:
    ```bash
    python main.py
