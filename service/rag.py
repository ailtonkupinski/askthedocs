"""
Serviço RAG (Retrieval-Augmented Generation)

Este módulo implementa o sistema RAG que combina busca semântica
com geração de texto para responder perguntas sobre documentação.
Utiliza embeddings para encontrar contexto relevante e um LLM para gerar respostas.
"""

import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class RAGService:
    """
    Serviço RAG para processamento de documentação.
    
    Funcionalidades:
    - Carrega documentos de uma coleção
    - Cria embeddings usando HuggingFace
    - Constrói índice vetorial com FAISS
    - Responde perguntas usando contexto relevante
    """
    
    def __init__(self):
        # Modelo de embeddings para representação semântica dos documentos
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"  # Modelo leve e eficiente
        )

        # LLM para geração de respostas (Groq API)
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="openai/gpt-oss-20b"  # Modelo otimizado para velocidade
        )

        # Divisor de texto para criar chunks de tamanho adequado
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,      # Tamanho máximo de cada chunk
            chunk_overlap=200,    # Sobreposição entre chunks para contexto
        )

        # Armazena o índice vetorial e a cadeia de perguntas-respostas
        self.vectorstore = None
        self.qa_chain = None

    def load_collection(self, collection_name):
        """
        Carrega uma coleção de documentos e prepara o sistema RAG.
        
        Args:
            collection_name (str): Nome da coleção a ser carregada
            
        Returns:
            bool: True se carregou com sucesso, False caso contrário
        """
        collection_path = f"data/collections/{collection_name}"

        # Carrega todos os arquivos .md da coleção
        loader = DirectoryLoader(
            collection_path, 
            glob="**.md", 
            loader_cls=TextLoader, 
            loader_kwargs={"encoding": "utf-8"}
        )

        documents = loader.load()

        if not documents:
            return False

        # Divide os documentos em chunks menores para melhor processamento
        texts = self.text_splitter.split_documents(documents)

        # Cria o índice vetorial usando FAISS
        self.vectorstore = FAISS.from_documents(texts, self.embeddings)

        # Template para o prompt do LLM
        template = """
            Você é um assistente de documentação. Use o contexto fornecido para responder à pergunta do usuário.
            Se você não souber a resposta, diga que não sabe.
            Não tente inventar uma resposta. Se você não souber, diga que não sabe.

            Contexto: {context}
            
            Pergunta: {question}
        """

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

        # Cria a cadeia de perguntas-respostas
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),  # Busca 3 chunks mais relevantes
            chain_type_kwargs={"prompt": prompt}
        )

        return True

    def ask_question(self, question):
        """
        Responde uma pergunta usando o sistema RAG.
        
        Args:
            question (str): Pergunta do usuário
            
        Returns:
            str: Resposta gerada pelo sistema
        """
        if not self.qa_chain:
            return "Nenhuma coleção carregada"
        
        try:
            # Usa a cadeia RAG para buscar contexto e gerar resposta
            result = self.qa_chain.invoke({"query": question})

            # Extrai a resposta do resultado
            if isinstance(result, dict):
                return result.get("result") or result.get("output_text") or str(result)
            return result
        except Exception as e:
            return f"Erro ao responder a pergunta: {str(e)}"