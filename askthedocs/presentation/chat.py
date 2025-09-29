"""
Interface de Chat com RAG

Este módulo implementa a interface de chat que permite aos usuários
fazer perguntas sobre documentação usando RAG (Retrieval-Augmented Generation).
Utiliza embeddings para buscar contexto relevante e um LLM para gerar respostas.
"""

import streamlit as st
from service.rag import RAGService

def show():
    """
    Exibe a interface de chat com RAG.
    
    Funcionalidades:
    - Carrega automaticamente a coleção selecionada
    - Mantém histórico de conversa na sessão
    - Usa RAG para responder perguntas baseadas na documentação
    """
    st.header("💬 Pergunte sobre a documentação")

    # Verifica se uma coleção foi selecionada
    if not st.session_state.collection:
        st.info("Selecione uma documentação para começar a perguntar")
        return
    
    st.success(f"Documentação selecionada: {st.session_state.collection}")

    # Inicializa o serviço RAG se não existir
    if "rag_service" not in st.session_state:
        st.session_state.rag_service = RAGService()

    # Carrega a coleção se for diferente da atual
    if "current_collection" not in st.session_state or st.session_state.current_collection != st.session_state.collection:
        with st.spinner("Carregando documentação..."):
            success = st.session_state.rag_service.load_collection(st.session_state.collection)
            if success:
                st.session_state.current_collection = st.session_state.collection
                st.success("Documentação carregada com sucesso!")
            else:
                st.error("Erro ao carregar documentação")
                return

    # Exibe histórico de mensagens
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Interface de input para novas perguntas
    if prompt := st.chat_input("Pergunte sobre a documentação"):
        # Adiciona pergunta do usuário ao histórico
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Gera resposta usando RAG
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = st.session_state.rag_service.ask_question(prompt)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

    # Botão para limpar conversa
    if st.button("Limpar conversa"):
        st.session_state.messages = []
        st.rerun()