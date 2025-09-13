# Fotônica Computacional - Análise Modal (Guias Planares 1D, TE)

<p align="center"> <img src="https://codeconverter.com/images/convert-matlab-to-python.png" alt="MATLAB → Python" style="width:20%;">

> **Aluno:** Thalles Cotta Fontainha - **PPGIO Matrícula:** 2410091DIOAMA  
> **Disciplina:** TCE11209 - Fotônica Computacional (UFF)  
> **Professor:** Andres Pablo Lopez Barbero

Projeto de **análise modal** em **guia planar 1D** (modos **TE**), formulado como **problema de autovalores** para obter **$n_\mathrm{eff}$** (autovalores) e **$E(x)$** (autovetores). Implementação principal em **Python/Colab**, com versão equivalente em **MATLAB/Octave**.

---

## Pipeline (A → B → C)
1. **Bloco A: Pré-processamento:** parâmetros físicos, domínio/malha e perfil **$n(x)$** com **camadas generalizadas**.  
2. **Bloco B: Montagem matricial:** discretização da 2ª derivada (diferenças finitas, CC Dirichlet) e montagem das matrizes do problema modal.  
3. **Bloco C: Solução e análise:** autovalores/autovetores, seleção de modos guiados ($n_\text{clad} < n_\mathrm{eff} < n_\text{core}$), normalização e gráficos.

> **Caso do slide (simétrico, pág. 15):** $n_2 = 3{,}60$, $n_1 = n_3 = 3{,}55$.

---

## Resultados Esperados
- **$n_\mathrm{eff}$** dos modos TE (entre **$n_\text{clad}$** e **$n_\text{core}$**).  
- **Perfis $E_m(x)$** normalizados (oscilatório no núcleo, evanescente nas cascas).  
- Gráficos de **$n(x)$** e dos **modos**.  
- Checagens numéricas (dimensões/simetria das matrizes; critério de guiamento).

---

## Referências
1. Okamoto, K. — *Fundamentals of Optical Waveguides* (2ª ed., Academic Press, 2006).  
   PDF neste repositório: [`[Katsunari_Okamoto]_Fundamentals_of_optical_waveguide.pdf`](./%5BKatsunari_Okamoto%5D_Fundamentals_of_optical_waveguide.pdf)

2. **modesolverpy** — Photonic mode solver em **Python** (SciPy/Matplotlib) com exemplos práticos de solução modal.  
   GitHub: <https://github.com/jtambasco/modesolverpy>

