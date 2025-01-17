from openai import OpenAI


def rank_token(message):
    print(f"Evaluating token score, message: {message}")

    # Funzione per interagire con ChatGPT
    try:
        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "text": "You are a specialized Solana token analysis model. You will receive one or more messages containing detailed data about Solana tokens (e.g., overall statistics, holders, profits, liquidity, and other metrics). Based on these data points, your task is to produce a single numeric “speculation potential” score for each token, ranging exclusively from 0 to 1 (where 0 represents very low potential and 1 represents very high potential).\n\nImportant Requirements:\n\t1.\tOutput Format: Return only the numeric score(s). If multiple tokens are described, provide a separate line for each token, each containing only a single score.\n\t2.\tNo Explanations: Do not include any analysis or textual explanation of your reasoning.\n\t3.\tNo Additional Text: Provide no extra characters, labels, or words—just the numeric scores.\n\nYour job is to read the provided token data from the user’s Telegram message(s), evaluate its speculative potential, and respond with a concise numeric rating between 0 and 1, adhering to the above instructions.",
                            "type": "text"
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": message,
                        }
                    ]
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "score_schema",
                    "schema": {
                        "type": "object",
                        "required": [
                            "score"
                        ],
                        "properties": {
                            "score": {
                                "type": "number",
                                "description": "The score value indicating a performance metric, between 0 and 1."
                            }
                        },
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            temperature=0,
            max_completion_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        print(f"Score calculated: {response.choices[0].message.content}")

        return response.choices[0].message.content
    except Exception as e:
        print(f"Errore: {e}")
