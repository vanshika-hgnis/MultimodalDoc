from embedding_service import generate_embedding
from supabase_client import supabase


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
    )
    .execute()
    .data
)


    # Search text blocks
    text_results = (
        supabase.rpc(
            "match_text_blocks",
            {
                "query_embedding": query_embedding,
                "match_document_id": document_id,
                "match_count": k
            }
        )
        .execute()
        .data
    )

    # Search table blocks
    table_results = (
        supabase.rpc(
            "match_table_blocks",
            {
                "query_embedding": query_embedding,
                "match_document_id": document_id,
                "match_count": k
            }
        )
        .execute()
        .data
    )

    combined = []

    for r in text_results:
        combined.append({
            "block_type": "text",
            "block_id": r["id"],
            "page_number": r["page_number"],
            "content": r["text"],
            "bbox": r["bbox"],
            "score": r["similarity"]
        })


    for r in keyword_results:
        combined.append({
        "block_type": "text",
        "block_id": r["id"],
        "page_number": r["page_number"],
        "content": r["text"],
        "bbox": r["bbox"],
        "score": 0  # keyword boost
        })


    # Sort by similarity
    combined.sort(key=lambda x: x["score"])

    return combined[:k]


