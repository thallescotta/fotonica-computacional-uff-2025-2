# app.py — App Streamlit (único arquivo) para montar A e B (guia planar)
import math
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Matrizes A e B (Guia Planar)", layout="wide")

# ======= ESTILO (fundo branco e área principal mais larga) =======

st.markdown(
    """
    <style>
      /* --- SIDEBAR: azul escuro e contraste --- */
      section[data-testid="stSidebar"]{
        background: #0b1220;              /* azul escuro */
        border-right: 1px solid #0f172a;  /* linha discreta */
      }
      /* textos/labels da sidebar mais legíveis */
      section[data-testid="stSidebar"] * { color: #e5e7eb !important; }
      section[data-testid="stSidebar"] h1,
      section[data-testid="stSidebar"] h2,
      section[data-testid="stSidebar"] h3 { color: #e5e7eb !important; }

      /* inputs dentro da sidebar com fundo azul escuro */
      section[data-testid="stSidebar"] div[data-baseweb="input"] > div{
        background: #111a2b !important;
        color: #e5e7eb !important;
        border-radius: 10px;
        border: 1px solid #1e3a8a;       /* borda azul */
      }
      section[data-testid="stSidebar"] div[data-baseweb="input"] > div:focus-within{
        border-color: #60a5fa;           /* foco azul claro */
        box-shadow: 0 0 0 1px #60a5fa inset;
      }

      /* botão na sidebar com boa visibilidade no tema escuro */
      section[data-testid="stSidebar"] .stButton > button{
        background: #2563eb;
        color: #ffffff;
        border: 1px solid #1e40af;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        font-weight: 700;
        box-shadow: 0 4px 14px rgba(37,99,235,0.25);
      }
      section[data-testid="stSidebar"] .stButton > button:hover{
        background: #1d4ed8;
        border-color: #1e3a8a;
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
      <img src="{LOGO_URL}" alt="Logo PPGIO" style="width:480px; max-width:40vw;" />
      <div>
        <h1 style="margin:0;">Matrizes A e B - Guia Planar</h1>
        <p style="margin:6px 0 0 0; opacity:.9;">
          <strong>Thalles Cotta Fontainha</strong>, <strong>PPGIO Matrícula:</strong> 2410091DIOAMA
        </p>
        <p style="margin:0; opacity:.9;">
          <em>"Fotonica Analise Modal e BPM V2.pdf"</em> recebido em 11/09/2025
        </p>
          <strong>Disciplina:</strong> Fotônica Computacional (TCE11209 - UFF)
        </p>
          <strong>Professor:</strong> Andres Pablo Lopez Barbero
        </p>
      </div>
    </div>

    <style>
  .note-small{
    background:#0f1a2b;              /* azul escuro da sua UI */
    border:1px solid #1f2937;
    border-radius:12px;
    padding:10px 14px;
    font-size:12px;                   /* menor */
    line-height:1.25;                 /* compacto */
    color:#e5e7eb;
  }
  .note-small pre{
    margin:6px 0 0 0;
    white-space:pre-wrap;             /* quebra se precisar */
  }
</style>

    """,
    unsafe_allow_html=True,
)

# ======= SIDEBAR (Parâmetros) =======
with st.sidebar:
    st.header("Parâmetros")
    n_camadas = st.number_input("Número de camadas (≥2)", min_value=2, value=3, step=1)
    st.markdown("**Informe largura e índice n para cada camada** (mesmas unidades que λ).")
    larguras, indices_n = [], []
    for i in range(n_camadas):
        c1, c2 = st.columns(2)
        with c1:
            L = st.number_input(
                f"Largura camada {i+1}",
                min_value=1e-12, value=1.00, step=0.01, format="%.2f", key=f"L{i}"
            )
        with c2:
            # se quiser retirar esses defaults fixos, me avise que troco para padrões editáveis via session_state
            n_default = 3.55 if (i == 0 or i == n_camadas - 1) else 3.60
            n = st.number_input(
                f"n camada {i+1}",
                min_value=1e-12, value=float(n_default), step=0.01, format="%.2f", key=f"n{i}"
            )
        larguras.append(L); indices_n.append(n)

    Np   = st.number_input("Np (nº de pontos, ≥3)", min_value=3, value=101, step=1)
    lamb = st.number_input("λ (compr. de onda)", min_value=1e-12, value=1.00, step=0.01, format="%.2f")
    montar = st.button("Montar A e B", use_container_width=True)

# ======= DESCRIÇÃO + PSEUDOCÓDIGO =======
st.info("Ajuste os parâmetros na barra lateral e clique **Montar A e B**.")

st.markdown("""
<div class="note-small">
  <strong>Etapa 1 — Pré-processamento: montar A e B</strong>
  <pre>
Entradas: n_camadas, largura[i], n[i], Np, λ

1) L_total = sum(largura)                 # largura total
2) Δx = L_total/(Np-1)                    # passo da malha
3) k0 = 2π/λ                              # número de onda
4) x = linspace(0, L_total, Np)           # grade 1D

5) limites = [0] + cumsum(largura)        # fronteiras das camadas
6) para x_j: achar c s/ limites[c-1] ≤ x_j < limites[c]; n_x[j] = n[c]

7) D2 = tridiag(1,-2,1)/(Δx^2)            # 2ª derivada (FDM)
8) Diag_n2 = diag(n_x^2)
9) A = D2 + k0^2 * Diag_n2
10) B = k0^2 * I

Checks: A.shape, B.shape; A[0,0], A[0,1], A[1,0], A[mid,mid]; B[0,0], B[-1,-1]
  </pre>
</div>
""", unsafe_allow_html=True)


# ======= LÓGICA =======
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

# ======= SAÍDA =======
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

    except Exception as e:
        st.error(f"Erro ao montar as matrizes: {e}")





