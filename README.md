# Fotônica Computacional - Análise Modal 

<p align="center"> <img src="https://codeconverter.com/images/convert-matlab-to-python.png" alt="MATLAB → Python" style="width:20%;">

---
## Atividade 1
[diagrama_dispersao_TE_FDM_1D.ipynb](https://github.com/thallescotta/fotonica-computacional-uff-2025-2/blob/main/diagrama_dispersao_TE_FDM_1D.ipynb)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white" alt="Python" />
  &nbsp;
  <img src="https://img.shields.io/badge/Jupyter-Notebook-orange?logo=jupyter&logoColor=white" alt="Jupyter Notebook" />
  &nbsp;
  <img src="https://img.shields.io/badge/NumPy-1.x-lightgrey?logo=numpy&logoColor=013243" alt="NumPy" />
  &nbsp;
  <img src="https://img.shields.io/badge/Matplotlib-3.x-lightgrey?logo=plotly&logoColor=white" alt="Matplotlib" />
</p>



---


> **Aluno:** Thalles Cotta Fontainha - **PPGIO Matrícula:** 2410091DIOAMA  
> **Disciplina:** TCE11209 - Fotônica Computacional (UFF)  
> **Professor:** Andres Pablo Lopez Barbero

Projeto de **análise modal** em **guia planar 1D** (modos **TE**), formulado como **problema de autovalores** para obter **$n_\mathrm{eff}$** (autovalores) e **$E(x)$** (autovetores). Implementação principal em **Python/Colab**, com versão equivalente em **MATLAB/Octave**.

---

## Pipeline do Projeto

O fluxo completo é dividido em **três etapas principais**, refletidas nos blocos de código:

1. **Bloco 1 – Pré-processamento**  
   Define os parâmetros físicos, constrói a malha 1D e monta o perfil de índice $n(x)$ com camadas generalizadas.  

2. **Bloco 2 – Processamento dos Modos**  
   Monta as matrizes do problema modal (diferenças finitas para a 2ª derivada com condição de contorno de Dirichlet), resolve o autoproblema, seleciona os modos guiados  
   ($n_1 < n_\mathrm{eff} < n_2$), normaliza os campos e gera os gráficos dos modos.

3. **Bloco 3 – Pós-processamento (Diagrama de Dispersão)**  
   Varre a razão $d/\lambda$, calcula as curvas $n_\mathrm{eff}(d/\lambda)$ para cada ordem de modo (TE0, TE1, …) e produz o diagrama de dispersão final.

> Este encadeamento **Pré → Processamento dos Modos → Pós** resume todo o pipeline:  
> da preparação da malha, passando pela solução do problema modal, até a análise final com o diagrama de dispersão.


> **Caso do slide (simétrico, pág. 15):** $n_2 = 3{,}60$, $n_1 = n_3 = 3{,}55$.


---

## Referências
1. Okamoto, K. — *Fundamentals of Optical Waveguides* (2ª ed., Academic Press, 2006).  
   PDF neste repositório: [`[Katsunari_Okamoto]_Fundamentals_of_optical_waveguide.pdf`](./%5BKatsunari_Okamoto%5D_Fundamentals_of_optical_waveguide.pdf)

2. **modesolverpy** — Photonic mode solver em **Python** (SciPy/Matplotlib) com exemplos práticos de solução modal.  
   GitHub: <https://github.com/jtambasco/modesolverpy>

