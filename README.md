# Trabalho 2 – Detector de Deadlock com Grafo de Alocação

**Disciplina:** Sistemas Operacionais – Engenharia de Computação
**Base:** Aula 07 – Impasses (Prof. Dr. Iago Medeiros)
**Linguagem:** Python 3

**Equipe:** Arthur Vale, Rhayan Alves, Tiago de Oliveira, Matheus Braz e Wandrio Neto.

---

## 1. Objetivo

Implementar um detector de deadlock para sistemas com **um recurso de cada tipo**, usando **busca em profundidade (DFS)** sobre o grafo de alocação de recursos, e validá-lo com os exemplos vistos em aula.

O programa lê um grafo dirigido com processos e recursos e responde:

- `Há deadlock: <ciclo encontrado>`, ou
- `Sem deadlock`.

## 2. Conceitos usados

No grafo de alocação de recursos (Holt, 1972) existem dois tipos de nós: **processos** (círculos) e **recursos** (quadrados).

| Aresta | Significado |
|---|---|
| `recurso -> processo` | o processo **possui** o recurso |
| `processo -> recurso` | o processo está **solicitando** o recurso |

Com um recurso de cada tipo, **um ciclo no grafo é condição suficiente para deadlock**.

## 3. Algoritmo (Aula 07, slides 41 a 48)

Para cada nó `N` do grafo, tomado como nó de partida:

1. Inicializa a lista `L` vazia e deixa todos os arcos desmarcados.
2. Adiciona o nó atual ao final de `L`. Se ele aparece duas vezes em `L`, há um ciclo (o trecho repetido de `L`) e o algoritmo termina.
3. Se o nó atual tem arco de saída desmarcado, marca o arco, segue por ele e volta ao passo 2.
4. Se não tem, e o nó atual é o inicial, não há ciclo a partir dele. Passa-se para o próximo nó de partida.
5. Caso contrário, é um beco sem saída: remove o nó de `L` e retrocede ao nó anterior.

Se nenhum nó de partida encontrar ciclo, o sistema **não está em deadlock**.

**Escolhas de implementação**

- Os arcos de saída são seguidos na **ordem em que aparecem no arquivo** e os nós de partida na ordem de declaração (processos, depois recursos). Isso torna a execução determinística. A aula escolhe os arcos aleatoriamente, mas o resultado (existência do ciclo) é o mesmo.
- O ciclo é impresso começando pelo **menor nome de nó**, para que a saída seja estável e igual aos exemplos da aula.

## 4. Formato de entrada (Opção 1 – lista de arestas)

Uma aresta por linha: `origem destino`. Os tipos dos nós são declarados antes.

```text
PROCESSOS A B C D E F G
RECURSOS R S T U V W
ARESTAS
R A
A S
...
```

- `PROCESSOS` e `RECURSOS` listam os nós de cada tipo, separados por espaço.
- Depois de `ARESTAS`, cada linha é uma aresta.
- Linhas em branco e comentários (iniciados por `#`) são ignorados.

**Validações feitas na leitura** (o programa mostra `Erro: ...` e encerra):

- nó usado em uma aresta mas não declarado;
- nome repetido entre processos e recursos;
- aresta ligando dois processos ou dois recursos (deve ligar um processo a um recurso);
- linha fora do formato.

## 5. Como compilar e executar

Não há etapa de compilação. É necessário apenas o **Python 3.8 ou superior**.

```bash
# Analisar um arquivo de entrada
python deadlock.py caminho/do/grafo.txt

# Mostrar também a lista L percorrida pelo algoritmo
python deadlock.py -v caminho/do/grafo.txt

# Rodar os casos de teste (T1 a T5)
python deadlock.py --testes

# Gerar a pasta testes/ com entradas e saídas esperadas
python deadlock.py --gerar-testes
```

Em alguns sistemas o comando é `python3` em vez de `python`.

Sem argumentos, o programa exibe as instruções de uso.

## 6. Casos de teste

Os cinco testes estão embutidos no código e também disponíveis como arquivos na pasta [`testes/`](testes/), no formato `Tn_entrada.txt` (entrada) e `Tn_esperado.txt` (saída esperada). T1 a T3 são os testes obrigatórios do enunciado. T4 e T5 são testes adicionais, com dois grafos maiores desenhados pela equipe, um com deadlock e outro sem.

| Teste | Entrada | Resultado esperado |
|---|---|---|
| **T1** | Grafo da aula (slide 40) | Deadlock, ciclo D, T, E, V, G, U |
| **T2** | Grafo 1 da aula (A, B e C requisitando R, S, T em ordens que não travam) | Sem deadlock |
| **T3** | Grafo 2 da aula (A requisita S, B requisita T, C requisita R, cada um já com um recurso) | Deadlock, ciclo entre A, B, C e R, S, T |
| **T4** | Grafo 1 com deadlock (processos B, D, E, Z, F e recursos T, U, V, W, S) | Deadlock, ciclo D, T, E, V, Z, U |
| **T5** | Grafo 2 sem deadlock (8 processos e 6 recursos) | Sem deadlock |

### T1 – Grafo do slide 40

Entrada (`testes/T1_entrada.txt`):

```text
PROCESSOS A B C D E F G
RECURSOS R S T U V W
ARESTAS
R A
A S
C S
D S
F S
W F
B T
D T
T E
E V
V G
G U
U D
```

Saída:

```text
Há deadlock: D -> T -> E -> V -> G -> U -> D
```

Com `-v`, a lista L ao encontrar o ciclo é `[B, T, E, V, G, U, D, T]`, a mesma mostrada no slide 48. A partir de `D`, o arco para `S` leva a um beco sem saída (o algoritmo retrocede) e o arco para `T` fecha o ciclo.

### T2 – Grafo 1 (sem deadlock)

O Grafo 1 da aula mostra apenas os programas dos processos (A pede R e S, B pede S e T, C pede T e R), sem desenhar um estado de alocação. Por isso foi montado um estado em que as requisições ocorrem em ordem que não trava: A possui R e S, C possui T e pede R, e B pede S.

Entrada (`testes/T2_entrada.txt`):

```text
PROCESSOS A B C
RECURSOS R S T
ARESTAS
R A
S A
T C
C R
B S
```

Saída:

```text
Sem deadlock
```

Não há ciclo: A, que possui R e S, não está esperando por nenhum recurso. Assim A termina e libera R e S, o que permite que B e C prossigam.

### T3 – Grafo 2 (deadlock)

Conforme a observação do enunciado, a entrada foi montada com posse (R com A, S com B, T com C) e solicitações (A para S, B para T, C para R).

Entrada (`testes/T3_entrada.txt`):

```text
PROCESSOS A B C
RECURSOS R S T
ARESTAS
R A
S B
T C
A S
B T
C R
```

Saída:

```text
Há deadlock: A -> S -> B -> T -> C -> R -> A
```

Cada processo espera um recurso que está com outro, o que fecha o ciclo A, B, C e R, S, T.

### T4 – Grafo 1 com deadlock

Grafo desenhado pela equipe, com cinco processos e cinco recursos. Há um ciclo e um ramo que sai dele sem voltar.

Entrada (`testes/T4_entrada.txt`):

```text
PROCESSOS B D E Z F
RECURSOS T U V W S
ARESTAS
B T
D T
T E
E V
V Z
Z U
U D
Z W
W F
F S
```

Saída:

```text
Há deadlock: D -> T -> E -> V -> Z -> U -> D
```

Com `-v`, a lista L é `[B, T, E, V, Z, U, D, T]`. O processo `B` apenas pede `T`, que está com `E`, e entra no ciclo sem fazer parte dele. O ramo `Z -> W -> F -> S` também fica fora do ciclo: `Z` possui `W` e `F` solicita `S`, mas `S` não tem arco de saída. Como o arco `Z -> U` aparece antes de `Z -> W` no arquivo, o DFS segue por ele e fecha o ciclo sem precisar visitar esse ramo.

### T5 – Grafo 2 sem deadlock

Grafo desenhado pela equipe, com oito processos e seis recursos, ramificado e sem ciclo.

Entrada (`testes/T5_entrada.txt`):

```text
PROCESSOS A B C D E F G Z
RECURSOS R S T U V W
ARESTAS
R A
A S
C S
F S
W F
S D
U D
G U
D T
B T
T E
V E
Z V
```

Saída:

```text
Sem deadlock
```

Todos os caminhos do grafo terminam em `E`, que não solicita nenhum recurso. Os processos `A`, `C` e `F` esperam por `S`, que está com `D`, e `D` espera por `T`, que está com `E`. Como `E` não espera por ninguém, não existe ciclo. O algoritmo percorre cada nó de partida, recua em todos os becos sem saída e conclui que não há deadlock.

### Resultado da bateria de testes

```text
$ python deadlock.py --testes
[PASSOU] T1: Há deadlock: D -> T -> E -> V -> G -> U -> D
[PASSOU] T2: Sem deadlock
[PASSOU] T3: Há deadlock: A -> S -> B -> T -> C -> R -> A
[PASSOU] T4: Há deadlock: D -> T -> E -> V -> Z -> U -> D
[PASSOU] T5: Sem deadlock
```

## 7. Estrutura do repositório

```text
.
├── deadlock.py              # código-fonte (leitura, DFS, impressão e testes)
├── README.md                # este arquivo
└── testes/
    ├── T1_entrada.txt
    ├── T1_esperado.txt
    ├── T2_entrada.txt
    ├── T2_esperado.txt
    ├── T3_entrada.txt
    ├── T3_esperado.txt
    ├── T4_entrada.txt
    ├── T4_esperado.txt
    ├── T5_entrada.txt
    └── T5_esperado.txt
```

## 8. Organização do código

| Função | Papel |
|---|---|
| `ler_grafo` / `montar_grafo` | leitura e validação da entrada, construção da lista de adjacência |
| `detectar_ciclo` | DFS conforme a aula (lista L, arcos marcados, retrocesso) |
| `extrair_ciclo` | isola o ciclo de L e o normaliza |
| `formatar_resultado` | monta a mensagem `Há deadlock: ...` ou `Sem deadlock` |
| `rodar_testes` / `gerar_arquivos_de_teste` | execução e geração dos casos T1 a T5 |

## 9. Contribuição individual

| Integrante | Contribuição |
|---|---|
| _Tiago de Oliveira_ | **Leitura e validação da entrada.** Implementou `ler_grafo` e `montar_grafo`: leitura do formato `PROCESSOS / RECURSOS / ARESTAS`, tratamento de comentários e linhas em branco, e verificação de erros (nó não declarado, nome repetido, aresta entre dois processos ou dois recursos). Ex.: uma aresta `R X` com `X` não declarado gera `Erro: Linha 4: nó 'X' não foi declarado.` |
| _Matheus Braz_ | **Implementação da DFS.** Implementou `detectar_ciclo`, seguindo os passos da aula: lista L, arcos marcados, avanço pelo primeiro arco desmarcado e retrocesso em beco sem saída. Conferiu que no T1 a lista L chega a `[B, T, E, V, G, U, D, T]`, igual ao slide 48. |
| _Wandrio Neto_ | **Impressão do ciclo.** Implementou `extrair_ciclo` e `formatar_resultado`: isola o ciclo dentro de L, gira-o para começar pelo menor nome de nó e monta a saída `Há deadlock: D -> T -> E -> V -> G -> U -> D` ou `Sem deadlock`. |
| _Arthur Vale_ | **Casos de teste, execução e README.** Montou as entradas de T1, T2 e T3 a partir dos slides 40, 31 e 32 e as de T4 e T5 a partir dos grafos desenhados pela equipe, implementou `rodar_testes` e `gerar_arquivos_de_teste` (pasta `testes/`) e escreveu o README com instruções de execução e resultados. |
| _Rhayan Alves_ | **Apresentação e demonstração.** Preparou os slides e o roteiro da demonstração ao vivo: `--testes`, depois `-v` sobre o T1 para mostrar a lista L e o retrocesso. |

## 10. Atendimento às regras do trabalho

| Item exigido | Situação |
|---|---|
| Código em linguagem livre | Python 3 |
| Entrega com README explicando como compilar e executar | Seção 5 |
| Testes obrigatórios, com arquivos de entrada e saída esperada e resultados no README | Seção 6 e pasta `testes/` (T1 a T3 obrigatórios, T4 e T5 adicionais) |
| Formato de entrada único, documentado | Opção 1 (lista de arestas), seção 4 |
| Saída com "Há deadlock" e o ciclo, ou "Sem deadlock" | Seção 6 |
| Declaração da participação de cada integrante | Seção 9 |
| Apresentação de 5 a 8 minutos, com demonstração ao vivo | 