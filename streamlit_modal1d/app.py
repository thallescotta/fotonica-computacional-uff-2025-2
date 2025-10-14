# app.py — App Streamlit (único arquivo) para montar A e B (guia planar)
import math
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Matrizes A e B (Guia Planar)", layout="centered")

# ======= TEMA CLARO + ESTILO (fundo branco e botões melhores) =======
st.markdown(
    """
    <style>
      /* fundo claro */
      .stApp { background: #ffffff; color: #0f172a; }

      /* sidebar com leve contraste */
      section[data-testid="stSidebar"] { background: #f8fafc; border-right: 1px solid #e5e7eb; }

      /* tipografia mais agradável nos títulos */
      h1, h2, h3 { line-height: 1.2; }

      /* cartão para inputs na sidebar */
      .param-card {
          background: #ffffff;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          padding: 12px;
          box-shadow: 0 2px 12px rgba(0,0,0,.04);
      }

      /* estiliza botões */
      .stButton > button {
          background: #2563eb;
          color: #ffffff;
          border: 1px solid #1e40af;
          border-radius: 10px;
          padding: 0.6rem 1rem;
          font-weight: 700;
          box-shadow: 0 4px 14px rgba(37,99,235,0.25);
      }
      .stButton > button:hover {
          background: #1d4ed8;
          border-color: #1e3a8a;
      }

      /* inputs com borda mais definida */
      div[data-baseweb="input"] > div {
          border-radius: 10px;
          border: 1px solid #cbd5e1;
      }
      div[data-baseweb="input"] > div:focus-within {
          border-color: #2563eb;
          box-shadow: 0 0 0 1px #2563eb inset;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ======= CAPA (logo + seus dados) =======
# Use o link RAW do GitHub para carregar a imagem no Streamlit
LOGO_URL = "https://raw.githubusercontent.com/thallescotta/logo-ppgio-vetorizado/main/SVG-PPGIO_invert_preto_para_branco.png"

st.markdown(
    f"""
    <div style="display:flex; gap:24px; align-items:center; margin:10px 0 12px 0;">
      <img src="{LOGO_URL}" alt="Logo PPGIO" style="width:240px; max-width:40vw;" />
      <div>
        <h1 style="margin:0;">Matrizes A e B — Guia Planar (Pré-processamento)</h1>
        <p style="margin:6px 0 0 0; opacity:.9;">
          <strong>Thalles Cotta Fontainha</strong> — <strong>PPGIO Matrícula:</strong> 2410091DIOAMA
        </p>
        <p style="margin:0; opacity:.9;">
          <em>"Fotonica Analise Modal e BPM V2.pdf"</em> recebido em 11/09/2025 •
          <strong>Disciplina:</strong> Fotônica Computacional (TCE11209 — UFF) •
          <strong>Professor:</strong> Andres Pablo Lopez Barbero
        </p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ======= SIDEBAR — PARÂMETROS EM DESTAQUE (2 casas decimais + padrões editáveis) =======
with st.sidebar:
    st.markdown("### ⚙️ Parâmetros (Etapa 1)")
    st.info("Preencha e clique **Montar A e B**.", icon="🧩")

    st.markdown('<div class="param-card">', unsafe_allow_html=True)

    n_camadas = st.number_input("Número de camadas (≥2)", min_value=2, value=3, step=1)

    # Padrões globais (não fixa nada no código; o usuário decide)
    L_default = st.number_input(
        "Largura padrão (para novas camadas)", min_value=1e-12, value=1.00, step=0.01, format="%.2f"
    )
    n_default = st.number_input(
        "n padrão (para novas camadas)", min_value=1e-12, value=1.00, step=0.01, format="%.2f"
    )

    st.markdown("**Largura e índice n por camada** (mesmas unidades que λ).")

    larguras, indices_n = [], []
    for i in range(n_camadas):
        c1, c2 = st.columns(2)

        # usa session_state para não perder valores já digitados ao mudar n_camadas
        key_L = f"L{i}"
        key_n = f"n{i}"
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
    lamb = st.number_input("λ (compr. de onda)", min_value=1e-12, value=1.00, step=0.01, format="%.2f")

    montar = st.button("🚀 Montar A e B", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ======= BLOCO EXPLICATIVO (ilustrativo da atividade proposta) =======
st.info(
    """
**Etapa 1 — Pré-processamento (o que o professor pediu):**

- **Entrada**: número de camadas, larguras, índices _n_, **Np** e **λ**.  
- **Discretização**: grade uniforme em \\([0, L_{total}]\\) com \\(\\Delta x = L_{total}/(Np-1)\\).  
- **Perfil** \\(n(x)\\): para cada ponto da grade, decidir em qual camada ele cai e atribuir \\(n\\).  
- **Matrizes**:  
  • \\(D_2/\\Delta x^2\\) (tridiagonal com \\(-2, +1, +1\\))  
  • \\(\\mathrm{diag}(n(x)^2)\\)  
  • **A** = \\(D_2/\\Delta x^2 + k_0^2\\,\\mathrm{diag}(n^2)\\)  
  • **B** = \\(k_0^2 I\\)  
- **Saída**: apenas **checks** simples (dimensões e alguns elementos).  
  Nada de modos, gráficos ou BPM nesta etapa.
""",
)

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

        # (Sem downloads, sem prévias, sem listas adicionais)
    except Exception as e:
        st.error(f"Erro ao montar as matrizes: {e}")
