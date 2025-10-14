# app.py — Frontend Streamlit para montar A e B (guia planar 1D)
import math
import numpy as np
import pandas as pd
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="Matrizes A e B (modal 1D)", layout="centered")

st.title("Matrizes A e B — Análise Modal 1D")
st.caption("Etapa 1 (somente A e B) • Generalizado para n camadas")

with st.sidebar:
    st.header("Parâmetros")
    n_camadas = st.number_input("Número de camadas (≥2)", min_value=2, value=3, step=1)
    st.markdown("**Informe largura e índice n para cada camada** (mesmas unidades que λ).")
    larguras, indices_n = [], []
    for i in range(n_camadas):
        c1, c2 = st.columns(2)
        with c1:
            L = st.number_input(f"Largura camada {i+1}", min_value=1e-12, value=1.0, step=0.1, format="%.6f", key=f"L{i}")
        with c2:
            n = st.number_input(f"n camada {i+1}", min_value=1e-12,
                                value=3.55 if (i==0 or i==n_camadas-1) else 3.60,
                                step=0.01, format="%.6f", key=f"n{i}")
        larguras.append(L); indices_n.append(n)

    Np   = st.number_input("Np (nº de pontos, ≥3)", min_value=3, value=101, step=1)
    lamb = st.number_input("λ (compr. de onda)", min_value=1e-12, value=1.0, step=0.1, format="%.6f")

    montar = st.button("Montar A e B")

def montar_AB(larguras, indices_n, Np, lamb):
    L_total = float(sum(larguras))
    dx = L_total / (Np - 1)
    k0 = 2.0 * math.pi / lamb
    x = np.linspace(0.0, L_total, Np)

    limites = np.concatenate(([0.0], np.cumsum(larguras)))
    n_x = np.empty(Np, dtype=float)
    for j, xj in enumerate(x):
        if j == Np - 1:
            c = len(indices_n)
        else:
            for c in range(1, len(indices_n) + 1):
                if limites[c-1] <= xj < limites[c]:
                    break
        n_x[j] = indices_n[c-1]

    D2 = np.zeros((Np, Np), dtype=float)
    idx = np.arange(Np)
    D2[idx, idx] = -2.0
    if Np > 1:
        D2[idx[1:], idx[:-1]] = 1.0
        D2[idx[:-1], idx[1:]] = 1.0
    D2 /= (dx ** 2)

    A = D2 + (k0 ** 2) * np.diag(n_x ** 2)
    B = (k0 ** 2) * np.eye(Np)
    return A, B, x, n_x, dx, k0, L_total

if montar:
    try:
        A, B, x, n_x, dx, k0, L_total = montar_AB(larguras, indices_n, Np, lamb)

        st.subheader("Resumo / Checks")
        c1, c2, c3 = st.columns(3)
        c1.metric("n_camadas", len(larguras))
        c2.metric("Np", Np)
        c3.metric("L_total", f"{L_total:.6g}")

        c4, c5, c6 = st.columns(3)
        c4.metric("Δx", f"{dx:.6g}")
        c5.metric("k0", f"{k0:.6g}")
        c6.metric("k0²", f"{k0**2:.6g}")

        mid = Np // 2
        st.markdown("**Amostras (para conferir no papel):**")
        df_checks = pd.DataFrame({
            "Elemento": [ "A[0,0]", "A[0,1]", "A[1,0]", f"A[{mid},{mid}]", "B[0,0]", f"B[{Np-1},{Np-1}]" ],
            "Valor":    [ A[0,0], A[0,1] if Np>1 else np.nan, A[1,0] if Np>1 else np.nan,
                          A[mid,mid], B[0,0], B[Np-1,Np-1] ]
        })
        st.dataframe(df_checks, use_container_width=True)

        st.markdown("**Prévia das matrizes (10×10 do canto superior esquerdo):**")
        def preview(M):
            s = min(10, M.shape[0]); return pd.DataFrame(M[:s, :s])
        with st.expander("Prévia A (10×10)"): st.dataframe(preview(A))
        with st.expander("Prévia B (10×10)"): st.dataframe(preview(B))

        # Downloads (.npy)
        bA, bB = BytesIO(), BytesIO()
        np.save(bA, A); bA.seek(0)
        np.save(bB, B); bB.seek(0)
        st.download_button("Baixar A (npy)", data=bA, file_name="A.npy")
        st.download_button("Baixar B (npy)", data=bB, file_name="B.npy")

        st.markdown("**Primeiros 12 valores de n(x)²:**")
        st.write(np.round((n_x[:12])**2, 6))
    except Exception as e:
        st.error(f"Erro ao montar as matrizes: {e}")
else:
    st.info("Ajuste os parâmetros na barra lateral e clique **Montar A e B**.")
