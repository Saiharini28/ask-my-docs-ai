from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
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
    chunk_size = 200,
    chunk_overlap = 50
)

chunks = splitter.split_text(text)

print("Total Chunks:", len(chunks))

# Embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# Store in FAISS
vectorstore = FAISS.from_texts(
    chunks,
    embedding=embeddings
)

query = "What skills does this person have?"

docs = vectorstore.similarity_search(query, k=2)

print("\nTOP RETRIEVED CHUNKS:\n")
for i, doc in enumerate(docs):
    print(f"Chunk {i+1}:\n{doc.page_content}\n")

# Build context properly
context = "\n".join([doc.page_content for doc in docs])

# LLM
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

print("\nAI ANSWER:\n")
print(response.content)