from config import GEMINI_API_KEY
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import os

vector_store = None
rag_chain = None

async def initialize_rag_models():
    global vector_store, rag_chain

    loader = DirectoryLoader("data", glob="**/*.txt", loader_cls=TextLoader)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vector_store = FAISS.from_documents(chunks, embeddings)

    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    prompt = PromptTemplate(
        template="""
        Siz Mohirdev haqida ma'lumot beruvchi yordamchisiz.
        Savol: {question}
        Matnlar: {context}
        Javobni faqat yuqoridagi matnlarga asoslanib o'zbek tilida yozing.
        """,
        input_variables=["context", "question"]
    )

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)

    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt}
    )

async def query_model(question: str) -> str:
    global rag_chain
    result = rag_chain.invoke({"query": question})
    return result["result"] if result and "result" in result else "Javob topilmadi."
