# app.py — Análise modal TE 1D (FDM) em Streamlit
#
# Versão alinhada com a aula de 06/11/2025 do Prof. Andres Pablo López Barbero:
# - Pré-processamento: entrada de dados e montagem das matrizes A e B
# - Processamento: solução do problema generalizado A v = λ B v usando eig
# - Pós-processamento: extração de n_eff, filtragem entre n_min e n_max
#   e visualização dos modos físicos.
#
# Observação (registro para o professor):
# Na aula de 06/11/2025 o senhor enfatizou:
#  • Usar eig(A,B) para obter autovalores/autovetores (λ = n_eff^2);
#  • Fazer a raiz quadrada de λ para obter n_eff;
#  • Filtrar os n_eff em um intervalo físico (ex.: 3.55 a 3.60),
#    pois os demais autovalores podem ser complexos ou não-físicos;
#  • Para o momento, focar em um único comprimento de onda (um ponto),
#    deixando o diagrama de dispersão (varrer λ) para uma etapa posterior.
# Este app implementa exatamente essa primeira etapa e segue essas decisões.

import numpy as np
import streamlit as st

try:
    from scipy.linalg import eigh  # versão simétrica de eig(A,B)
    SCIPY_OK = True
except Exception:
    SCIPY_OK = False

# --------------------------------------------------------------------
# Funções numéricas
# --------------------------------------------------------------------


def montar_malha_e_indice(Np: int, t_layers, n_layers):
    """
    Monta a malha 1D em x e o perfil de índice n(x) em degraus.

    Parâmetros
    ----------
    Np       : número de pontos da malha
    t_layers : lista/array com espessuras de cada camada [µm]
    n_layers : lista/array com índices de refração de cada camada

    Retorna
    -------
    x   : coordenadas [µm]
    n_x : perfil n(x) amostrado em Np pontos
    dx  : passo de malha [µm]
    Lx  : comprimento total [µm]
    """
    t_layers = np.array(t_layers, dtype=float)
    n_layers = np.array(n_layers, dtype=float)

    Lx = float(np.sum(t_layers))
    x = np.linspace(-Lx / 2, Lx / 2, Np)
    dx = x[1] - x[0]

    # Constrói n(x) como degraus simples: divide o intervalo em
    # segmentos proporcionais às espessuras.
    edges = np.concatenate(([0.0], np.cumsum(t_layers)))  # em [0, Lx]
    x_shift = x + Lx / 2  # leva [-Lx/2, Lx/2] -> [0, Lx]

    n_x = np.zeros_like(x_shift)
    for i in range(len(t_layers)):
        mask = (x_shift >= edges[i]) & (x_shift <= edges[i + 1] + 1e-12)
        n_x[mask] = n_layers[i]

    return x, n_x, dx, Lx


def montar_matrizes_A_B(Np: int, x, n_x, dx, lam_um: float):
    """
    Monta as matrizes densas A e B como no script MATLAB:

        D2p  = tridiag(-2, 1, 1) / dx^2
        k0   = 2*pi/lambda
        k2dx = diag((k0*n(x))^2)
        A    = D2p + k2dx
        B    = k0^2 * I

    Retorna A, B, k0, k2vec (vetor (k0*n(x))^2).
    """
    c = 1.0 / dx**2
    main = (-2.0 * c) * np.ones(Np)
    off = (1.0 * c) * np.ones(Np - 1)
    D2p = (
        np.diag(main, 0)
        + np.diag(off, 1)
        + np.diag(off, -1)
    )

    k0 = 2.0 * np.pi / lam_um
    k2vec = (k0 * n_x) ** 2
    k2dx = np.diag(k2vec)

    A = D2p + k2dx
    B = (k0**2) * np.eye(Np)

    return A, B, k0, k2vec


def resolver_modal(A, B):
    """
    Resolve A v = λ B v e devolve:

    neff   : array com n_eff (ordenado DECRESCENTE)
    neff2  : n_eff^2 correspondente
    V_sort : matriz cujas colunas são os autovetores associados.
    """
    if not SCIPY_OK:
        raise RuntimeError(
            "SciPy não disponível. Instale scipy para resolver o problema de autovalores."
        )

    # eigh(A,B) -> autovalores λ em ordem crescente,
    # autovetores nas colunas de V.
    w, V_raw = eigh(A, B)

    neff2 = np.real(w)          # n_eff^2
    neff2[neff2 < 0] = np.nan   # descarta negativos

    neff = np.sqrt(neff2)       # n_eff

    # ordena por n_eff decrescente (modo fundamental primeiro)
    idx_sort = np.argsort(neff)[::-1]
    neff_sorted = neff[idx_sort]
    neff2_sorted = neff2[idx_sort]
    V_sort = V_raw[:, idx_sort]

    # normalização simples: |E|max = 1
    for m in range(V_sort.shape[1]):
        vmax = np.max(np.abs(V_sort[:, m]))
        if vmax > 0:
            V_sort[:, m] /= vmax

    return neff_sorted, neff2_sorted, V_sort


def filtrar_intervalo(neff, neff2, V, n_min, n_max):
    """
    Filtra os modos cujo n_eff esteja entre n_min e n_max.
    """
    mask = (neff >= n_min) & (neff <= n_max)
    return neff[mask], neff2[mask], V[:, mask]


# --------------------------------------------------------------------
# Interface Streamlit
# --------------------------------------------------------------------


st.set_page_config(
    page_title="Modal TE 1D (FDM) — A·v = λ·B·v",
    layout="wide",
)

st.title("Análise Modal TE 1D (FDM) — A·v = λ·B·v")

with st.expander("📌 Contexto da aula de 06/11/2025", expanded=False):
    st.markdown(
        """
**Registro para o professor**

Na aula de **06/11/2025**, combinamos que esta primeira versão do código em Python
deveria:

1. **Montar as matrizes densas A e B** a partir dos dados de entrada do guia
   (camadas, índices e malha 1D);
2. **Resolver o problema de autovalor generalizado** `A·v = λ·B·v` usando
   uma rotina equivalente ao `eig(A,B)` do MATLAB;
3. **Extrair os autovalores físicos** \(n_\\text{eff}^2\), tirar a raiz quadrada
   para obter \(n_\\text{eff}\) e
4. **Filtrar os modos** em um intervalo escolhido de \(n_\\text{eff}\),
   por exemplo entre **3.55** e **3.60**, como discutido em aula.

Esta aplicação faz exatamente essa etapa de **Processamento** (para um único λ),
deixando o diagrama de dispersão (varrer λ) para uma fase posterior.
"""
    )

st.sidebar.header("⚙️ Pré-processamento — Parâmetros de entrada")

# Valores padrão = exemplo do script MATLAB de referência
lam_um = st.sidebar.number_input(
    "Comprimento de onda λ [µm]",
    min_value=0.1,
    max_value=5.0,
    value=1.0,
    step=0.05,
)

Np = st.sidebar.number_input(
    "Número de pontos na malha (Np)",
    min_value=100,
    max_value=5000,
    value=1000,
    step=100,
)

st.sidebar.markdown("#### Camadas do guia (exemplo 3 camadas)")

n1 = st.sidebar.number_input("n₁ (camada 1 - cladding)", value=3.55, step=0.01)
t1 = st.sidebar.number_input("t₁ [µm]", value=50.0, step=1.0)

n2 = st.sidebar.number_input("n₂ (camada 2 - núcleo)", value=3.60, step=0.01)
t2 = st.sidebar.number_input("t₂ [µm]", value=1.0, step=0.1)

n3 = st.sidebar.number_input("n₃ (camada 3 - cladding)", value=3.55, step=0.01)
t3 = st.sidebar.number_input("t₃ [µm]", value=50.0, step=1.0)

st.sidebar.markdown("#### Intervalo de filtragem para nₑff")

neff_min = st.sidebar.number_input(
    "nₑff mínimo", value=3.55, step=0.01, format="%.4f"
)
neff_max = st.sidebar.number_input(
    "nₑff máximo", value=3.60, step=0.01, format="%.4f"
)

st.sidebar.markdown("----")
run_btn = st.sidebar.button("▶️ Calcular modos (Processamento)")


if not SCIPY_OK:
    st.error(
        "SciPy não está disponível. Instale o pacote `scipy` "
        "para resolver o problema de autovalores: `pip install scipy`."
    )

if run_btn and SCIPY_OK:
    # --------------------------------------------------------------
    # PRÉ-PROCESSAMENTO: malha e perfil n(x)
    # --------------------------------------------------------------
    n_layers = [n1, n2, n3]
    t_layers = [t1, t2, t3]

    x, n_x, dx, Lx = montar_malha_e_indice(Np, t_layers, n_layers)

    st.subheader("Pré-processamento")
    st.write(
        f"λ = {lam_um:.3f} µm | Np = {Np} | Lx = {Lx:.2f} µm | dx = {dx:.4f} µm"
    )

    # --------------------------------------------------------------
    # PROCESSAMENTO: montagem de A, B e solução do autoproblema
    # --------------------------------------------------------------
    A, B, k0, k2vec = montar_matrizes_A_B(Np, x, n_x, dx, lam_um)

    st.subheader("Processamento — Autovalores e Autovetores")
    st.write(
        "Resolvendo o problema generalizado **A·v = λ·B·v** "
        "com `λ = n_eff²` via `scipy.linalg.eigh(A, B)`."
    )

    neff_all, neff2_all, V_all = resolver_modal(A, B)

    # --------------------------------------------------------------
    # PÓS-PROCESSAMENTO: filtragem no intervalo [neff_min, neff_max]
    # --------------------------------------------------------------
    neff_fil, neff2_fil, V_fil = filtrar_intervalo(
        neff_all, neff2_all, V_all, neff_min, neff_max
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Perfil de índice n(x)")
        import matplotlib.pyplot as plt

        fig1, ax1 = plt.subplots()
        ax1.plot(x, n_x)
        ax1.set_xlabel("x [µm]")
        ax1.set_ylabel("n(x)")
        ax1.grid(True)
        st.pyplot(fig1)

    with col2:
        st.markdown("#### Perfil de (k₀·n(x))²")
        fig2, ax2 = plt.subplots()
        ax2.plot(x, k2vec)
        ax2.set_xlabel("x [µm]")
        ax2.set_ylabel("(k₀ n(x))² [µm⁻²]")
        ax2.grid(True)
        st.pyplot(fig2)

    st.subheader("Autovalores nₑff (todos)")

    # tabela resumida com todos os n_eff
    import pandas as pd

    df_all = pd.DataFrame(
        {
            "modo": np.arange(1, len(neff_all) + 1),
            "n_eff": neff_all,
            "n_eff²": neff2_all,
        }
    )
    st.dataframe(df_all.style.format({"n_eff": "{:.6f}", "n_eff²": "{:.6f}"}))

    st.subheader(
        f"Modos físicos filtrados — {neff_min:.4f} ≤ nₑff ≤ {neff_max:.4f}"
    )

    if len(neff_fil) == 0:
        st.warning(
            "Nenhum autovalor caiu dentro do intervalo de filtragem. "
            "Ajuste nₑff mínimo/máximo e tente novamente."
        )
    else:
        df_fil = pd.DataFrame(
            {
                "modo_filtrado": np.arange(1, len(neff_fil) + 1),
                "n_eff": neff_fil,
                "n_eff²": neff2_fil,
            }
        )
        st.dataframe(df_fil.style.format({"n_eff": "{:.6f}", "n_eff²": "{:.6f}"}))

        # Plota perfis de campo dos dois primeiros modos filtrados
        st.markdown("#### Perfis de campo |E(x)| dos modos filtrados")

        n_plot = min(2, V_fil.shape[1])  # até 2 modos
        fig3, ax3 = plt.subplots()
        for m in range(n_plot):
            ax3.plot(x, np.real(V_fil[:, m]), label=f"Modo {m+1}")
        ax3.set_xlabel("x [µm]")
        ax3.set_ylabel("Re{E(x)} (normalizado)")
        ax3.grid(True)
        ax3.legend()
        st.pyplot(fig3)

else:
    st.info(
        "Defina os parâmetros no menu lateral e clique em "
        "**'Calcular modos (Processamento)'** para executar."
    )
