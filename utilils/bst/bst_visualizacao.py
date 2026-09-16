"""
Visualizacao (matplotlib) do algoritmo em bst_core.py: gera uma
IMAGEM ESTATICA (PNG) da arvore ja pronta -- sem animacao.

Uso direto (funcoes soltas):
    from bst_visualizacao import gerar_imagem_cripto, gerar_imagem_decripto
    resultado = gerar_imagem_cripto("minha-senha", "texto secreto", "arvore.png")
    # resultado = {"cifra": "...", "imagem": "arvore.png"}

Uso via classe:
    from bst_visualizacao import BSTCripto
    bst = BSTCripto("minha-senha")
    resultado = bst.imagem_cripto("texto secreto", "arvore.png")
"""

import math

import matplotlib

matplotlib.use("Agg")  # backend sem tela -- TEM que vir antes do import do pyplot

import matplotlib.pyplot as plt

from bst_core import PERCURSOS, BalancedBST, cifrar, decifrar


# ======================================================================
# AUXILIARES DE DESENHO
# ======================================================================


def _posicoes_layout(raiz):
    """Calcula (x, y) de cada no: x = posicao em-ordem (deixa a arvore
    legivel, sem cruzar galhos), y = -profundidade (raiz no topo)."""
    posicoes = {}
    contador = [0]

    def walk(no, profundidade):
        if no is None:
            return
        walk(no.left, profundidade + 1)
        posicoes[id(no)] = (contador[0], -profundidade)
        contador[0] += 1
        walk(no.right, profundidade + 1)

    walk(raiz, 0)
    return posicoes


def _profundidades(raiz):
    prof = {}

    def walk(no, d):
        if no is None:
            return
        prof[id(no)] = d
        walk(no.left, d + 1)
        walk(no.right, d + 1)

    walk(raiz, 0)
    return prof


def _nos_na_ordem(raiz, func_percurso):
    """Anda na arvore com a MESMA funcao de percurso usada (preorder/
    inorder/postorder), coletando os objetos _Node."""
    nos = []

    def walk_pre(n):
        if n:
            nos.append(n)
            walk_pre(n.left)
            walk_pre(n.right)

    def walk_in(n):
        if n:
            walk_in(n.left)
            nos.append(n)
            walk_in(n.right)

    def walk_post(n):
        if n:
            walk_post(n.left)
            walk_post(n.right)
            nos.append(n)

    caminhada = {
        BalancedBST.preorder: walk_pre,
        BalancedBST.inorder: walk_in,
        BalancedBST.postorder: walk_post,
    }[func_percurso]
    caminhada(raiz)
    return nos


def _desenhar_arestas(ax, no, posicoes):
    if no is None:
        return
    x0, y0 = posicoes[id(no)]
    for filho in (no.left, no.right):
        if filho:
            x1, y1 = posicoes[id(filho)]
            ax.plot([x0, x1], [y0, y1], color="#9AA5B1", zorder=1, linewidth=1.6)
            _desenhar_arestas(ax, filho, posicoes)


def _cor_por_profundidade(d, d_max):
    frac = 0.35 + 0.5 * (d / max(1, d_max))
    return plt.cm.Blues(frac)


def _desenhar_arvore_estatica(arvore, func, caminho_imagem):
    """
    Desenha a arvore JA PRONTA (todos os nos de uma vez, sem
    animacao), colorida por profundidade, com a altura/balanceamento
    no titulo. Usa scatter (tamanho em pontos) em vez de Circle
    (tamanho em unidade de dado) porque a arvore fica bem mais larga
    (eixo X) do que alta (eixo Y) -- um Circle nessa proporcao sai
    achatado, parecendo elipse; scatter sempre desenha bolinhas
    redondas de verdade.
    """
    nos_ordem = _nos_na_ordem(arvore.root, func)
    n = len(nos_ordem)
    posicoes = _posicoes_layout(arvore.root)
    prof = _profundidades(arvore.root)
    d_max = max(prof.values()) if prof else 0

    fig, ax = plt.subplots(figsize=(7, 7))
    fig.patch.set_facecolor("white")
    _desenhar_arestas(ax, arvore.root, posicoes)

    xs = [posicoes[id(no)][0] for no in nos_ordem]
    ys = [posicoes[id(no)][1] for no in nos_ordem]
    cores = [_cor_por_profundidade(prof[id(no)], d_max) for no in nos_ordem]
    tamanho_ponto = max(35, min(260, 9000 / max(n, 1)))  # arvores grandes -> pontos menores

    ax.scatter(xs, ys, s=tamanho_ponto, c=cores, edgecolors="#1C3D5A", linewidths=1.0, zorder=2)

    altura_real = arvore.height()
    altura_teorica = math.ceil(math.log2(n + 1)) if n > 0 else 0
    balanceada = "balanceada ✓" if altura_real == altura_teorica else "DESBALANCEADA ✗"
    ax.set_title(
        f"n = {n}    altura = {altura_real}    ⌈log₂(n+1)⌉ = {altura_teorica}    {balanceada}",
        fontsize=11, fontweight="bold", color="#212529",
    )
    ax.set_xlim(-1, n + 1)
    ax.set_ylim(-d_max - 1, 1.2)
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(caminho_imagem, dpi=130, facecolor="white")
    plt.close(fig)


# ======================================================================
# CRIPTO / DECRIPTO + IMAGEM
# ======================================================================


def gerar_imagem_cripto(chave: str, texto: str, caminho_imagem: str, lixo_max: int = 64) -> dict:
    """
    Cifra UMA VEZ e desenha a arvore resultante -- a imagem e
    garantidamente a mesma arvore usada pra gerar o token devolvido
    (nunca chama cifrar() de novo).

    Devolve {"cifra": <token>, "imagem": <caminho_imagem>}.
    """
    token, arvore, percurso = cifrar(chave, texto, _debug=True, lixo_max=lixo_max)
    _, func = PERCURSOS[percurso]
    _desenhar_arvore_estatica(arvore, func, caminho_imagem)
    return {"cifra": token, "imagem": caminho_imagem}


def gerar_imagem_decripto(chave: str, token: str, caminho_imagem: str) -> dict:
    """
    Decifra UMA VEZ e desenha a arvore reconstruida.

    Devolve {"texto": <texto decifrado>, "imagem": <caminho_imagem>}.
    """
    texto, arvore, percurso = decifrar(chave, token, _debug=True)
    _, func = PERCURSOS[percurso]
    _desenhar_arvore_estatica(arvore, func, caminho_imagem)
    return {"texto": texto, "imagem": caminho_imagem}


# ======================================================================
# CLASSE
# ======================================================================


class BSTCripto:
    """
    Wrapper orientado a objeto em cima das funcoes de bst_core e da
    imagem estatica deste arquivo. Guarda a chave uma vez no construtor.

    Exemplo:
        bst = BSTCripto("senha-do-anderson")

        token = bst.cifrar("texto secreto")
        texto = bst.decifrar(token)

        resultado = bst.imagem_cripto("texto secreto", "arvore.png")
        # {"cifra": "...", "imagem": "arvore.png"}
        resultado = bst.imagem_decripto(resultado["cifra"], "arvore_decripto.png")
        # {"texto": "texto secreto", "imagem": "arvore_decripto.png"}
    """

    def __init__(self, chave: str):
        self.chave = chave

    def cifrar(self, texto: str, lixo_max: int = 64) -> str:
        """Cifra sem gerar imagem -- so o token. Ver bst_core.cifrar."""
        return cifrar(self.chave, texto, lixo_max=lixo_max)

    def decifrar(self, token: str) -> str:
        """Decifra sem gerar imagem -- so o texto. Ver bst_core.decifrar."""
        return decifrar(self.chave, token)

    def imagem_cripto(self, texto: str, caminho_imagem: str) -> dict:
        """Cifra E desenha a árvore final. Devolve {"cifra", "imagem"}."""
        return gerar_imagem_cripto(self.chave, texto, caminho_imagem)

    def imagem_decripto(self, token: str, caminho_imagem: str) -> dict:
        """Decifra E desenha a árvore final. Devolve {"texto", "imagem"}."""
        return gerar_imagem_decripto(self.chave, token, caminho_imagem)


# ======================================================================
# USO
# ======================================================================

if __name__ == "__main__":
    bst = BSTCripto("senha-do-anderson")
    texto = "OI TUDO BEM"

    resultado_cripto = bst.imagem_cripto(texto, "cripto.png")
    resultado_decripto = bst.imagem_decripto(resultado_cripto["cifra"], "decripto.png")

    print("texto original    :", repr(texto))
    print("resultado cripto  :", resultado_cripto)
    print("resultado decripto:", resultado_decripto)
    print("bate?             :", resultado_decripto["texto"] == texto)
