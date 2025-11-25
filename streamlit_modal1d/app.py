# app.py — App Streamlit (único arquivo) para montar A e B (guia planar)
# Atualizado com as orientações do professor na aula de 06/11/2025:
# - Divisão em 3 partes: pré-processamento (matrizes A e B),
#   processamento (autovalores/autovetores, análogo a eig(A,B) do MATLAB)
#   e pós-processamento (visualização dos modos).
# - Filtro manual dos n_eff entre dois índices (por ex. 3.55 e 3.60).
# Nesta versão eu (Thalles) implementei a Etapa 1 completa
# (montagem de A e B) + início da Etapa 2 (cálculo dos modos e filtragem).

import math
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Matrizes A, B e Modos (Guia Planar)", layout="wide")

# ======= ESTILO (tema escuro + área principal mais larga + sidebar azul) =======
st.markdown(
    """
    <style>
      /* App escuro */
      .stApp { background: #000000; color: #e5e7eb; }
      h1, h2, h3 { line-height: 1.2; color: #e5e7eb; }

      /* Sidebar azul */
      section[data-testid="stSidebar"] > div {
        background: #020617;
        border-right: 1px solid #1f2937;
      }
      section[data-testid="stSidebar"] h1,
      section[data-testid="stSidebar"] h2,
      section[data-testid="stSidebar"] h3 {
        color: #e5e7eb;
      }

      /* Ajuste de largura do container principal */
      .main .block-container {
        max-width: 1200px;
        padding-top: 1rem;
      }

      /* Botão principal */
      .stButton > button{
        background: #2563eb;
        color: #ffffff;
        border: 1px solid #1e40af;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        font-weight: 700;
        box-shadow: 0 4px 14px rgba(37,99,235,0.25);
      }
      .stButton > button:hover{ background: #1d4ed8; border-color: #1e3a8a; }

      /* Boxes/expanders */
      .stAlert, .stDataFrame, .st-expander {
        border-radius: 12px !important;
        border: 1px solid #1f2937;
      }

      /* Bloco de código (pseudocódigo) compacto */
      div.stCode{
        background:#0f1a2b;
        border:1px solid #1f2937;
        border-radius:12px;
        padding:8px 10px;
      }
      div.stCode pre{ margin:0; }
      div.stCode code{
        font-size:12px;
        line-height:1.2;
        color:#e5e7eb;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ======= CAPA (logo + seus dados) =======
LOGO_URL = "https://raw.githubusercontent.com/thallescotta/logo-ppgio-vetorizado/main/SVG-PPGIO_invert_preto_para_branco.png"

st.markdown(
    f"""
    <div style="display:flex; gap:24px; align-items:center; margin:10px 0 12px 0;">
      <img src="{LOGO_URL}" alt="Logo PPGIO" style="width:320px; max-width:40vw;" />
      <div>
        <h1 style="margin:0;">Matrizes A, B e Modos - Guia Planar</h1>
        <p style="margin:6px 0 0 0; opacity:.9;">
          <strong>Thalles Cotta Fontainha</strong>, <strong>PPGIO Matrícula:</strong> 2410091DIOAMA
        </p>
        <p style="margin:0; opacity:.9;">
          <em>"Fotonica Analise Modal e BPM V2.pdf"</em> recebido em 11/09/2025
        </p>
        <p style="margin:0; opacity:.9;">
          Orientações de implementação discutidas em aula no dia <strong>06/11/2025</strong>
          (divisão em pré-processamento, processamento e pós-processamento, uso de autovalores tipo eig(A,B) e filtragem de n_eff).
        </p>
        <p style="margin:0; opacity:.9;">
          Disciplina: <strong>Fotônica Computacional (TCE11209 - UFF)</strong> •
          Professor: <strong>Andres Pablo Lopez Barbero</strong>
        </p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ======= SIDEBAR (Parâmetros mínimos que o professor pediu) =======
with st.sidebar:
    st.header("Parâmetros")

    # nº de camadas
    n_camadas = st.number_input("Número de camadas (≥2)", min_value=2, value=3, step=1)

    st.markdown("**Informe largura e índice n para cada camada** (mesmas unidades que λ).")

    larguras = []
    indices_n = []

    for i in range(n_camadas):
        c1, c2 = st.columns(2)
        key_L = f"L{i}"
        key_n = f"n{i}"

        # Valores padrão inspirados no exemplo do professor:
        # 3 camadas: 50 | 1 | 50 e 3.55 | 3.60 | 3.55
        if n_camadas == 3:
            if i == 0 or i == 2:
                default_L = 50.0
                default_n = 3.55
            else:
                default_L = 1.0
                default_n = 3.60
        else:
            # Outras quantidades: bordas com valor "cladding" e interior "núcleo"
            if i == 0 or i == n_camadas - 1:
                default_L = 50.0
                default_n = 3.55
            else:
                default_L = 1.0
                default_n = 3.60

        L = c1.number_input(
            f"Largura camada {i+1}",
            min_value=0.0,
            value=float(default_L),
            step=0.1,
            format="%.6g",
            key=key_L,
        )
        n_val = c2.number_input(
            f"n da camada {i+1}",
            min_value=0.0,
            value=float(default_n),
            step=0.001,
            format="%.6g",
            key=key_n,
        )

        larguras.append(L)
        indices_n.append(n_val)

    # Discretização e comprimento de onda
    Np = st.number_input("Np (nº de pontos, ≥3)", min_value=3, value=101, step=1)
    lamb = st.number_input(
        "λ (comprimento de onda)",
        min_value=1e-12,
        value=1.00,
        step=0.01,
        format="%.2f",
    )

    st.markdown("---")
    st.markdown(
        "**Janela de filtragem de n_eff**  \n"
        "(conforme combinado na aula de 06/11/2025: filtrar entre os índices das camadas)"
    )

    if len(indices_n) > 0:
        n_min_default = float(min(indices_n))
        n_max_default = float(max(indices_n))
    else:
        n_min_default = 0.0
        n_max_default = 1.0

    neff_min = st.number_input(
        "n_eff mínimo (limite inferior da janela)",
        value=n_min_default,
        step=0.001,
        format="%.6f",
    )
    neff_max = st.number_input(
        "n_eff máximo (limite superior da janela)",
        value=n_max_default,
        step=0.001,
        format="%.6f",
    )

    st.markdown(
        "<small>Obs.: em muitos exemplos de validação, usa-se "
        "n_eff ∈ [n_cladding, n_core], por ex. [3.55, 3.60].</small>",
        unsafe_allow_html=True,
    )

    montar = st.button("Montar A, B e calcular modos", use_container_width=True)

# ======= DESCRIÇÃO + PSEUDOCÓDIGO (ETAPA 1 + visão da ETAPA 2) =======
st.markdown(
    "#### Etapa 1: montar as matrizes A e B  \n"
    "(Construir as matrizes A e B para o guia planar com camadas arbitrárias, "
    "a partir dos dados de entrada.)"
)

pseudo = """\
# Entradas do usuário:
# n_camadas  -> número de camadas do guia
# largura[i] -> largura da i-ésima camada (mesmas unidades de λ)
# n[i]       -> índice de refração da i-ésima camada
# Np         -> número de pontos da discretização (≥3)
# λ (lambda) -> comprimento de onda
# i, j       -> índices da malha (0..Np-1) para linhas/colunas das matrizes
# x_i, x_j   -> posições espaciais correspondentes (x_i = i·Δx, x_j = j·Δx)

L_total = sum(largura)             # largura total do guia
Δx      = L_total/(Np-1)           # passo da malha 1D
k0      = 2*π/λ                    # número de onda no vácuo
x       = linspace(0, L_total, Np) # grade uniforme

# Perfil n(x):
limites = [0] + cumsum(largura)    # fronteiras acumuladas das camadas
n_x     = array de tamanho Np

for cada x_j em x:                 # j = 0..Np-1
    encontre c tal que limites[c-1] ≤ x_j < limites[c]
    n_x[j] = n[c]                  # índice de refração da camada c

# Matrizes:
D2      = tridiag(1, -2, 1)/(Δx**2) # operador de 2ª derivada (FDM)
Diag_n2 = diag(n_x**2)              # diagonal com n(x)^2
A       = D2 + (k0**2)*Diag_n2      # matriz do problema generalizado
B       = (k0**2)*I                 # matriz massa (diagonal)

# (Visão da Etapa 2 – Processamento, discutida em 06/11/2025)
# Problema de autovalores generalizado: A·v = λ·B·v
# Como B = k0²·I, o problema é equivalente a:
#   (A / k0²)·v = λ·v,   onde λ = n_eff²
#
# Passos:
# 1) Calcular autovalores e autovetores de M = A / k0²:
#       vals, V = eig(M)              # análogo ao eig(A,B) do MATLAB
# 2) n_eff² = vals (parte real, valores negativos → 0)
# 3) n_eff  = sqrt(n_eff²)
# 4) Ordenar n_eff (por exemplo, em ordem decrescente) e normalizar colunas de V
#    para |E|max = 1.
# 5) Filtrar somente n_eff entre [n_eff_min, n_eff_max] (janela definida pelo usuário).
"""

st.code(pseudo, language="python")

# ======= FUNÇÕES DE CÁLCULO =======
def montar_AB(larguras, indices_n, Np, lamb):
    """
    Pré-processamento: monta as matrizes A e B (densas) e o perfil n(x).
    Implementa o mesmo conceito do código em MATLAB:
    - A = D2 + k0^2 * diag(n(x)^2)
    - B = k0^2 * I
    """
    L_total = float(sum(larguras))
    dx = L_total / (Np - 1)
    k0 = 2.0 * math.pi / float(lamb)
    x = np.linspace(0.0, L_total, Np)

    # Perfil n(x) por faixas (camadas)
    limites = np.concatenate(([0.0], np.cumsum(larguras)))
    n_x = np.empty(Np, dtype=float)

    for j, xj in enumerate(x):
        # Garante que o último ponto caia na última camada
        if j == Np - 1:
            c = len(indices_n)
        else:
            c = len(indices_n)
            for idx_camada in range(1, len(indices_n) + 1):
                if limites[idx_camada - 1] <= xj < limites[idx_camada]:
                    c = idx_camada
                    break
        n_x[j] = indices_n[c - 1]

    # Operador de segunda derivada (diferenças finitas centradas, tridiagonal)
    D2 = np.zeros((Np, Np), dtype=float)
    idx = np.arange(Np)
    D2[idx, idx] = -2.0
    if Np > 1:
        D2[idx[1:], idx[:-1]] = 1.0
        D2[idx[:-1], idx[1:]] = 1.0
    D2 /= dx ** 2

    # Matrizes A e B
    A = D2 + (k0 ** 2) * np.diag(n_x ** 2)
    B = (k0 ** 2) * np.eye(Np)

    return A, B, x, n_x, dx, k0, L_total


def resolver_modos(A, B, k0, x, neff_min, neff_max):
    """
    Processamento: resolve o problema de autovalores equivalente a eig(A,B),
    obtendo n_eff e modos E(x), e aplica a filtragem pela janela [neff_min, neff_max].

    Como B = k0²·I, o problema generalizado A·v = λ·B·v vira:
        (A / k0²)·v = λ·v,   com λ = n_eff².
    """
    # Matriz equivalente ao B^{-1}·A
    M = A / (k0 ** 2)

    # Como M é simétrica real, usamos eigh (autovalores reais, ordenados crescentes)
    eigvals, eigvecs = np.linalg.eigh(M)

    # n_eff² e n_eff
    neff2 = np.maximum(eigvals.real, 0.0)
    neff = np.sqrt(neff2)

    # Ordenar por n_eff em ordem decrescente (módulos mais "importantes" no final do espectro)
    idx_sort = np.argsort(neff)[::-1]
    neff_sorted = neff[idx_sort]
    modos_sorted = eigvecs[:, idx_sort]

    # Normalizar cada modo para |E|max = 1 (como no código MATLAB do colega)
    for m in range(modos_sorted.shape[1]):
        vmax = np.max(np.abs(modos_sorted[:, m]))
        if vmax > 0:
            modos_sorted[:, m] /= vmax

    # Filtragem: somente modos com n_eff dentro da janela
    mascara = (neff_sorted >= neff_min) & (neff_sorted <= neff_max)
    neff_filtrados = neff_sorted[mascara]
    modos_filtrados = modos_sorted[:, mascara] if modos_sorted.shape[1] > 0 else np.empty((len(x), 0))

    return neff_sorted, modos_sorted, neff_filtrados, modos_filtrados


def preview_matrix(M, x, s=10):
    """
    Cria uma submatriz com rótulos i/j e as posições x_i/x_j correspondentes
    para conferir no papel, como o professor sugeriu.
    """
    s = min(s, M.shape[0])
    cols = [f"j={j}  |  x_j={x[j]:.6g}" for j in range(s)]
    idx = [f"i={i}  |  x_i={x[i]:.6g}" for i in range(s)]
    return pd.DataFrame(M[:s, :s], columns=cols, index=idx)


# ======= SAÍDA (PRÉ + PROCESSAMENTO + PÓS) =======
if montar:
    try:
        # ------------------- PRÉ-PROCESSAMENTO -------------------
        A, B, x, n_x, dx, k0, L_total = montar_AB(larguras, indices_n, Np, lamb)

        st.subheader("Resumo da discretização e das matrizes (Pré-processamento)")
        c1, c2, c3 = st.columns(3)
        c1.metric("Número de camadas", len(larguras))
        c2.metric("Np", Np)
        c3.metric("L_total (largura total)", f"{L_total:.6g}")

        c4, c5, c6 = st.columns(3)
        c4.metric("Δx", f"{dx:.6g}")
        c5.metric("λ", f"{lamb:.6g}")
        c6.metric("k0²", f"{k0**2:.6g}")

        # Perfil n(x) resumido
        st.markdown("**Perfil do índice n(x)** (útil para comparar com o slide do exemplo).")
        df_nx = pd.DataFrame({"x [unidades de λ]": x, "n(x)": n_x})
        st.line_chart(df_nx.set_index("x [unidades de λ]"))

        # Amostras de elementos de A e B para conferência no papel
        mid = Np // 2
        st.markdown("**Amostras de A e B (para conferir com o exemplo do livro/slide):**")
        df_checks = pd.DataFrame(
            {
                "Elemento": [
                    "A[0,0]",
                    "A[0,1]",
                    "A[1,0]",
                    f"A[{mid},{mid}]",
                    "B[0,0]",
                    f"B[{Np-1},{Np-1}]",
                ],
                "Valor": [
                    A[0, 0],
                    A[0, 1] if Np > 1 else np.nan,
                    A[1, 0] if Np > 1 else np.nan,
                    A[mid, mid],
                    B[0, 0],
                    B[Np - 1, Np - 1],
                ],
            }
        )
        st.dataframe(df_checks, use_container_width=True)

        # Pré-visualizações das submatrizes
        s = min(10, Np)
        st.markdown(
            "**Pré-visualizações das matrizes A e B**  \n"
            "Linhas = `i` (x_i = i·Δx), colunas = `j` (x_j = j·Δx)."
        )

        st.markdown(f"**Matriz A — submatriz [0:{s}, 0:{s}] (canto superior esquerdo)**")
        with st.expander("Mostrar A (0…s-1, 0…s-1)"):
            st.dataframe(preview_matrix(A, x, s=s), use_container_width=True)

        st.markdown(f"**Matriz B — submatriz [0:{s}, 0:{s}] (canto superior esquerdo)**")
        with st.expander("Mostrar B (0…s-1, 0…s-1)"):
            st.dataframe(preview_matrix(B, x, s=s), use_container_width=True)

        # ------------------- PROCESSAMENTO -------------------
        st.markdown("---")
        st.subheader("Etapa 2: processamento (autovalores/autovetores)")

        st.info(
            "Esta etapa implementa, em Python, o que o professor descreveu na aula de 06/11/2025 "
            "como o uso de `eig(A,B)` no MATLAB:\n\n"
            "- Resolvemos o problema equivalente `(A / k0²)·v = λ·v`, com λ = n_eff².\n"
            "- Calculamos `n_eff`, ordenamos e filtramos apenas os valores dentro da janela "
            "definida `[n_eff_min, n_eff_max]`."
        )

        neff_all, modos_all, neff_filtrados, modos_filtrados = resolver_modos(
            A, B, k0, x, neff_min, neff_max
        )

        df_neff = pd.DataFrame(
            {
                "índice (ordenado)": np.arange(len(neff_all)),
                "n_eff": neff_all,
                "β = k0·n_eff": k0 * neff_all,
            }
        )
        st.markdown("**Todos os autovalores (n_eff)** — ainda contêm soluções não físicas.")
        st.dataframe(df_neff, use_container_width=True)

        # ------------------- PÓS-PROCESSAMENTO (VISUALIZAÇÃO DOS MODOS GUIADOS) -------------------
        st.markdown("---")
        st.subheader("Etapa 3: pós-processamento (modos guiados e campos E(x))")

        if len(neff_filtrados) == 0:
            st.warning(
                "Nenhum n_eff caiu dentro da janela informada "
                f"[{neff_min:.6f}, {neff_max:.6f}]. "
                "Ajuste os valores de filtragem (por exemplo, use os índices das camadas do guia)."
            )
        else:
            df_neff_filt = pd.DataFrame(
                {
                    "modo guiado": np.arange(len(neff_filtrados)),
                    "n_eff (filtrado)": neff_filtrados,
                    "β = k0·n_eff": k0 * neff_filtrados,
                }
            )
            st.markdown("**Modos guiados após filtragem (n_eff_min ≤ n_eff ≤ n_eff_max):**")
            st.dataframe(df_neff_filt, use_container_width=True)

            st.markdown(
                "#### Perfis de campo E(x) normalizados (|E|max = 1)  \n"
                "Esses gráficos correspondem à parte de pós-processamento que o professor "
                "comentou, em que se plota o campo dos modos físicos."
            )

            # Um gráfico por modo guiado filtrado
            for idx_modo in range(modos_filtrados.shape[1]):
                neff_val = neff_filtrados[idx_modo]
                st.markdown(f"**Modo guiado {idx_modo} — n_eff = {neff_val:.6f}**")
                df_plot = pd.DataFrame({"x [unid. de λ]": x, "E(x)": modos_filtrados[:, idx_modo]})
                st.line_chart(df_plot.set_index("x [unid. de λ]"))

    except Exception as e:
        st.error(f"Erro ao montar as matrizes ou calcular os modos: {e}")
