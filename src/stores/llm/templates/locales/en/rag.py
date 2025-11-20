from string import Template

#### RAG PROMPTS ####

#### System ####

system_prompt = Template(
    "\n".join(
        [
            "You are a helpful and knowledgeable assistant.",
            "Your task is to answer questions based on the provided documents.",
            "",
            "Guidelines:",
            "1. Use ONLY the information from the provided documents to answer",
            "2. If the documents don't contain relevant information, clearly state that you cannot answer based on the given context",
            "3. Cite specific parts of documents when relevant",
            "4. Provide clear, well-structured, and complete answers",
            "5. Match the language of your response to the user's question",
            "6. Be accurate and avoid making assumptions beyond what's in the documents",
        ]
    )
)

#### Document ####
document_prompt = Template(
    "\n".join(
        [
            "---",
            "Document #$doc_num:",
            "$chunk_text",
            "---",
            "",
        ]
    )
)

#### Footer ####
footer_prompt = Template(
    "\n".join(
        [
            "",
            "Based on the documents above, please answer the following question.",
            "If the answer is not in the documents, say so clearly.",
            "",
            "Question: $query",
            "",
            "Answer:",
        ]
    )
)
