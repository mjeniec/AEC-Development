from ollama import chat
from retrieval import load_or_create_index, find_relevant_pages

# 1. Load the document
pages, embeddings = load_or_create_index()

# 2. Ask a question
question = "What is the minimum headroom required above stairs?"

# 3. Retrieve the most relevant pages
relevant_pages = find_relevant_pages(question, pages, embeddings)

# 4. Prepare the retrieved information for Qwen
context = "\n\n".join(
    f"PDF Page {page['pdf_page']}:\n{page['text']}"
    for page in relevant_pages
)

# 5. Send the question and retrieved information to Qwen
response = chat(
    model="qwen2.5:3b",
    options={"temperature": 0},
    messages=[
        {
            "role": "system",
            "content": (
                "You are a Building Regulations assistant. "
                "Answer using only the supplied document extracts. "
                "Always reference the relevant PDF page number. "
                "If the information is missing, say so."
            )
        },
        {
            "role": "user",
            "content": f"Document extracts:\n{context}\n\nQuestion: {question}"
        }
    ]
)

# 6. Display the answer
print("\nANSWER:\n")
print(response.message.content)

print("\nSOURCE PAGES:")
for page in relevant_pages:
    print(f"PDF page {page['pdf_page']}")