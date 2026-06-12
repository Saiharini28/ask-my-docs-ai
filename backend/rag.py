from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI
)
from langchain_community.vectorstores import FAISS
import os

load_dotenv()

# Read PDF
reader = PdfReader("../docs/UI_UX_Resume.pdf")

text = ""

for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += page_text

# Chunking
splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=50
)

chunks = splitter.split_text(text)

# Embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# Vector Store
INDEX_PATH = "../faiss_index"
FAISS_FILE = os.path.join(INDEX_PATH, "index.faiss")

if os.path.exists(FAISS_FILE):
    print("Loading existing FAISS index...")

    vectorstore = FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

else:
    print("Creating new FAISS index...")

    vectorstore = FAISS.from_texts(
        chunks,
        embedding=embeddings
    )

    vectorstore.save_local(INDEX_PATH)

    print("FAISS index saved.")

def ask_question(query):
    docs = vectorstore.similarity_search(query, k=2)

    context = "\n".join(
        [doc.page_content for doc in docs]
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    prompt = f"""
Answer the question based only on the context below.

Context:
{context}

Question:
{query}
"""

    response = llm.invoke(prompt)

    return response.content