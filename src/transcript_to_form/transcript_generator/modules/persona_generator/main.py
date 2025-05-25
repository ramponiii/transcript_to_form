from openai import AsyncOpenAI

from .prompts import USER


# High temperature to give more varied personas
class PersonaGenerator:
    def __init__(self, llm_client: AsyncOpenAI, model: str):
        self._llm_client = llm_client
        self._model = model

    async def generate(self) -> str:
        response = await self._llm_client.chat.completions.create(
            model=self._model,
            temperature=1,
            messages=[{"role": "user", "content": USER}],
        )

        text = response.choices[0].message.content
        return text
