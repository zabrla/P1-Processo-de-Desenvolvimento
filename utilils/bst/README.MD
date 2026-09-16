# Documentação Técnica — Criptografia com BST Balanceada

Documento de referência técnica do módulo de criptografia didática baseado em Árvore Binária de Busca balanceada e percursos clássicos.

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Fundamentação do Algoritmo](#2-fundamentação-do-algoritmo)
3. [Arquitetura do Sistema](#3-arquitetura-do-sistema)
4. [Especificação dos Módulos](#4-especificação-dos-módulos)
5. [Fluxo de Execução](#5-fluxo-de-execução)
6. [Formato do Token Cifrado](#6-formato-do-token-cifrado)
7. [Interface de Uso](#7-interface-de-uso)
8. [Módulo de Visualização](#8-módulo-de-visualização)
9. [Análise de Segurança](#9-análise-de-segurança)
10. [Exemplos de Integração](#10-exemplos-de-integração)
11. [Referência de Termos](#11-referência-de-termos)

---

## 1. Visão Geral

Este projeto implementa um algoritmo de cifra por transposição estruturada, no qual uma Árvore Binária de Busca (BST) perfeitamente balanceada é utilizada como estrutura intermediária para o embaralhamento de bytes. O processo de cifragem consiste em percorrer a árvore segundo um dos três percursos clássicos (pré-ordem, em-ordem ou pós-ordem) e extrair a sequência de bytes na ordem de visitação resultante.

O sistema é composto por dois módulos independentes:

| Módulo | Responsabilidade | Dependências externas |
|---|---|---|
| `bst_core.py` | Núcleo do algoritmo. Contém a BST, os percursos, e as funções `cifrar` e `decifrar`. Não possui dependências visuais. | Nenhuma (apenas biblioteca padrão: `random`, `secrets`) |
| `bst_visualizacao.py` | Geração de imagens estáticas (PNG) das árvores geradas. Utilizado para estudo, debug e inspeção do estado interno. | `matplotlib` |

O módulo núcleo é adequado para uso em ambientes restritos (embarcados, scripts CLI, pipelines), enquanto o módulo de visualização é opcional e voltado para análise pedagógica.

---

## 2. Fundamentação do Algoritmo

O algoritmo pode ser classificado como uma **cifra por transposição com estrutura de dados intermediária**. O princípio operacional é:

1. Cada byte da mensagem recebe um valor inteiro denominado *rank*, calculado deterministicamente a partir da chave fornecida pelo usuário.
2. Os bytes são inseridos em uma BST balanceada, ordenados por rank.
3. A sequência cifrada é obtida percorrendo-se a árvore segundo uma ordem definida (gravada no token).
4. O decifrador reconstrói a mesma árvore a partir da chave e do tamanho conhecido, percorre-a na mesma ordem e reassocia cada byte à sua posição original.

A propriedade fundamental que garante o funcionamento é o **determinismo do embaralhamento em função da chave**: dado o mesmo par `(chave, n)`, a ordem dos ranks é idêntica, e portanto a árvore é isomórfica.

### Propriedades Garantidas

- **Balanceamento por construção.** A árvore é montada por bisseção sobre uma lista previamente ordenada por rank, resultando em altura `⌈log₂(n+1)⌉` sem necessidade de rotações.
- **Determinismo do rank.** O módulo `random` é semeado com a chave do usuário, garantindo reprodutibilidade.
- **Não-determinismo da saída.** O percurso é sorteado em cada chamada, e bytes de lixo são adicionados antes da cifragem, de modo que a mesma mensagem cifrada com a mesma chave produza tokens distintos.

---

## 3. Arquitetura do Sistema

```
+--------------------------+
|   Aplicação cliente      |
+------------+-------------+
             |
   +---------+----------+
   |                    |
   v                    v
+------------------+  +----------------------+
|  bst_core.py     |  | bst_visualizacao.py  |
|  (núcleo)        |<-| (opcional, estuda)   |
+------------------+  +----------------------+
   |        |                     |
   |        |                     v
   v        v              +--------------+
+------+ +--------+        |  matplotlib  |
| _Node| |Balanced|        +--------------+
|      | |  BST   |
+------+ +--------+
```

O `bst_visualizacao.py` consome o núcleo via importação direta (`from bst_core import ...`) e nunca duplica lógica de cifragem. A imagem gerada é sempre proveniente da árvore efetivamente utilizada na produção do token, evitando inconsistências entre representação visual e dado cifrado.

---

## 4. Especificação dos Módulos

### 4.1 `bst_core.py`

#### 4.1.1 Classe `_Node`

Representa um nó da árvore.

```python
class _Node:
    __slots__ = ("key", "value", "left", "right")
```

| Atributo | Tipo | Descrição |
|---|---|---|
| `key` | `int` | Chave de busca, correspondente ao rank calculado. |
| `value` | `tuple[int, int \| None]` | Par `(posição_original, byte)`. O byte é `None` durante a reconstrução no decifrador, antes da reassociação. |
| `left` | `_Node \| None` | Filho esquerdo (chaves menores). |
| `right` | `_Node \| None` | Filho direito (chaves maiores). |

A diretiva `__slots__` é utilizada para reduzir consumo de memória em árvores de grande porte.

#### 4.1.2 Classe `BalancedBST`

Responsável pela construção e percursos.

**Métodos públicos:**

- `build_sorted(pairs: list[tuple[int, tuple]]) -> None` — Constrói a árvore a partir de uma lista **já ordenada** por chave. Pré-condição obrigatória.
- `preorder() -> list[tuple]` — Retorna os pares `(chave, valor)` em pré-ordem.
- `inorder() -> list[tuple]` — Retorna os pares em em-ordem (ordem crescente de chave).
- `postorder() -> list[tuple]` — Retorna os pares em pós-ordem.
- `height() -> int` — Altura real da árvore. Utilizada somente pela camada de visualização.

**Invariante:** A árvore resultante de `build_sorted` é sempre perfeitamente balanceada.

#### 4.1.3 Tabela `PERCURSOS`

Mapa que associa um código binário gravado no token à função de percurso correspondente.

| Código | Percurso | Método |
|---|---|---|
| `"0"` | pré-ordem | `BalancedBST.preorder` |
| `"1"` | em-ordem | `BalancedBST.inorder` |
| `"2"` | pós-ordem | `BalancedBST.postorder` |

#### 4.1.4 Funções auxiliares internas

- `_ordem_embaralhada(chave: str, n: int) -> list[int]` — Gera uma permutação determinística dos índices `[0, n-1]` com base em `random.Random(chave)`.
- `_montar_arvore(chave: str, n: int, dados: list[int] | None) -> BalancedBST` — Constrói a árvore balanceada a partir da chave e do tamanho. Quando `dados=None`, os valores dos nós ficam sem byte associado (usado no decifrador).

#### 4.1.5 Assinaturas das funções principais

```python
def cifrar(chave: str, texto: str, _debug: bool = False, lixo_max: int = 64) -> str | tuple
def decifrar(chave: str, token: str, _debug: bool = False) -> str | tuple
```

**Parâmetros:**

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `chave` | `str` | Senha do usuário. Utilizada como semente do gerador determinístico. |
| `texto` | `str` | Mensagem em claro (cifrar) ou token (decifrar). |
| `lixo_max` | `int` | Quantidade máxima de bytes de lixo (0 a 64 por padrão). |
| `_debug` | `bool` | Quando `True`, retorna também a árvore e o percurso utilizados. |

**Retorno:**

- `cifrar` retorna `str` (token) ou, em modo debug, `(token, arvore, percurso)`.
- `decifrar` retorna `str` (texto) ou, em modo debug, `(texto, arvore, percurso)`.

### 4.2 `bst_visualizacao.py`

#### 4.2.1 Funções auxiliares de desenho

- `_posicoes_layout(raiz)` — Atribui coordenadas `(x, y)` a cada nó. O eixo X é definido pela ordem em-ordem (evita cruzamento de arestas); o eixo Y é definido pela profundidade negativa (raiz no topo).
- `_profundidades(raiz)` — Mapeia cada nó à sua profundidade.
- `_nos_na_ordem(raiz, func_percurso)` — Percorre a árvore com a mesma função de percurso escolhida, retornando objetos `_Node` na ordem correta.
- `_desenhar_arestas(ax, no, posicoes)` — Traça os segmentos entre pais e filhos.
- `_cor_por_profundidade(d, d_max)` — Retorna uma cor do colormap `Blues` proporcional à profundidade.
- `_desenhar_arvore_estatica(arvore, func, caminho_imagem)` — Função principal de renderização. Utiliza `scatter` (tamanho em pontos) em vez de `Circle` (tamanho em unidades de dado), evitando distorção em proporções alongadas no eixo X.

#### 4.2.2 Funções públicas

```python
def gerar_imagem_cripto(chave, texto, caminho_imagem, lixo_max=64) -> dict
def gerar_imagem_decripto(chave, token, caminho_imagem) -> dict
```

Ambas executam a operação **uma única vez** e reaproveitam a árvore resultante para gerar a imagem, garantindo consistência entre token e representação visual.

#### 4.2.3 Classe `BSTCripto`

Wrapper orientado a objeto, útil quando a mesma chave é utilizada em múltiplas operações.

```python
class BSTCripto:
    def __init__(self, chave: str)
    def cifrar(self, texto: str, lixo_max: int = 64) -> str
    def decifrar(self, token: str) -> str
    def imagem_cripto(self, texto: str, caminho_imagem: str) -> dict
    def imagem_decripto(self, token: str, caminho_imagem: str) -> dict
```

---

## 5. Fluxo de Execução

### 5.1 Cifragem

Entrada: `chave="senha-do-anderson"`, `texto="ABC"`.

1. **Codificação.** `"ABC"` é convertido para bytes UTF-8: `[65, 66, 67]`.
2. **Injeção de lixo.** Uma quantidade aleatória `l` (0 ≤ l ≤ `lixo_max`) é sorteada via `secrets`. Suponha `l=3`: `[65, 66, 67, 203, 47, 91]`. Tamanho total `n=6`, tamanho real `t=3`.
3. **Cálculo dos ranks.** A chave semeia `random.Random`; os índices `[0..5]` são embaralhados, gerando `ordem`. A lista inversa `rank` é calculada:
   ```
   ordem = [1, 2, 0, 5, 3, 4]
   rank  = [2, 0, 1, 4, 5, 3]
   ```
4. **Pareamento.** Cada byte é associado a `(rank[i], (i, byte))`.
5. **Ordenação.** A lista é ordenada por rank crescente.
6. **Construção da BST.** `build_sorted` monta a árvore por bisseção recursiva, resultando em altura `⌈log₂(6+1)⌉ = 3`.
7. **Sorteio do percurso.** `random.choice(["0", "1", "2"])`.
8. **Extração.** O percurso é aplicado à árvore; os bytes são lidos na ordem de visitação e concatenados em `cifra`.
9. **Montagem do token.** `token = f"{percurso_bin}${cifra_hex}#{n_bin}#{t_bin}"`.

### 5.2 Decifragem

Entrada: `chave="senha-do-anderson"`, `token="0$...hex...#110#11"`.

1. **Parsing.** O token é dividido em quatro campos: percurso, cifra (hex), tamanho total, tamanho real.
2. **Reconstrução da árvore.** `_montar_arvore(chave, n, None)` reconstrói a mesma topologia da etapa de cifragem, sem bytes associados.
3. **Percurso.** O percurso gravado no token é aplicado à árvore.
4. **Reassociação.** Para cada par `((chave, (pos, _)), byte)` obtido por `zip`, executa-se `dados[pos] = byte`.
5. **Truncamento.** Apenas os primeiros `t` bytes são considerados: `dados[:t]`.
6. **Decodificação.** Os bytes são decodificados de UTF-8.

Em modo `_debug=True`, antes do truncamento, os valores dos nós da árvore reconstruída são preenchidos com os bytes recebidos, permitindo inspeção visual do estado completo (incluindo lixo).

---

## 6. Formato do Token Cifrado

```
<percurso_bin>$<cifra_hex>#<tamanho_total_bin>#<tamanho_real_bin>
```

| Campo | Codificação | Descrição |
|---|---|---|
| `percurso_bin` | binário, sem prefixo `0b` | `"0"`, `"1"` ou `"2"` |
| `cifra_hex` | hexadecimal | bytes (texto + lixo) na ordem de visitação |
| `tamanho_total_bin` | binário | `n`, total de bytes cifrados |
| `tamanho_real_bin` | binário | `t`, bytes que compõem o texto original |

Exemplo concreto:

```
0$434241f2a91c#110#11
```

Interpretação:

| Campo | Valor | Significado |
|---|---|---|
| `percurso_bin` | `0` | pré-ordem |
| `cifra_hex` | `434241f2a91c` | 6 bytes cifrados |
| `tamanho_total_bin` | `110` | n = 6 |
| `tamanho_real_bin` | `11` | t = 3 (portanto, 3 bytes de lixo) |

A escolha de binário e hexadecimal é puramente cosmética — ambos são representações textuais de inteiros e bytes, e poderiam ser substituídos por decimal e base64 sem alteração semântica. A utilidade prática é inspeção manual e baixo overhead de caracteres.

---

## 7. Interface de Uso

### 7.1 Uso direto via funções

```python
from bst_core import cifrar, decifrar

token = cifrar("minha-senha", "texto secreto")
texto = decifrar("minha-senha", token)
assert texto == "texto secreto"
```

### 7.2 Uso via classe

```python
from bst_visualizacao import BSTCripto

bst = BSTCripto("minha-senha")

token = bst.cifrar("texto secreto")
texto = bst.decifrar(token)

resultado = bst.imagem_cripto("texto secreto", "arvore_cripto.png")
# resultado = {"cifra": "...", "imagem": "arvore_cripto.png"}

resultado = bst.imagem_decripto(token, "arvore_decripto.png")
# resultado = {"texto": "texto secreto", "imagem": "arvore_decripto.png"}
```

### 7.3 Uso via funções soltas de visualização

```python
from bst_visualizacao import gerar_imagem_cripto, gerar_imagem_decripto

r1 = gerar_imagem_cripto("senha", "mensagem", "cripto.png")
r2 = gerar_imagem_decripto("senha", r1["cifra"], "decripto.png")
```

### 7.4 Execução como script

```bash
python bst_visualizacao.py
```

Gera `cripto.png` e `decripto.png` no diretório corrente, executando o ciclo completo com o texto de exemplo embutido.

### 7.5 Ajuste do volume de lixo

```python
token = cifrar("senha", "texto", lixo_max=128)
```

O valor padrão de `lixo_max` é 64. Aumentá-lo eleva o custo computacional (árvores maiores) e o tamanho do token, em troca de maior ruído.

### 7.6 Modo de depuração

```python
token, arvore, percurso = cifrar("senha", "texto", _debug=True)
texto, arvore, percurso = decifrar("senha", token, _debug=True)
```

Retorna objetos internos. Utilizado pela camada de visualização para evitar cifrar duas vezes.

---

## 8. Módulo de Visualização

### 8.1 Estratégia de Layout

O cálculo das coordenadas segue duas regras:

1. **Eixo X:** posição em-ordem do nó (contador incrementado durante o percurso em-ordem). Essa escolha garante que sub-árvores esquerda e direita se disponham naturalmente em torno da raiz sem sobreposição horizontal.
2. **Eixo Y:** profundidade negativa. A raiz fica em `y=0`, filhos em `y=-1`, netos em `y=-2`, e assim por diante.

### 8.2 Renderização

- **Arestas:** segmentos de reta desenhados com `ax.plot`, cor `#9AA5B1`, largura 1.6, `zorder=1`.
- **Nós:** desenhados com `ax.scatter` (tamanho em pontos, sempre circular). A escolha por `scatter` em vez de `Circle` decorre da diferença de escala entre os eixos X (proporcional a `n`) e Y (proporcional a `log₂ n`). Círculos definidos em unidades de dados seriam distorcidos horizontalmente em árvores grandes.
- **Coloração:** gradiente gerado por `plt.cm.Blues` com fração `0.35 + 0.5 * (d / d_max)`. Nós mais profundos ficam mais escuros.
- **Tamanho do ponto:** `max(35, min(260, 9000 / n))` — adaptativo ao número de nós, evitando colisão visual em árvores densas.
- **Título:** exibe `n`, altura real, altura teórica `⌈log₂(n+1)⌉` e classificação `balanceada` ou `DESBALANCEADA`.

### 8.3 Backend `Agg`

O módulo força `matplotlib.use("Agg")` antes do `import pyplot`. O backend `Agg` é puramente baseado em rasterização em memória, não requer servidor gráfico (`X11`, `Wayland`) e é seguro em ambientes headless (containers, CI, servidores). A ordem de importação é obrigatória: alterar o backend após importar `pyplot` não tem efeito.

---

## 9. Análise de Segurança

### 9.1 Propriedades Implementadas

| Propriedade | Status | Observação |
|---|---|---|
| Determinismo em função da chave | Presente | Mesma chave + mesmo `n` produzem a mesma topologia de árvore |
| Tamanho de saída variável | Presente | Bytes de lixo sorteados via `secrets` a cada chamada |
| Ordem de leitura imprevisível | Presente | Percurso sorteado via `random.choice` |
| Balanceamento garantido | Presente | Construção por bisseção, altura `⌈log₂(n+1)⌉` |
| Suporte a Unicode | Presente | Bytes processados individualmente; decodificação UTF-8 no final |
| Autenticação de integridade | Ausente | Nenhum MAC ou assinatura. Alterações no token não são detectadas |
| Primitivas criptográficas modernas | Ausente | Não utiliza AES, ChaCha20, HMAC ou equivalentes |
| Gerador criptograficamente seguro para a chave | Ausente | `random.Random(chave)` **não** é CSPRNG |

### 9.2 Limitações Conhecidas

1. **Ausência de integridade.** Um atacante pode modificar qualquer byte do token. O decifrador pode aceitar a alteração silenciosamente ou falhar com `UnicodeDecodeError`, dependendo do byte alterado. Não há garantia de detecção.

2. **Semente fraca.** `random.Random` implementa o algoritmo Mersenne Twister, adequado para simulação, não para criptografia. A segurança depende inteiramente da entropia da chave fornecida pelo usuário, e ainda assim o mapeamento `chave → permutação` não é resistente a ataques de força bruta otimizados.

3. **Vazamento por erro de decodificação.** Com a chave errada, o decifrador geralmente falha em `decode("utf-8")`. Essa falha constitui um oráculo de verificação de chave: um atacante pode distinguir "chave errada" de "chave certa" com uma tentativa por chave candidata.

4. **Análise estatística em volume.** Embora o lixo aumente o ruído, um atacante com grandes volumes de mensagens sob a mesma chave pode aplicar análise de frequência e correlação.

5. **Sem forward secrecy.** A comprometimento da chave compromete mensagens passadas e futuras.

### 9.3 Recomendações de Uso

**Adequado para:**

- Estudo de estruturas de dados (BST, percursos, balanceamento).
- Trabalhos acadêmicos, provas de conceito, demonstrações pedagógicas.
- Exercícios de análise de algoritmos e complexidade.

**Inadequado para:**

- Proteção de dados sensíveis em produção.
- Comunicação em redes não confiáveis.
- Armazenamento de credenciais, chaves, tokens de sessão.

**Alternativas recomendadas para produção:** bibliotecas consolidadas como `cryptography` (Python), `libsodium`, ou primitivas de alto nível como AES-GCM, ChaCha20-Poly1305, ou XChaCha20-Poly1305.

---

## 10. Exemplos de Integração

### 10.1 Ciclo básico com verificação

```python
from bst_core import cifrar, decifrar

chave = "minha-senha-secreta"
texto = "Mensagem de teste"

token = cifrar(chave, texto)
recuperado = decifrar(chave, token)

assert recuperado == texto
print("Token:", token)
```

### 10.2 Detecção de chave incorreta

```python
from bst_core import cifrar, decifrar

token = cifrar("senha-correta", "mensagem secreta")

try:
    texto = decifrar("senha-incorreta", token)
    print("Resultado inesperado:", texto)
except UnicodeDecodeError:
    print("Chave incorreta detectada via erro de decodificação UTF-8")
```

### 10.3 Geração de imagem para análise

```python
from bst_visualizacao import gerar_imagem_cripto

resultado = gerar_imagem_cripto(
    chave="senha-de-estudo",
    texto="Exemplo",
    caminho_imagem="arvore.png",
)

print("Token :", resultado["cifra"])
print("Imagem:", resultado["imagem"])
```

### 10.4 Simulação de múltiplas mensagens

```python
from bst_core import cifrar, decifrar

chave = "senha-compartilhada"

for msg in ["primeira", "segunda", "terceira"]:
    token = cifrar(chave, msg)
    recuperado = decifrar(chave, token)
    assert recuperado == msg
    print(f"{msg!r} -> {token[:24]}...")
```

Cada iteração gera token diferente mesmo para mensagens distintas, em função do lixo variável e do percurso sorteado.

### 10.5 Integração com pipeline de processamento

```python
from bst_core import cifrar

def persistir_mensagem(chave: str, caminho: str, texto: str) -> None:
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(cifrar(chave, texto, lixo_max=32))
```

---

## 11. Referência de Termos

| Termo | Definição |
|---|---|
| BST | Árvore Binária de Busca. Estrutura em que o valor de cada nó é maior que todos os seus descendentes à esquerda e menor que todos à direita. |
| Balanceamento | Propriedade de uma árvore cuja altura é O(log n). Aqui garantida por construção via bisseção. |
| Rank | Valor inteiro associado a cada posição de byte, determinando a ordem de inserção na árvore. |
| Percurso | Sequência sistemática de visitação dos nós. |
| Pré-ordem | Visita raiz, depois sub-árvore esquerda, depois direita. |
| Em-ordem | Visita sub-árvore esquerda, depois raiz, depois direita. Produz chaves em ordem crescente em uma BST. |
| Pós-ordem | Visita sub-árvore esquerda, depois direita, depois raiz. |
| Lixo | Sequência de bytes aleatórios anexada ao texto original antes da cifragem, descartada na decifragem. |
| Token | Saída textual da função `cifrar`. Contém percurso, bytes cifrados e metadados de tamanho. |
| Semente | Valor inicial de um gerador pseudoaleatório. Aqui, derivada da chave. |
| CSPRNG | Cryptographically Secure Pseudo-Random Number Generator. `secrets` é CSPRNG; `random` não é. |
| UTF-8 | Codificação de caracteres em bytes, de 1 a 4 bytes por caractere. |

---

## Considerações Finais

O projeto explora a intersecção entre estruturas de dados clássicas e técnicas elementares de cifragem por transposição. A BST balanceada é utilizada como mecanismo de garantia de altura logarítmica, e os percursos fornecem a variação na ordem de leitura dos bytes.

Do ponto de vista de engenharia, os pontos de maior interesse técnico são:

1. **Construção determinística da árvore** a partir de um par `(chave, n)`, sem necessidade de armazenar a árvore no token.
2. **Aproveitamento dos três percursos** clássicos como três permutações distintas, selecionáveis por um único dígito binário no token.
3. **Uso de `secrets` para o lixo e `random` para a chave**, distinguindo deliberadamente o que exige segurança criptográfica do que é apenas determinístico.
4. **Renderização estática consistente** com a árvore efetivamente utilizada, sem recomputação.