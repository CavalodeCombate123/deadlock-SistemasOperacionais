"""
Trabalho 2 - Detector de deadlock com grafo de alocação (1 recurso de cada tipo)
Algoritmo: busca em profundidade (DFS) conforme a aula (slides 41-48):
lista L, arcos marcados e retrocesso em beco sem saída.

COMO EXECUTAR
    python deadlock.py grafo.txt      # analisa um arquivo de entrada
    python deadlock.py --gerar-testes # cria a pasta testes/ (entrada + saída esperada)
    python deadlock.py --testes       # roda T1, T2, T3, T4 e T5
    python deadlock.py -v grafoexemplo.txt   # mostra também a lista L do algoritmo
    
FORMATO DE ENTRADA (Opção 1 - lista de arestas)
    PROCESSOS A B C D E F G
    RECURSOS R S T U V W
    ARESTAS
    R A        # recurso -> processo : o processo POSSUI o recurso
    A S        # processo -> recurso : o processo SOLICITA o recurso
    Linhas em branco e comentários (#) são ignorados.

SAÍDAS ESPERADAS
    T1 (grafo da aula, slide 40):
        Há deadlock: D -> T -> E -> V -> G -> U -> D
    T2 (grafo 1 da aula, requisições em ordem que não trava):
        Sem deadlock
    T3 (grafo 2 da aula, A->S, B->T, C->R, cada um já com um recurso):
        Há deadlock: A -> S -> B -> T -> C -> R -> A
    T4 (grafo 1 com deadlock, ciclo com processos B, D, E, Z, F e recursos T, U, V, W, S):
        Há deadlock: D -> T -> E -> V -> Z -> U -> D
    T5 (grafo 2 sem deadlock, 8 processos e 6 recursos, sem ciclo):
        Sem deadlock

    O ciclo é impresso começando pelo menor nome de nó (ordem alfabética).
    
    Demonstração sugerida: `--testes`, depois `-v` sobre o T1 |
"""

import sys
from pathlib import Path


class ErroDeEntrada(Exception):
    """Entrada mal formatada ou inconsistente."""


# ----------------------------------------------------------------------------
# Leitura e validação da entrada
# ----------------------------------------------------------------------------
def ler_grafo(texto):
    """Lê o formato de lista de arestas e devolve (nós, adjacência)."""
    processos, recursos, arestas = [], [], []
    em_arestas = False

    for num, linha in enumerate(texto.splitlines(), start=1):
        linha = linha.split("#", 1)[0].strip()
        if not linha:
            continue
        partes = linha.split()
        cabecalho = partes[0].upper()

        if cabecalho == "PROCESSOS":
            processos, em_arestas = partes[1:], False
        elif cabecalho == "RECURSOS":
            recursos, em_arestas = partes[1:], False
        elif cabecalho == "ARESTAS":
            em_arestas = True
        elif em_arestas and len(partes) == 2:
            arestas.append((partes[0], partes[1], num))
        else:
            raise ErroDeEntrada(f"Linha {num} inválida: '{linha}'")

    return montar_grafo(processos, recursos, arestas)


def montar_grafo(processos, recursos, arestas):
    nos = processos + recursos
    if len(set(nos)) != len(nos):
        raise ErroDeEntrada("Há nomes repetidos entre processos e recursos.")

    adjacencia = {no: [] for no in nos}
    for origem, destino, num in arestas:
        for no in (origem, destino):
            if no not in adjacencia:
                raise ErroDeEntrada(f"Linha {num}: nó '{no}' não foi declarado.")
        if (origem in processos) == (destino in processos):
            raise ErroDeEntrada(
                f"Linha {num}: aresta '{origem} {destino}' deve ligar "
                "um processo a um recurso."
            )
        adjacencia[origem].append(destino)
    return nos, adjacencia


# ----------------------------------------------------------------------------
# Detecção de ciclo por DFS 
# ----------------------------------------------------------------------------
def detectar_ciclo(nos, adjacencia):
    """
    Devolve (ciclo, L). Se não houver ciclo, ciclo é None.
    L é a lista de nós percorrida quando o ciclo foi encontrado.
    """
    for inicio in nos:                       # passo 1: cada nó como partida
        L = [inicio]                         # passo 2: L vazia + arcos desmarcados
        marcados = set()

        while True:
            atual = L[-1]
            saidas = [d for d in adjacencia[atual] if (atual, d) not in marcados]

            if saidas:                       # passos 4 e 5: segue um arco desmarcado
                proximo = saidas[0]
                marcados.add((atual, proximo))
                L.append(proximo)
                if L.count(proximo) > 1:     # passo 3: nó repetido => ciclo
                    return extrair_ciclo(L), L
            elif atual == inicio:            # passo 6: voltou à raiz, sem ciclo
                break
            else:                            # passo 6: beco sem saída, recua
                L.pop()

    return None, []


def extrair_ciclo(L):
    """Isola o ciclo de L e o gira para começar pelo menor nome de nó."""
    repetido = L[-1]
    ciclo = L[L.index(repetido):-1]
    k = ciclo.index(min(ciclo))
    ciclo = ciclo[k:] + ciclo[:k]
    return ciclo + [ciclo[0]]


def formatar_resultado(ciclo):
    if ciclo is None:
        return "Sem deadlock"
    return "Há deadlock: " + " -> ".join(ciclo)


def analisar(texto, verboso=False):
    nos, adjacencia = ler_grafo(texto)
    ciclo, L = detectar_ciclo(nos, adjacencia)
    saida = formatar_resultado(ciclo)
    if verboso and ciclo:
        saida += "\nL = [" + ", ".join(L) + "]"
    return saida


# ----------------------------------------------------------------------------
# Casos de teste (T1 a T5)
# ----------------------------------------------------------------------------
T1 = """\
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
"""

T2 = """\
PROCESSOS A B C
RECURSOS R S T
ARESTAS
R A
S A
T C
C R
B S
"""

T3 = """\
PROCESSOS A B C
RECURSOS R S T
ARESTAS
R A
S B
T C
A S
B T
C R
"""

T4 = """\
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
"""

T5 = """\
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
"""

TESTES = {
    "T1": (T1, "Há deadlock: D -> T -> E -> V -> G -> U -> D"),
    "T2": (T2, "Sem deadlock"),
    "T3": (T3, "Há deadlock: A -> S -> B -> T -> C -> R -> A"),
    "T4": (T4, "Há deadlock: D -> T -> E -> V -> Z -> U -> D"),
    "T5": (T5, "Sem deadlock"),
}


def rodar_testes():
    falhas = 0
    for nome, (entrada, esperado) in TESTES.items():
        obtido = analisar(entrada)
        ok = obtido == esperado
        falhas += not ok
        print(f"[{'PASSOU' if ok else 'FALHOU'}] {nome}: {obtido}")
        if not ok:
            print(f"          esperado: {esperado}")
    return 1 if falhas else 0


def gerar_arquivos_de_teste(pasta="testes"):
    Path(pasta).mkdir(exist_ok=True)
    for nome, (entrada, esperado) in TESTES.items():
        Path(pasta, f"{nome}_entrada.txt").write_text(entrada, encoding="utf-8")
        Path(pasta, f"{nome}_esperado.txt").write_text(esperado + "\n", encoding="utf-8")
    print(f"Arquivos de teste gravados em '{pasta}/'.")


# ----------------------------------------------------------------------------
# Linha de comando
# ----------------------------------------------------------------------------
def main(argv):
    verboso = "-v" in argv
    args = [a for a in argv if a != "-v"]

    if not args:
        print(__doc__)
        return 0
    if args[0] == "--testes":
        return rodar_testes()
    if args[0] == "--gerar-testes":
        gerar_arquivos_de_teste()
        return 0

    try:
        texto = Path(args[0]).read_text(encoding="utf-8")
        print(analisar(texto, verboso))
    except (OSError, ErroDeEntrada) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))