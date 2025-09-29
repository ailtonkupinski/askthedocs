"""
AskTheDocs - Aplicação principal

Esta é a aplicação principal do AskTheDocs, construída com Streamlit.
Oferece duas funcionalidades principais:
1. Chat com documentação usando RAG (Retrieval-Augmented Generation)
2. Scraping de websites para criar coleções de documentação

Autor: Ailton Kupinski
Data: 2025
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
from presentation import scraping, chat

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da página principal
st.set_page_config(
    page_title="AskTheDocs", 
    page_icon=":books:", 
    layout="wide"
)
st.title("AskTheDocs")

# Sidebar com navegação e seleção de coleções
with st.sidebar:
    # Sistema de logo adaptativo ao tema (claro/escuro)
    _base_dir = Path(__file__).parent
    _logo_light_path = _base_dir / "assets" / "logo_white.svg"
    _logo_dark_path = _base_dir / "assets" / "logo_dark.svg"
    _theme_base = st.get_option("theme.base") or "light"
    _logo_to_use = _logo_dark_path if _theme_base == "dark" else _logo_light_path
    st.image(str(_logo_to_use), width='stretch')
    
    # Seletor de modo de operação
    st.header("Documento")
    mode = st.radio("Modo:", ("Chat", "Scraping"))

    st.divider()
    st.subheader("Documentações disponíveis")

    # Lista coleções de documentação disponíveis
    collections_path = "data/collections"
    if os.path.exists(collections_path):
        collections = [d for d in os.listdir(collections_path)
                        if os.path.isdir(os.path.join(collections_path, d))]

        # Exibe cada coleção com botão para selecionar
        for collection in collections:
            col1, col2 = st.columns([3, 2])
            with col1:
                st.write(f"📁 {collection}")
            with col2:
                if st.button("Usar", key=f"use_{collection}"):
                    st.session_state.collection = collection
                    st.rerun()

# Inicializa estado da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []
if "collection" not in st.session_state:
    st.session_state.collection = None

# Roteamento para diferentes modos
if mode == "Scraping":
    scraping.show()
else:
    chat.show()