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

INDEX_PATH = "../faiss_index"

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)


def process_pdf(pdf_path):
    """
    Read PDF -> Chunk -> Embed -> Save FAISS
    """

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=50
    )

    chunks = splitter.split_text(text)

    vectorstore = FAISS.from_texts(
        chunks,
        embedding=embeddings
    )

    vectorstore.save_local(INDEX_PATH)

    print("FAISS index saved successfully.")


def load_vectorstore():

    faiss_file = os.path.join(
        INDEX_PATH,
        "index.faiss"
    )

    if not os.path.exists(faiss_file):
        raise Exception(
            "No FAISS index found. Upload a PDF first."
        )

    return FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


def ask_question(query):

    vectorstore = load_vectorstore()

    docs = vectorstore.similarity_search(
        query,
        k=2
    )

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


# Initial PDF setup (first run only)

faiss_file = os.path.join(
    INDEX_PATH,
    "index.faiss"
)

if not os.path.exists(faiss_file):

    print("Creating initial FAISS index...")

    process_pdf("../docs/UI_UX_Resume.pdf")

else:

    print("Loading existing FAISS index...")