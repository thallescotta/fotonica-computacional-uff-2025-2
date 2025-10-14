# app.py — App Streamlit (único arquivo) para montar A e B (guia planar)
import math
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Matrizes A e B (Guia Planar)", layout="wide")

# ======= ESTILO (tema escuro + área principal mais larga + sidebar azul) =======
st.markdown(
    """
    <style>
      /* App escuro */
      .stApp { background: #000000; color: #e5e7eb; }
      h1, h2, h3 { line-height: 1.2; color: #e5e7eb; }

      /* Aumenta a largura útil do conteúdo (~40% maior) */
      .main .block-container {
        max-width: 1400px;
        padding-top: 0.5rem;
      }

      /* Sidebar azul escuro */
      section[data-testid="stSidebar"]{
        background: #0b1220;
        border-right: 1px solid #0f172a;
      }
      section[data-testid="stSidebar"] * { color: #e5e7eb !important; }
      section[data-testid="stSidebar"] h1,
      section[data-testid="stSidebar"] h2,
      section[data-testid="stSidebar"] h3 { color: #e5e7eb !important; }

      /* Inputs na sidebar */
      section[data-testid="stSidebar"] div[data-baseweb="input"] > div{
        background: #111a2b !important;
        color: #e5e7eb !important;
        border-radius: 10px;
        border: 1px solid #1e3a8a;
      }
      section[data-testid="stSidebar"] div[data-baseweb="input"] > div:focus-within{
        border-color: #60a5fa;
        box-shadow: 0 0 0 1px #60a5fa inset;
      }

      /* Botões visíveis no escuro */
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
        <h1 style="margin:0;">Matrizes A e B - Guia Planar</h1>
        <p style="margin:6px 0 0 0; opacity:.9;">
          <strong>Thalles Cotta Fontainha</strong>, <strong>PPGIO Matrícula:</strong> 2410091DIOAMA
        </p>
        <p style="margin:0; opacity:.9;">
          <em>"Fotonica Analise Modal e BPM V2.pdf"</em> recebido em 11/09/2025
        </p>
        <p style="margin:0; opacity:.9;">
          <strong>Disciplina:</strong> Fotônica Computacional (TCE11209 - UFF) •
          <strong>Professor:</strong> Andres Pablo Lopez Barbero
        </p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ======= SIDEBAR (Parâmetros com padrões editáveis e persistência) =======
with st.sidebar:
    st.header("Parâmetros")

    n_camadas = st.number_input("Número de camadas (≥2)", min_value=2, value=3, step=1)

    # Padrões globais (o usuário define; não há valores fixos no código)
    L_default = st.number_input(
        "Largura padrão (para novas camadas)", min_value=1e-12, value=1.00, step=0.01, format="%.2f"
    )
    n_default = st.number_input(
        "n padrão (para novas camadas)", min_value=1e-12, value=1.00, step=0.01, format="%.2f"
    )  # OBS: valores típicos anteriormente usados eram 3.55 (borda) e 3.60 (núcleo); aqui são entradas do usuário e totalmente ajustáveis.

    st.markdown("**Informe largura e índice n para cada camada** (mesmas unidades que λ).")

    larguras, indices_n = [], []
    for i in range(n_camadas):
        c1, c2 = st.columns(2)
        key_L = f"L{i}"
        key_n = f"n{i}"
        # Inicializa com os padrões apenas na 1ª vez; depois mantém o que o usuário editou
        if key_L not in st.session_state:
            st.session_state[key_L] = float(L_default)
        if key_n not in st.session_state:
            st.session_state[key_n] = float(n_default)

        with c1:
            L = st.number_input(
                f"Largura camada {i+1}",
                min_value=1e-12,
                value=float(st.session_state[key_L]),
                step=0.01, format="%.2f",
                key=key_L
            )
        with c2:
            n_val = st.number_input(
                f"n camada {i+1}",
                min_value=1e-12,
                value=float(st.session_state[key_n]),
                step=0.01, format="%.2f",
                key=key_n
            )
        larguras.append(L)
        indices_n.append(n_val)

    Np   = st.number_input("Np (nº de pontos, ≥3)", min_value=3, value=101, step=1)
    lamb = st.number_input("λ (comprimento de onda)", min_value=1e-12, value=1.00, step=0.01, format="%.2f")

    montar = st.button("Montar A e B", use_container_width=True)

# ======= DESCRIÇÃO + PSEUDOCÓDIGO (compacto, com comentários verdes) =======
st.markdown("#### Etapa 1 — Pré-processamento: montar A e B (passo a passo)")

pseudo = """\
# Entradas do usuário:
# n_camadas, largura[i], n[i], Np, λ

L_total = sum(largura)             # largura total do guia
Δx      = L_total/(Np-1)           # passo da malha 1D
k0      = 2*π/λ                    # número de onda no vácuo
x       = linspace(0, L_total, Np) # grade uniforme

# Perfil n(x):
limites = [0] + cumsum(largura)    # fronteiras acumuladas das camadas
for cada x_j em x:                 # j = 0..Np-1
    encontre c tal que limites[c-1] ≤ x_j < limites[c]
    n_x[j] = n[c]                  # índice de refração da camada c

# Matrizes:
D2      = tridiag(1, -2, 1)/(Δx**2) # operador de 2ª derivada (FDM)
Diag_n2 = diag(n_x**2)              # diagonal com n(x)^2
A       = D2 + (k0**2)*Diag_n2      # matriz do problema generalizado
B       = (k0**2)*I                 # matriz massa (diagonal)

# Checks para conferência no papel:
# A.shape, B.shape
# A[0,0], A[0,1], A[1,0], A[mid,mid], B[0,0], B[-1,-1]
"""
st.code(pseudo, language="python")

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

        st.subheader("Resumo")
        c1, c2, c3 = st.columns(3)
        c1.metric("Número de camadas", len(larguras))
        c2.metric("Np", Np)
        c3.metric("L_total (largura total)", f"{L_total:.6g}")

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

        # ---- Pré-visualizações com detalhes de eixos (i/j e x correspondente) ----
        def preview_matrix(M, x, s=10):
            s = min(s, M.shape[0])
            cols = [f"j={j}  |  x_j={x[j]:.6g}" for j in range(s)]
            idx  = [f"i={i}  |  x_i={x[i]:.6g}" for i in range(s)]
            return pd.DataFrame(M[:s, :s], columns=cols, index=idx)

        s = min(10, Np)
        st.markdown("**Legenda das pré-vias:** linhas = `i` (x_i = i·Δx), colunas = `j` (x_j = j·Δx).")

        st.markdown(f"**Matriz A — submatriz [0:{s}, 0:{s}] (canto superior esquerdo)**")
        with st.expander("Mostrar A (0…s-1, 0…s-1)"):
            st.dataframe(preview_matrix(A, x, s=s), use_container_width=True)

        st.markdown(f"**Matriz B — submatriz [0:{s}, 0:{s}] (canto superior esquerdo)**")
        with st.expander("Mostrar B (0…s-1, 0…s-1)"):
            st.dataframe(preview_matrix(B, x, s=s), use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao montar as matrizes: {e}")
