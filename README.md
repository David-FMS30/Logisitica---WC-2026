# 🏆 Copa do Mundo 2026: Análise de Desgaste Logístico

<p align="center">
  <img src="assets/intro-readme.webp" alt="Imagem inicial do projeto" width="800">
</p>
🔗 **[Acesse o Dashboard Interativo Online Aqui](#)** *https://logistica-wc2026.streamlit.app/*

---

## O porquê desse projeto:

Como um apaixonado por futebol e esportes em geral, sei que o esporte de alto rendimento hoje é decidido nos detalhes: na intensidade de um sprint aos 85 minutos, na recomposição tática rápida e na saúde física dos atletas. 

A Copa do Mundo de 2026 será a maior e mais continental da história, espalhada por EUA, Canadá e México. Com 4 fusos horários diferentes e altitudes que passam de 2.200 metros, a logística deixou de ser apenas um detalhe fora de campo e passou a ser um **adversário invisível**. 

Meu objetivo com este projeto foi provar uma hipótese: **o sorteio dos grupos gerou uma desigualdade logística que impactará a recuperação física de algumas seleções antes mesmo de a bola rolar.**

## 🧠 A Engenharia: Índice de Fadiga Logística (IFL)

Para quantificar esse desgaste, desenvolvi uma métrica própria através de *Feature Engineering*. O **IFL** não apenas soma os quilômetros voados, mas pune o calendário de uma equipe baseando-se em quatro pilares fisiológicos:

1. **Distância Percorrida:** O tempo em trânsito entre as sedes.
2. **Choque de Fuso Horário:** A quebra do ciclo circadiano (Jet Lag).
3. **Janela de Descanso:** Penalização matemática aguda para intervalos de descanso inferiores a 6 dias entre as partidas.
4. **Fator Altitude:** O estresse aeróbico de jogar acima de 500 metros do nível do mar (ex: Cidade do México e Guadalajara).

Os dados brutos são processados e a equação final é normalizada em uma escala amigável de **0 a 10** (onde 10 representa exaustão crítica).

## 🚀 Funcionalidades do Produto de Dados

* **🗺️ Mapa Interativo de Rotas (Folium):** Visualização geográfica das rotas de voo. Linhas animadas que mudam de cor do verde ao vermelho dependendo da criticidade do trecho.
* **📊 Dashboard de KPIs (Streamlit):** Identificação automática da "Zona da Morte" logística, ranqueando as seleções que mais vão sofrer na fase de grupos.
* **🌡️ Heatmap de Fadiga (Seaborn/Plotly):** Matriz temporal que isola os dias críticos do torneio para cada seleção.
* **🔍 Deep-Dive e Evolução:** Análise jogo a jogo de uma seleção específica, permitindo que comissões técnicas (ou fãs) simulem o impacto logístico do seu time do coração.
* **⬇️ Exportação de Dados:** Pipeline limpo que permite baixar as tabelas tratadas em formato `.csv` diretamente pela interface.

## 🔮 Próximos Passos (Trabalhos Futuros)

Este projeto atende primariamente ao calendário mapeado da Fase de Grupos. Como desejo futuro para a evolução desta análise, planejo:
* **Análise Logística Completa do Torneio:** Expandir a arquitetura de dados para cobrir todo o mata-mata (a partir da nova fase de 16 avos de final), criando simulações probabilísticas que mapeiam as rotas mais exaustivas para as seleções que chegarem à grande final.
* **Módulo de Estresse Térmico:** Integrar APIs climáticas para cruzar as temperaturas históricas do verão norte-americano e umidade relativa do ar como peso adicional no algoritmo do IFL.

## 🛠️ Stack Tecnológico

A aplicação foi construída inteiramente em Python, com foco em uma arquitetura de dados limpa e visualização responsiva:
* **Engenharia de Dados:** `pandas`, `numpy`
* **Geolocalização:** `geopy` (Cálculo de distância geodésica entre estádios)
* **Desenvolvimento Web:** `streamlit` (UI/UX e deploy)
* **Visualização de Dados:** `folium`, `streamlit-folium`, `plotly`, `seaborn`, `matplotlib`

## 💻 Como Rodar o Projeto Localmente

Se você deseja explorar o código, clonar o repositório ou executar o dashboard na sua própria máquina, siga os passos abaixo:

### 1. Clone o repositório

```bash
git clone https://github.com/David-FMS30/Logisitica---WC-2026.git
```

### 2. Acesse a pasta do projeto

```bash
cd Logisitica---WC-2026
```

### 3. Instale as dependências

Recomenda-se o uso de um ambiente virtual para evitar conflitos entre bibliotecas.

```bash
pip install -r requirements.txt
```

### 4. Execute a aplicação

```bash
streamlit run app.py
```

Após executar o comando, o Streamlit abrirá o dashboard no navegador. Caso isso não aconteça automaticamente, acesse o endereço exibido no terminal, geralmente:

```text
http://localhost:8501
```

---

## 📁 Estrutura do Repositório

A estrutura principal do projeto está organizada da seguinte forma:

```text
Logisitica---WC-2026/
│
├── app.py
├── requirements.txt
├── README.md
│
└── data/
    └── Bases de dados utilizadas no projeto
```

### Descrição dos Arquivos e Pastas

| Arquivo/Pasta | Descrição |
|---|---|
| `app.py` | Arquivo principal da aplicação Streamlit, responsável por executar o dashboard. |
| `requirements.txt` | Lista de bibliotecas necessárias para instalar e executar o projeto. |
| `README.md` | Documentação principal do projeto. |
| `data/` | Pasta destinada ao armazenamento das bases de dados utilizadas na análise. |
| `assets/` | Pasta contendo imagens do projeto. |

