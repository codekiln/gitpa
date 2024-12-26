from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv



def test_openai_structured_outputs():
    load_dotenv()
    client = OpenAI()

    class Step(BaseModel):
        explanation: str
        output: str

    class MathReasoning(BaseModel):
        steps: list[Step]
        final_answer: str

    system_prompt = "You are a helpful math tutor. Guide the user through the solution step by step."
    print(f"{system_prompt=}")
    user_prompt = "how can I solve 8x + 7 = -23"
    print(f"{user_prompt=}")

    print("Calling OpenAI ...")
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=MathReasoning,
    )

    math_reasoning = completion.choices[0].message.parsed
    print(f"{math_reasoning=}")

def main():
    result = test_openai_structured_outputs()

if __name__ == "__main__":
    main()