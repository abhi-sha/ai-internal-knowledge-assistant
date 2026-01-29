import os
from openai import OpenAI 
from app.core.config import GROQ_API_KEY
from openai import BadRequestError

_client=None

def get_llm_client():
    global _client

    if _client is None:
        _client=OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )

    return _client


def generate_answer(prompt:str)->str:
    
    _client=get_llm_client()
    try:
        response=_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role":"system","content": "You are a helpful internal knowledge assistant."},
                {"role":"user","content":prompt}],
            temperature=0.2)

        return response.choices[0].message.content.strip()
    except BadRequestError as e:
        print("LLM ERROR",e.response.json())
        raise
