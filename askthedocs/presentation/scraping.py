"""
Interface de Web Scraping

Este módulo implementa a interface para scraping de websites,
permitindo aos usuários extrair documentação de URLs e criar
coleções locais para uso com o sistema RAG.
"""

import streamlit as st
from service.scraping import ScrapingService

def show():
    """
    Exibe a interface de web scraping.
    
    Funcionalidades:
    - Formulário para inserir URL e nome da coleção
    - Execução do scraping usando Firecrawl API
    - Feedback visual do progresso e resultados
    """
    st.header("🔍 Web Scraping")

    # Formulário para configuração do scraping
    with st.form("scraping_form"):
        url = st.text_input("URL da documentação:")
        collection_name = st.text_input("Nome da documentação:")
        submitted = st.form_submit_button("Iniciar scraping")

    # Processa o scraping quando o formulário é submetido
    if submitted:
        # Validação dos campos obrigatórios
        if not url or not collection_name:
            st.warning("Preencha a URL e o nome da documentação.")
            return
            
        # Execução do scraping com feedback visual
        with st.spinner("Iniciando scraping..."):
            try:
                scraper = ScrapingService()
                result = scraper.scrape_website(url, collection_name)
                
                # Exibe resultado do scraping
                if result.get("success"):
                    st.success(f"Scraping concluído com sucesso! Salvos {result['files']} arquivos.")
                else:
                    st.error(f"Erro ao iniciar scraping: {result.get('error', 'desconhecido')}")
            except Exception as e:
                st.error(f"Falha inesperada: {e}")