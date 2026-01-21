from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Initialize simple embedding model (runs locally)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = None

def ingest_document(file_path: str):
    global vector_store
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = splitter.split_documents(docs)
    
    # Create/Update Vector Store
    vector_store = Chroma.from_documents(documents=splits, embedding=embeddings)
    return "Document processed successfully."

def query_vector_db(query: str):
    if not vector_store:
        return None
    results = vector_store.similarity_search(query, k=3)
    return "\n".join([doc.page_content for doc in results])