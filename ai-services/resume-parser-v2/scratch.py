import asyncio
from llm.qwen_callback import QwenCallbackLLM
async def main():
    qwen = QwenCallbackLLM()
    text = 'I built a react and node.js web application for a hackathon. My skills include python, java, c++, and docker. I also have soft skills like leadership and communication.'
    res = await qwen.classify_uncertain_paragraph(text)
    print(res)
asyncio.run(main())
