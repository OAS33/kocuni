import openai
from json import load
file = open("config.json", "r", encoding="utf-8")
config = load(file)

openai.api_key = config["BACKEND"]["AI"]["OPENAI_API_KEY"]


def get_completion(prompt, model):
    data = openai.Completion.create(model=model,
                                    prompt=prompt,
                                    temperature=0.45,
                                    max_tokens=2049 -
                                    round(len(prompt) / 4 * 3),
                                    top_p=1,
                                    frequency_penalty=0.2,
                                    presence_penalty=0.2,
                                    stop=["⚿"])
    return data["choices"][0]["text"], data["usage"]["total_tokens"]
