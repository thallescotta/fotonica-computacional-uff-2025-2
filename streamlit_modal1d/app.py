# app.py
# -------------------------------------------------------------------
# Análise Modal TE 1D (FDM) — A·v = λ·B·v
#
# Este app segue a organização que o professor pediu na aula de
# 06/11/2025: pré-processamento, processamento e pós-processamento.
#
# Nesta versão (entrega parcial 1/2 e 2/3) estão implementados:
#  - Pré-processamento:
#       * Entrada de parâmetros do guia planar
#       * Montagem das matrizes A e B (B = k0^2 * I)
#       * Perfis n(x) e (k0*n(x))^2
#  - Processamento:
#       * Resolução do problema A·v = λ·B·v usando o análogo de eig(A,B)
#         do MATLAB, em Python:
#             A·v = λ·(k0^2 I)·v  =>  (A / k0^2)·v = λ·v
#         Logo usamos numpy.linalg.eigh(A/k0^2) para obter λ = n_eff^2
#         e depois tiramos a raiz quadrada para obter n_eff, como
#         discutido em 06/11/2025.
#       * Filtro de modos por intervalo de n_eff
#       * Gráficos dos perfis de campo E(x) para até dois modos
#
#  - Pós-processamento:
#       * Ainda NÃO implementado de propósito, como combinado.
#         Os blocos de código e comentários “TODO” abaixo indicam
#         onde serão incluídos, futuramente, os gráficos adicionais
#         (por exemplo, diagrama de dispersão em função de λ).
# -------------------------------------------------------------------

import math
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# ================== CONFIGURAÇÃO DA PÁGINA ==========================
st.set_page_config(
    page_title="Análise Modal TE 1D (FDM) — Matrizes A e B",
    layout="wide",
)

# ======= ESTILO GLOBAL (tema escuro simples, mantendo cabeçalho) =====
st.markdown(
    """
    <style>
      body {
        background-color: #0e1117;
      }
      .main {
        background-color: #0e1117;
        color: #e0e0e0;
      }
      section[data-testid="stSidebar"] {
        background-color: #111827;
        color: #e5e7eb;
      }
      section[data-testid="stSidebar"] h1,
      section[data-testid="stSidebar"] h2,
      section[data-testid="stSidebar"] h3 {
        color: #e5e7eb;
      }
      .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ====================== SIDEBAR: PRÉ-PROCESSAMENTO ===================
with st.sidebar:
    st.header("⚙️ Pré-processamento — Parâmetros de entrada")

    st.markdown("Comprimento de onda e malha 1D:")
    lambda_um = st.number_input(
        "Comprimento de onda λ [µm]", value=1.00, format="%.2f"
    )
    Np = st.number_input(
        "Número de pontos na malha (Np)",
        min_value=100,
        max_value=5000,
        value=1000,
        step=100,
    )

    st.markdown("---")
    st.markdown("Camadas do guia (exemplo 3 camadas)")

    # Camada 1 (cladding)
    st.markdown("**n₁ (camada 1 – cladding)**")
    n1 = st.number_input("n₁", value=3.55, format="%.3f")
    t1 = st.number_input("t₁ [µm]", value=50.0, format="%.2f")

    # Camada 2 (núcleo)
    st.markdown("**n₂ (camada 2 – núcleo)**")
    n2 = st.number_input("n₂", value=3.60, format="%.3f")
    t2 = st.number_input("t₂ [µm]", value=1.0, format="%.2f")

    # Camada 3 (cladding)
    st.markdown("**n₃ (camada 3 – cladding)**")
    n3 = st.number_input("n₃", value=3.55, format="%.3f")
    t3 = st.number_input("t₃ [µm]", value=50.0, format="%.2f")

    st.markdown("---")
    st.markdown("Intervalo de filtragem para nₑff:")

    neff_min = st.number_input(
        "nₑff mínimo", value=3.5500, format="%.4f"
    )
    neff_max = st.number_input(
        "nₑff máximo", value=3.6000, format="%.4f"
    )

    st.markdown("---")
    calcular = st.button("▶️ Calcular modos (Processamento)")

# ====================== CABEÇALHO DA PÁGINA =========================
st.title("Análise Modal TE 1D (FDM) — A·v = λ·B·v")

with st.expander("📌 Contexto da aula de 06/11/2025", expanded=False):
    st.markdown(
        """
        Na aula de **06/11/2025**, o professor reforçou que:
        
        - O programa deve ser organizado em **três etapas**:
          **pré-processamento**, **processamento** e **pós-processamento**.
        - Na etapa de **processamento**, é preciso resolver o problema de
          **autovalores generalizado**:
          
          \\[
          A \\cdot v = \\lambda \\cdot B \\cdot v
          \\]
          
          utilizando a função `eig(A,B)` no MATLAB, obtendo:
          
          - matriz `V` (autovetores → perfis de campo elétrico \\(E(x)\\))
          - matriz `D` (autovalores)
        - A matriz `D` contém **nₑff²**. Para chegar ao índice efetivo,
          é necessário tirar a **raiz quadrada**:
          \\(n_{\\text{eff}} = \\sqrt{D}\\).
        - Depois, deve-se **filtrar** os modos em um intervalo de
          **nₑff** de interesse (por exemplo, próximo ao índice do núcleo).
        - Para cada modo selecionado, é feito o gráfico da coluna do
          autovetor \\(E(x)\\).
        
        Nesta versão do app, eu segui essas orientações e **concordo**
        com essa divisão e com a forma de obter \\(n_{\\text{eff}}\\),
        reproduzindo em Python o comportamento da `eig(A,B)` do MATLAB.
        """
    )

st.info(
    "Defina os parâmetros no menu lateral e clique em "
    "**'Calcular modos (Processamento)'** para executar a etapa "
    "de autovalores/autovetores.\n\n"
    "Observação: como B = k₀²·I, não é necessário SciPy; usamos "
    "`numpy.linalg.eigh(A / k₀²)` para obter nₑff²."
)

# ===================== PRÉ-PROCESSAMENTO ============================
# 1) Vetores de índices e espessuras
n_layers = np.array([n1, n2, n3], dtype=float)
t_layers = np.array([t1, t2, t3], dtype=float)

if np.any(t_layers <= 0):
    st.error("Todas as espessuras das camadas devem ser positivas.")
    st.stop()

# 2) Malha espacial x
Lx = float(np.sum(t_layers))          # largura total [µm]
x = np.linspace(0.0, Lx, int(Np))     # vetor 1D de posições
dx = x[1] - x[0]

# 3) Atribuição de n(x) por faixas de espessura
edges = np.concatenate(([0.0], np.cumsum(t_layers)))  # [0, t1, t1+t2, ...]
# digitize devolve índices 1..len(edges) para bins; ajustamos para 0..N-1
idx_bins = np.digitize(x, edges, right=True)

# Correções de borda (equivalente ao que é feito no MATLAB)
idx_bins[idx_bins == 0] = 1
idx_bins[idx_bins > len(n_layers)] = len(n_layers)
idx_bins = idx_bins - 1  # agora entre 0 e len(n_layers)-1

n_x = n_layers[idx_bins]  # perfil n(x)

# 4) Operador de segunda derivada (diferenças finitas tridiagonais)
c = 1.0 / dx**2
main = (-2.0 * c) * np.ones(Np)
off = (1.0 * c) * np.ones(Np - 1)

D2p = (
    np.diag(main, k=0)
    + np.diag(off, k=1)
    + np.diag(off, k=-1)
)

# 5) Termo óptico k0² n(x)² e matrizes A e B
k0 = 2.0 * math.pi / lambda_um      # [1/µm]
k0_sq = k0**2

k2vec = (k0 * n_x)**2               # (k0*n(x))²
k2dx = np.diag(k2vec)

A = D2p + k2dx                      # matriz A densa
# B = k0^2 * I (não precisamos criar explicitamente, pois vamos
# dividir A por k0^2 no problema padrão de autovalores)

# ===================== GRÁFICOS DE PRÉ-PROCESSAMENTO ===============
st.subheader("📊 Perfis de pré-processamento")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Perfil do índice n(x)**")
    fig_n, ax_n = plt.subplots()
    ax_n.plot(x, n_x, linewidth=1.5)
    ax_n.set_xlabel("x [µm]")
    ax_n.set_ylabel("n(x)")
    ax_n.grid(True)
    ax_n.set_title("n(x)")
    st.pyplot(fig_n)

with col2:
    st.markdown("**Perfil de (k₀·n(x))²**")
    fig_k2, ax_k2 = plt.subplots()
    ax_k2.plot(x, k2vec, linewidth=1.5)
    ax_k2.set_xlabel("x [µm]")
    ax_k2.set_ylabel("(k₀·n(x))² [µm⁻²]")
    ax_k2.grid(True)
    ax_k2.set_title("(k₀·n(x))²")
    st.pyplot(fig_k2)

# ====================== PROCESSAMENTO: AUTOVALORES ==================
st.subheader("🧮 Processamento — Cálculo de autovalores e autovetores")

st.markdown(
    f"""
    - Tamanho da malha: **Np = {Np}** pontos  
    - Largura total: **Lx = {Lx:.2f} µm**  
    - Passo espacial: **dx = {dx:.4f} µm**  
    - k₀² = **{k0_sq:.4f} µm⁻²**
    """
)

if calcular:
    st.success("Iniciando cálculo de autovalores/autovetores (A·v = λ·B·v)...")

    # Problema generalizado A·v = λ·B·v com B = k0²·I
    # => (A / k0²)·v = λ·v   com λ = n_eff²
    A_tilde = A / k0_sq

    # eigh: para matrizes hermitianas/simétricas (como nosso caso)
    eigvals, eigvecs = np.linalg.eigh(A_tilde)

    # λ = n_eff²  (parte real e eliminação de negativos numéricos)
    neff2 = np.real(eigvals)
    neff2[neff2 < 0] = 0.0
    neff = np.sqrt(neff2)

    # Ordena por n_eff decrescente
    idx_sort = np.argsort(neff)[::-1]
    neff_sorted = neff[idx_sort]
    eigvecs_sorted = eigvecs[:, idx_sort]

    # Normaliza cada autovetor para |E|max = 1
    for m in range(eigvecs_sorted.shape[1]):
        vmax = np.max(np.abs(eigvecs_sorted[:, m]))
        if vmax > 0:
            eigvecs_sorted[:, m] /= vmax

    # Filtragem por intervalo de n_eff (como professor sugeriu)
    mask = (neff_sorted >= neff_min) & (neff_sorted <= neff_max)
    neff_filtrado = neff_sorted[mask]
    modos_filtrados = eigvecs_sorted[:, mask]

    st.markdown("**Lista de nₑff (ordenados, antes da filtragem):**")

    df_neff = pd.DataFrame(
        {
            "índice (coluna)": np.arange(len(neff_sorted)),
            "nₑff": neff_sorted,
        }
    )
    st.dataframe(
        df_neff.style.format({"nₑff": "{:.6f}"}),
        use_container_width=True,
        height=250,
    )

    if neff_filtrado.size == 0:
        st.warning(
            "Nenhum modo encontrado no intervalo de nₑff especificado. "
            "Ajuste os valores de nₑff mínimo e máximo na barra lateral."
        )
    else:
        st.markdown(
            f"**Modos dentro do intervalo:** {neff_min:.4f} ≤ nₑff ≤ {neff_max:.4f}  "
            f"→ {neff_filtrado.size} modos encontrados."
        )

        # Gráfico dos perfis de campo E(x) dos dois primeiros modos filtrados
        st.markdown("**Perfis de campo E(x) dos modos filtrados (até 2 modos):**")
        fig_modes, ax_modes = plt.subplots()

        num_to_plot = min(2, modos_filtrados.shape[1])
        for j in range(num_to_plot):
            ax_modes.plot(
                x,
                modos_filtrados[:, j],
                label=f"Modo {j} (nₑff = {neff_filtrado[j]:.6f})",
                linewidth=1.5,
            )

        ax_modes.set_xlabel("x [µm]")
        ax_modes.set_ylabel("E(x) (normalizado)")
        ax_modes.grid(True)
        ax_modes.legend()
        ax_modes.set_title("Perfis de campo E(x) dos modos (filtrados)")
        st.pyplot(fig_modes)

        st.caption(
            "Obs.: Para esta entrega, estamos focando na visualização de até dois modos "
            "como discutido em 06/11/2025 (modo fundamental e um modo de ordem superior)."
        )

# =================== PÓS-PROCESSAMENTO (A IMPLEMENTAR) ===============
st.subheader("📈 Pós-processamento (ainda não implementado)")

st.markdown(
    """
    Nesta etapa futura, serão incluídos, por exemplo:
    
    - **Diagramas de dispersão** (nₑff em função do comprimento de onda λ).
    - Gráficos adicionais de comparação entre modos.
    - Outras análises numéricas que o professor vier a solicitar.
    
    ```python
    # TODO (pós-processamento):
    # for lambda_um in faixa_de_lambda:
    #     1) Repetir pré-processamento (montar A e B)
    #     2) Recalcular n_eff
    #     3) Guardar n_eff para cada modo
    #     4) Montar diagrama de dispersão (n_eff vs lambda)
    ```
    """
)