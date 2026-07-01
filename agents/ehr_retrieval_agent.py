import json
from typing import Dict, Any
from domain.schemas import EHRFindings, EHRChunk
from agents.base_agent import BaseAgent
from infrastructure.vector_store import VectorStore

class EHRRetrievalAgent(BaseAgent):
    def __init__(self, version: str = "v1.0"):
        super().__init__("ehr_retrieval_agent", version)
        self.vector_store = VectorStore()
        
    async def retrieve(self, patient_id: str, query_params: Dict[str, Any], clinical_question: str) -> EHRFindings:
        # 1. Retrieve from VectorStore
        query = query_params.get("keywords", [clinical_question])
        if isinstance(query, list):
            query = " ".join(query)
            
        retrieved_raw = self.vector_store.search(patient_id=patient_id, query=query, top_k=5)
        
        # 2. Re-rank or filter
        retrieved_chunks = []
        for r in retrieved_raw:
            if r["distance"] < 0.6:  # arbitrary threshold
                retrieved_chunks.append(
                    EHRChunk(
                        chunk_id=r["chunk_id"],
                        document=r["document"],
                        metadata=r["metadata"],
                        distance=r["distance"]
                    )
                )
                
        # 3. Ask LLM to summarize using LangChain structured output
        # Because we only get back summary, key_findings, citations from LLM, we inject the chunks
        chunks_json = json.dumps([c.model_dump() for c in retrieved_chunks], indent=2)
        user_prompt = f"Clinical Question: {clinical_question}\nRetrieved EHR Chunks:\n{chunks_json}"
        
        from pydantic import BaseModel
        from typing import List
        class EHRResponse(BaseModel):
            summary: str
            key_findings: List[str]
            citations: List[str]
            
        try:
            llm_response = await self.run_structured(user_prompt, EHRResponse)
            return EHRFindings(
                retrieved_chunks=retrieved_chunks,
                summary=llm_response.summary,
                key_findings=llm_response.key_findings,
                citations=llm_response.citations
            )
        except Exception as e:
            raise RuntimeError(f"Failed to execute EHRRetrievalAgent: {str(e)}")
