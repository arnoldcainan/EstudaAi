import os
from typing import Dict, List, Optional
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from .deepseek import DeepSeekLLM  # Importa sua conexão existente DeepSeek


# --- 1. Definição do Esquema de Saída (Pydantic para o QCM) ---

class Questao(BaseModel):
    """Modelo Pydantic para uma única questão de múltipla escolha."""
    pergunta: str = Field(description="A pergunta de múltipla escolha baseada no texto.")
    opcoes: List[str] = Field(description="Lista de 4 opções de resposta, incluindo a correta.")
    resposta_correta: str = Field(description="A resposta correta (deve ser idêntica a uma das opções).")


class QCM_Output(BaseModel):
    """Modelo Pydantic para o conjunto completo de questões."""
    questoes: List[Questao] = Field(description="Lista contendo exatamente 5 objetos de Questão.")


# --- 2. Função Central de Leitura de Documentos ---

def load_document(file_path: str) -> str:
    """Carrega o conteúdo de um documento (PDF/DOCX/TXT) e o retorna como texto simples."""
    file_extension = os.path.splitext(file_path)[1].lower()

    # 2.1. Seleciona o Loader com base na extensão
    if file_extension == '.pdf':
        # Usa PyPDFLoader para PDFs
        loader = PyPDFLoader(file_path)
    elif file_extension == '.docx':
        # Usa Unstructured para DOCX (requer dependências como python-docx)
        loader = UnstructuredWordDocumentLoader(file_path)
    elif file_extension == '.txt':
        # Usa TextLoader para TXT
        loader = TextLoader(file_path, encoding='utf-8')
    else:
        raise ValueError(f"Extensão de arquivo não suportada: {file_extension}")

    docs = loader.load()

    # 2.2. Junta o conteúdo de todas as páginas em uma string
    full_text = " ".join(doc.page_content for doc in docs)
    return full_text


# --- 3. Função de Processamento Completo de IA (Síncrono) ---

def process_study_material(file_path: str, titulo: Optional[str] = "Estudo Gerado por IA") -> Dict:
    """
    Função principal que realiza o resumo e a geração de QCM de forma síncrona.

    :param file_path: Caminho local do arquivo.
    :param titulo: Título fornecido pelo usuário.
    :return: Dicionário com 'resumo', 'qcm' (JSON) e 'status'.
    """
    try:
        # 3.1. CARREGAR E DIVIDIR O DOCUMENTO
        full_text = load_document(file_path)

        # Usamos um splitter para garantir que grandes textos caibam no contexto do LLM
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200
        )
        texts = text_splitter.create_documents([full_text])

        # Se houver muitos chunks, usamos apenas os primeiros/mais representativos para o MVP
        context_text = texts[0].page_content if texts else full_text[:8000]  # Limita para o MVP

        llm = DeepSeekLLM()  # Inicializa sua conexão DeepSeek (usando DeepSeekLLM do deepseek.py)

        # 3.2. GERAÇÃO DE RESUMO
        resumo_prompt = PromptTemplate.from_template(
            "Você é um tutor especializado. Crie um resumo conciso, didático e focado em pontos-chave a partir do texto a seguir. O resumo deve ter no máximo 300 palavras. TEXTO: {text}"
        )
        resumo_chain = resumo_prompt | llm
        resumo = resumo_chain.invoke({"text": context_text})

        # 3.3. GERAÇÃO DE QCM (Questionário de Múltipla Escolha)

        # Cria o parser Pydantic
        parser = PydanticOutputParser(pydantic_object=QCM_Output)

        qcm_prompt = PromptTemplate.from_template(
            "Com base no texto fornecido, gere **EXATAMENTE 5** questões de múltipla escolha (QCM). Cada questão deve ter **4 opções** de resposta (A, B, C, D) e uma única resposta correta. Use a formatação JSON específica do esquema Pydantic. TEXTO: {text}\n\n{format_instructions}"
        )

        # O prompt final inclui as instruções de formatação do Pydantic
        qcm_chain = qcm_prompt.partial(format_instructions=parser.get_format_instructions()) | llm

        qcm_raw = qcm_chain.invoke({"text": resumo})  # Usamos o resumo como base para as perguntas

        # Tenta parsear a saída JSON do LLM
        qcm_data = parser.parse(qcm_raw)

        return {
            "status": "completed",
            "titulo": titulo,
            "resumo": resumo,
            "qcm_json": qcm_data.dict()  # Converte o objeto Pydantic para dicionário
        }

    except ValueError as e:
        return {"status": "failed", "error": f"Erro de validação: {e}"}
    except Exception as e:
        # Captura DeepSeekError ou erros de conexão
        return {"status": "failed", "error": f"Erro de Processamento de IA: {e}"}

# --- FIM DO SERVIÇO ---