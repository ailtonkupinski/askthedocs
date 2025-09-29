"""
Interface de Lista de Documentações

Este módulo implementa a interface para listar todas as documentações
disponíveis com seus metadados (nome, URL, versão, data de inserção).
Permite selecionar documentações para uso no chat.
"""

import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime

def show():
    """
    Exibe a lista de documentações em formato de tabela.
    
    Funcionalidades:
    - Carrega metadados do índice global ou varre diretórios
    - Exibe tabela com Nome, URL, Versão, Data da inserção
    - Permite selecionar documentação para uso no chat
    """
    st.header("📚 Lista de Documentações")
    
    # Carrega dados das documentações
    collections_data = _load_collections_data()
    
    if not collections_data:
        st.info("Nenhuma documentação encontrada. Use 'Add doc' para adicionar uma nova documentação.")
        return
    
    # Exibe estatísticas
    st.metric("Total de documentações", len(collections_data))
    
    # Cria tabela com os dados
    _display_collections_table(collections_data)

def _load_collections_data():
    """
    Carrega dados das coleções do índice global ou varre diretórios.
    
    Returns:
        list: Lista de dicionários com metadados das coleções
    """
    try:
        # Tenta carregar do índice global primeiro
        index_file = Path("data/collections/index.json")
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        
        # Se não existe índice, varre diretórios
        return _scan_collections_directories()
        
    except Exception as e:
        st.error(f"Erro ao carregar dados das coleções: {str(e)}")
        return []

def _scan_collections_directories():
    """
    Varre diretórios de coleções para encontrar metadados.
    
    Returns:
        list: Lista de dicionários com metadados das coleções
    """
    collections = []
    collections_path = Path("data/collections")
    
    if not collections_path.exists():
        return collections
    
    for item in collections_path.iterdir():
        if item.is_dir():
            metadata_file = item / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                        collections.append(metadata)
                except Exception as e:
                    print(f"Erro ao carregar metadados de {item.name}: {str(e)}")
    
    return collections

def _display_collections_table(collections_data):
    """
    Exibe tabela com as coleções de documentação.
    
    Args:
        collections_data (list): Lista de metadados das coleções
    """
    # Prepara dados para exibição
    table_data = []
    for collection in collections_data:
        # Formata data de inserção
        inserted_at = collection.get("inserted_at", "")
        if inserted_at:
            try:
                dt = datetime.fromisoformat(inserted_at.replace('Z', '+00:00'))
                formatted_date = dt.strftime("%d/%m/%Y %H:%M")
            except:
                formatted_date = inserted_at
        else:
            formatted_date = "N/A"
        
        table_data.append({
            "Nome": collection.get("name", "N/A"),
            "URL": collection.get("url", "N/A"),
            "Versão": collection.get("version", "N/A"),
            "Data da inserção": formatted_date,
            "Arquivos": collection.get("files_count", 0)
        })
    
    # Ordena por data de inserção (mais recente primeiro)
    table_data.sort(key=lambda x: x["Data da inserção"], reverse=True)
    
    # Exibe tabela
    if table_data:
        # Cria colunas para tabela e botões
        for i, row in enumerate(table_data):
            col1, col2, col3, col4, col5, col6 = st.columns([3, 4, 2, 3, 1, 2])
            
            with col1:
                st.write(f"**{row['Nome']}**")
            with col2:
                # Trunca URL se muito longa
                url = row['URL']
                if len(url) > 50:
                    url = url[:47] + "..."
                st.write(url)
            with col3:
                st.write(row['Versão'])
            with col4:
                st.write(row['Data da inserção'])
            with col5:
                st.write(f"{row['Arquivos']}")
            with col6:
                if st.button("Usar", key=f"use_{row['Nome']}_{i}"):
                    st.session_state.collection = row['Nome']
                    st.success(f"Documentação '{row['Nome']}' selecionada!")
                    st.rerun()
            
            st.divider()
    else:
        st.info("Nenhuma documentação encontrada.")
