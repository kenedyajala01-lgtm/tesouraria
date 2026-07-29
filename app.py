"""
⚓ Tesouraria Grêmio Naval — app.py
Ponto de entrada da aplicação com controle de acesso (ADM / Visitante).
"""
import hashlib
import streamlit as st

# Import dos módulos no topo do arquivo — precisa vir antes de qualquer uso
# (ex.: no bloco da sidebar, que consulta gs.load_caixa() antes das abas).
from modules import dashboard, lancamentos, socios, relatorios, simulador, limpeza, verba, gsheets as gs  # noqa: E402

st.set_page_config(
    page_title="Tesouraria — Grêmio Naval",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Constantes de autenticação
# ─────────────────────────────────────────────────────────────────────────────
_SENHA_HASH = hashlib.sha256(b"rogerreidelas2026").hexdigest()


def _check_password(pw: str) -> bool:
    return hashlib.sha256(pw.encode()).hexdigest() == _SENHA_HASH


# ─────────────────────────────────────────────────────────────────────────────
# CSS — Tema Marítimo (Navy × Gold)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Nunito:ital,wght@0,300;0,400;0,600;1,400&display=swap');

    :root {
        --bg:      #060D1B; --surface: #0C1A31; --card:    #102244;
        --border:  rgba(201,168,76,0.18);
        --gold:    #C9A84C; --gold-hi: #E8C878;
        --text:    #EEF2F7; --muted:   #7A8EA8;
        --success: #27AE60; --danger:  #C0392B; --warn: #E67E22;
    }

    .stApp { background-color: var(--bg); color: var(--text); font-family: 'Nunito', sans-serif; }
    .block-container { padding-top: 1.5rem; }

    [data-testid="stSidebar"] { background-color: var(--surface); border-right: 1px solid var(--border); }
    [data-testid="stSidebar"] [data-testid="stMetric"] { background: var(--card); }

    h1, h2, h3, h4 { font-family: 'Cinzel', serif !important; color: var(--gold) !important; letter-spacing: 0.04em; }
    h1 { font-size: 1.9rem !important; }
    h4 { font-size: 1rem !important; color: var(--gold-hi) !important; }

    .stTabs [data-baseweb="tab-list"] { background: var(--surface); border-radius: 10px; padding: 4px 6px; gap: 4px; border: 1px solid var(--border); }
    .stTabs [data-baseweb="tab"] { color: var(--muted); font-family: 'Cinzel', serif; font-size: 0.82rem; border-radius: 8px; padding: 6px 14px; transition: all 0.2s; }
    .stTabs [aria-selected="true"] { background: var(--gold) !important; color: var(--bg) !important; font-weight: 700; }
    .stTabs [data-baseweb="tab"]:hover { color: var(--gold-hi); }

    [data-testid="stMetric"] { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1rem 1.25rem; }
    [data-testid="stMetricLabel"] p { color: var(--muted) !important; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.09em; }
    [data-testid="stMetricValue"]  { color: var(--gold-hi) !important; font-family: 'Cinzel', serif; font-size: 1.5rem !important; }
    [data-testid="stMetricDelta"]  { font-size: 0.8rem !important; }

    .stButton > button { background: linear-gradient(135deg, var(--gold), var(--gold-hi)); color: var(--bg); border: none; border-radius: 8px; font-family: 'Cinzel', serif; font-weight: 700; letter-spacing: 0.05em; padding: 0.45rem 1.25rem; transition: all 0.18s ease; box-shadow: 0 2px 8px rgba(201,168,76,0.25); }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(201,168,76,0.45); }

    .stTextInput input, .stNumberInput input, .stSelectbox > div > div { background-color: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; color: var(--text) !important; }
    .stDateInput input { background: var(--card) !important; color: var(--text) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; }
    label { color: var(--muted) !important; font-size: 0.82rem; letter-spacing: 0.04em; }

    .stDataFrame { border: 1px solid var(--border) !important; border-radius: 10px !important; }
    .stAlert { border-radius: 10px !important; }
    [data-testid="stNotificationContentSuccess"] { background: rgba(39,174,96,0.12) !important; }
    [data-testid="stNotificationContentError"]   { background: rgba(192,57,43,0.12) !important; }

    details { border: 1px solid var(--border) !important; border-radius: 10px !important; background: var(--surface) !important; }
    summary { color: var(--gold) !important; font-family: 'Cinzel', serif; font-size: 0.88rem; }
    hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

    .wpp-btn { display: inline-block; background: #25D366; color: #fff !important; padding: 3px 12px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; text-decoration: none; letter-spacing: 0.03em; transition: opacity 0.15s; }
    .wpp-btn:hover { opacity: 0.85; }

    /* Badge de role */
    .role-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        font-family: 'Cinzel', serif;
    }
    .role-adm  { background: rgba(201,168,76,0.18); color: #E8C878; border: 1px solid rgba(201,168,76,0.4); }
    .role-vis  { background: rgba(52,152,219,0.15); color: #85C1E9; border: 1px solid rgba(52,152,219,0.35); }

    /* Tela de login */
    .login-card {
        max-width: 440px;
        margin: 3rem auto;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 2.5rem 2rem;
    }

    ::-webkit-scrollbar       { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--gold); border-radius: 3px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# Cabeçalho
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center;padding:0.5rem 0 1rem;">
        <div style="font-size:2.4rem;">⚓</div>
        <h1 style="margin:0.1rem 0 0;">GRÊMIO NAVAL</h1>
        <p style="color:#7A8EA8;font-size:0.8rem;letter-spacing:0.18em;
                  text-transform:uppercase;margin-top:0.3rem;">
            Sistema Integrado de Tesouraria
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# Estado de sessão
# ─────────────────────────────────────────────────────────────────────────────
if "role" not in st.session_state:
    st.session_state["role"] = None          # None | "admin" | "visitor"
if "login_error" not in st.session_state:
    st.session_state["login_error"] = False

# ─────────────────────────────────────────────────────────────────────────────
# Tela de Acesso (se ainda não autenticado)
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state["role"] is None:
    st.markdown(
        """
        <div style="text-align:center;margin-bottom:0.5rem;">
            <p style="color:#7A8EA8;font-size:0.92rem;">
                Selecione como deseja acessar o sistema.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_vis, col_adm = st.columns(2, gap="large")

    with col_vis:
        st.markdown(
            """
            <div style="background:#0C1A31;border:1px solid rgba(52,152,219,0.25);
                        border-radius:14px;padding:1.5rem;text-align:center;margin-bottom:1rem;">
                <div style="font-size:2rem;">👁️</div>
                <h4 style="color:#85C1E9 !important;margin:0.5rem 0 0.3rem;">Visitante</h4>
                <p style="color:#7A8EA8;font-size:0.82rem;margin:0;">
                    Acesso somente leitura.<br>Dashboard · Relatórios · Simulador
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Entrar como Visitante", use_container_width=True, key="btn_visitor"):
            st.session_state["role"] = "visitor"
            st.rerun()

    with col_adm:
        st.markdown(
            """
            <div style="background:#0C1A31;border:1px solid rgba(201,168,76,0.25);
                        border-radius:14px;padding:1.5rem;text-align:center;margin-bottom:1rem;">
                <div style="font-size:2rem;">🔐</div>
                <h4 style="color:#E8C878 !important;margin:0.5rem 0 0.3rem;">Administrador</h4>
                <p style="color:#7A8EA8;font-size:0.82rem;margin:0;">
                    Acesso total ao sistema.<br>Requer senha de administrador.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        senha = st.text_input(
            "Senha", type="password", placeholder="Digite a senha de ADM",
            key="inp_senha_adm", label_visibility="collapsed",
        )
        if st.button("Entrar como Administrador", use_container_width=True, key="btn_adm"):
            if _check_password(senha):
                st.session_state["role"] = "admin"
                st.session_state["login_error"] = False
                st.rerun()
            else:
                st.session_state["login_error"] = True
                st.rerun()

        if st.session_state["login_error"]:
            st.error("🔒 Senha incorreta. Tente novamente.")

    st.stop()  # Não renderiza nada mais enquanto não autenticado

# ─────────────────────────────────────────────────────────────────────────────
# Usuário autenticado — barra de status + logout
# ─────────────────────────────────────────────────────────────────────────────
role = st.session_state["role"]   # "admin" | "visitor"

_badge_html = (
    '<span class="role-badge role-adm">⚙️ ADMINISTRADOR</span>'
    if role == "admin"
    else '<span class="role-badge role-vis">👁️ VISITANTE</span>'
)

col_badge, col_logout = st.columns([6, 1])
with col_badge:
    st.markdown(_badge_html, unsafe_allow_html=True)
with col_logout:
    if st.button("🚪 Sair", key="btn_logout"):
        st.session_state["role"] = None
        st.session_state["login_error"] = False
        st.rerun()

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# Barra lateral — painel rápido de status
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:0.5rem 0 1rem;">
            <div style="font-size:1.8rem;">⚓</div>
            <h4 style="margin:0.2rem 0 0;">GRÊMIO NAVAL</h4>
            <p style="color:#7A8EA8;font-size:0.72rem;letter-spacing:0.1em;
                      text-transform:uppercase;margin-top:0.2rem;">
                Diretoria Naval · 2026
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(_badge_html, unsafe_allow_html=True)
    st.divider()

    _df_caixa = gs.load_caixa()
    if not _df_caixa.empty:
        _saldo = _df_caixa[_df_caixa["Tipo"] == "Entrada"]["Valor"].sum() \
                 - _df_caixa[_df_caixa["Tipo"] == "Saída"]["Valor"].sum()
    else:
        _saldo = 0.0
    st.metric("💰 Saldo Atual", f"R$ {_saldo:,.2f}")

    if role == "admin":
        _pendentes = gs.count_solicitacoes_pendentes()
        st.metric(
            "💼 Solicitações Pendentes", _pendentes,
            delta="requer análise" if _pendentes else None,
            delta_color="off",
        )

    st.divider()
    st.caption(
        "Navegue pelas abas no topo da página para acessar Dashboard, "
        "Lançamentos, Relatórios e demais funções."
    )

# ─────────────────────────────────────────────────────────────────────────────
# Demo warning
# ─────────────────────────────────────────────────────────────────────────────
try:
    _demo = "gcp_service_account" not in st.secrets
except Exception:
    _demo = True

if _demo:
    st.warning(
        "🔒 **Modo Demo** — os dados ficam apenas na memória desta sessão. "
        "Configure `.streamlit/secrets.toml` com suas credenciais do Google Sheets "
        "para persistência real.",
        icon="ℹ️",
    )

# ─────────────────────────────────────────────────────────────────────────────
# Tabs — exibição condicional por role
# ─────────────────────────────────────────────────────────────────────────────
if role == "admin":
    _pend = gs.count_solicitacoes_pendentes()
    _label_verba = f"💼 Solicitações de Verba ({_pend})" if _pend else "💼 Solicitações de Verba"
    tabs = st.tabs([
        "📊 Dashboard",
        "💸 Lançamentos",
        "👥 Sócios & Cobranças",
        _label_verba,
        "📋 Relatórios",
        "🧮 Simulador de Eventos",
        "🗑️ Limpeza de Dados",
    ])
    with tabs[0]: dashboard.render()
    with tabs[1]: lancamentos.render()
    with tabs[2]: socios.render()
    with tabs[3]: verba.render(role)
    with tabs[4]: relatorios.render()
    with tabs[5]: simulador.render()
    with tabs[6]: limpeza.render()

else:  # visitor
    tabs = st.tabs([
        "📊 Dashboard",
        "💼 Solicitar Verba",
        "📋 Relatórios",
        "🧮 Simulador de Eventos",
        "🔒 Área Restrita",
    ])
    with tabs[0]: dashboard.render()
    with tabs[1]: verba.render(role)
    with tabs[2]: relatorios.render()
    with tabs[3]: simulador.render()
    with tabs[4]:
        st.markdown(
            """
            <div style="text-align:center;padding:3rem 1rem;">
                <div style="font-size:3.5rem;margin-bottom:1rem;">🔒</div>
                <h3 style="color:#E74C3C !important;">Acesso Restrito</h3>
                <p style="color:#7A8EA8;font-size:0.95rem;max-width:400px;margin:0 auto 1.5rem;">
                    As abas <strong>Lançamentos</strong>, <strong>Sócios & Cobranças</strong>
                    e demais funções administrativas exigem acesso de Administrador.
                </p>
                <p style="color:#7A8EA8;font-size:0.82rem;">
                    Clique em <strong>🚪 Sair</strong> e entre com a senha de ADM para liberar o acesso completo.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
