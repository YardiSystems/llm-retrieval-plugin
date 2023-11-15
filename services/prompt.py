from typing import Any, Dict, List

async def get_prompt_response(prompt: str, text_chunks: List[str], llm_model: str = None) -> str:
    response = ""
    if not llm_model:
        response = await call_chatgpt_api(prompt, text_chunks)

    return response


def apply_prompt_template(question: str) -> str:
    """
        A helper function that applies additional template on user's question.
        Prompt engineering could be done here to improve the result. Here I will just use a minimal example.
    """
    prompt = f"""
        By considering above input from me, answer the question: {question}
    """
    return prompt


async def call_chatgpt_api(user_prompt: str, text_chunks: List[str]) -> Dict[str, Any]:
    """
    Call chatgpt api with user's prompt and retrieved text chunks.
    """

    from services.openai import get_chat_completion_async

    # Send a request to the GPT-3 API
    messages = list(
        map(lambda chunk: {
            "role": "user",
            "content": chunk
        }, text_chunks))
    full_prompt = apply_prompt_template(user_prompt)
    messages.append({"role": "user", "content": full_prompt})
    response = await get_chat_completion_async(
        messages=messages
    )
    return response
