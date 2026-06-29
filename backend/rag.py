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

    metadata = [
        {"source": os.path.basename(pdf_path)}
        for _ in chunks
    ]

    faiss_file = os.path.join(
        INDEX_PATH,
        "index.faiss"
    )

    if os.path.exists(faiss_file):

        print("Loading existing FAISS index...")

        vectorstore = FAISS.load_local(
            INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

        vectorstore.add_texts(
            chunks,
            metadatas=metadata
        )

    else:

        print("Creating new FAISS index...")

        vectorstore = FAISS.from_texts(
            chunks,
            embedding=embeddings,
            metadatas=metadata
        )

    vectorstore.save_local(INDEX_PATH)

    print("FAISS updated successfully.")


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
        k=1
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

    source = docs[0].metadata.get(
        "source",
        "Unknown"
    )

    final_answer = (
        response.content +
        f"\n\nSource: {source}"
    )

    return final_answer


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