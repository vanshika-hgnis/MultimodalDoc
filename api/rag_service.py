import os
from ollama import Client
from embedding_service import generate_embedding
from supabase_client import supabase

client = Client(
    host="https://ollama.com",
    headers={
        "Authorization": "Bearer " + os.getenv("OLLAMA_API_KEY")
    }
)

def retrieve_evidence(document_id: str, query: str, k: int = 8):

    query_embedding = generate_embedding(query)

    keyword_results = (
        supabase.rpc(
            "match_text_blocks_keyword",
            {
                "match_document_id": document_id,
                "query_text": query,
                "match_count": k
            }
        ).execute().data
    )

    text_results = (
        supabase.rpc(
            "match_text_blocks",
            {
                "query_embedding": query_embedding,
                "match_document_id": document_id,
                "match_count": k
            }
        ).execute().data
    )

    table_results = (
        supabase.rpc(
            "match_table_blocks",
            {
                "query_embedding": query_embedding,
                "match_document_id": document_id,
                "match_count": k
            }
        ).execute().data
    )

    combined = []

    for r in text_results:
        combined.append({
            "block_type": "text",
            "block_id": r["id"],
            "page_number": r["page_number"],
            "content": r["text"],
            "bbox": r["bbox"],
            "score": float(r["similarity"])
        })

    for r in table_results:
        combined.append({
            "block_type": "table",
            "block_id": r["id"],
            "page_number": r["page_number"],
            "content": r["table_markdown"],
            "bbox": r["bbox"],
            "score": float(r["similarity"])
        })

    for r in keyword_results:
        for item in combined:
            if item["block_id"] == r["id"]:
                item["score"] += float(r.get("rank", 0)) * 0.6
                break
        else:
            combined.append({
                "block_type": "text",
                "block_id": r["id"],
                "page_number": r["page_number"],
                "content": r["text"],
                "bbox": r["bbox"],
                "score": 0.15
            })

    unique = {}
    for item in combined:
        key = (item["page_number"], item["content"].strip())
        if key not in unique:
            unique[key] = item

    combined = list(unique.values())
    combined.sort(key=lambda x: x["score"], reverse=True)

    return combined[:k]


def generate_answer(document_id, query, k=8):

    evidence = retrieve_evidence(document_id, query, k)

    if not evidence:
        return {
            "answer": "No relevant context found in document.",
            "sources": []
        }
        
    context = "\n\n".join([
    f"[{i+1}] Page {e['page_number']} | {e['block_type']}\n{e['content']}"
    for i, e in enumerate(evidence)])

    messages = [
    {"role": "system", "content": "Answer ONLY from the context. After each sentence, add citations like [1] using the provided source numbers. If unknown, say you don't know."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{query}"}
    ]

    response = client.chat(
        model="gpt-oss:20b",
        messages=messages
    )

    return {
        "answer": response["message"]["content"],
        "sources": evidence
    }