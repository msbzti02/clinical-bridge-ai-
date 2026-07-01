import os
import chromadb
from typing import List, Dict, Any
from domain.schemas import EHRRecord, RecordType

class VectorStore:
    def __init__(self, persist_directory: str = "chroma_db"):
        self.persist_directory = persist_directory
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name="ehr_records",
            metadata={"hnsw:space": "cosine"}
        )
        
    def _chunk_text(self, text: str, max_tokens: int = 512, overlap: int = 50) -> List[str]:
        # A simple whitespace chunker that roughly approximates tokens
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + max_tokens])
            chunks.append(chunk)
            i += max_tokens - overlap
            if i >= len(words):
                break
        return chunks

    def add_ehr_records(self, records: List[EHRRecord]):
        documents = []
        metadatas = []
        ids = []
        
        for record in records:
            base_metadata = {
                "patient_id": str(record.patient_id),
                "record_id": str(record.record_id),
                "record_type": record.record_type.value,
                "timestamp": record.timestamp.isoformat() + "Z",
                "source_facility": record.source_facility or "Unknown"
            }
            
            if record.record_type == RecordType.visit_note:
                content_str = str(record.content)
                chunks = self._chunk_text(content_str)
                for idx, chunk in enumerate(chunks):
                    documents.append(chunk)
                    meta = base_metadata.copy()
                    meta["chunk_index"] = idx
                    meta["total_chunks"] = len(chunks)
                    metadatas.append(meta)
                    ids.append(f"{record.record_id}_{idx}")
            else:
                # Labs, meds, problems - do not chunk
                documents.append(str(record.content))
                meta = base_metadata.copy()
                meta["chunk_index"] = 0
                meta["total_chunks"] = 1
                metadatas.append(meta)
                ids.append(str(record.record_id))
                
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

    def search(self, patient_id: str, query: str, top_k: int = 5, record_type: str = None) -> List[Dict[str, Any]]:
        where_filter = {"patient_id": patient_id}
        if record_type:
            where_filter["record_type"] = record_type
            
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter
        )
        
        if not results["documents"] or not results["documents"][0]:
            return []
            
        retrieved = []
        for i in range(len(results["documents"][0])):
            retrieved.append({
                "chunk_id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if "distances" in results and results["distances"] else 0.0
            })
            
        return retrieved
