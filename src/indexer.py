import chromadb
from sentence_transformers import SentenceTransformer


class DocumentIndexer:

    def __init__(self, collection_name="technical_documents"):
        # Load the embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Create a local ChromaDB database
        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        # Create or reuse the document collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks):
        if not chunks:
            return

        # Convert document text into numerical vectors
        texts = [chunk.content for chunk in chunks]
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        ).tolist()

        # Store documents, vectors, and metadata
        self.collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=texts,
            embeddings=embeddings,
            metadatas=[
                {
                    "parent_doc": chunk.parent_doc,
                    "heading": str(
                        chunk.metadata.get("heading", "Unknown")
                    )
                }
                for chunk in chunks
            ]
        )

    def search(self, query, top_k=5):
        # Convert the search question into a vector
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        ).tolist()

        # Find the closest document vectors
        return self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, self.collection.count())
        )
