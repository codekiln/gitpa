import os
from dotenv import load_dotenv
from openai import OpenAI

def test_openai_connectivity():
    load_dotenv()
    client = OpenAI(
        # this is the default and can be omitted
        # api_key=os.environ.get("OPENAI_API_KEY")
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
        model="gpt-4o-mini",
    )
    print(chat_completion)

def main():
    test_openai_connectivity()

if __name__ == "__main__":
    main()