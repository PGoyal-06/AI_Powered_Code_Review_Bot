from openai import OpenAI


def analyze_code(code_diff, filename, client: OpenAI):
    """Generate code review using OpenAI API."""
    prompt = (
        f"You are an experienced software engineer. Please review the changes made to the file `{filename}` "
        "and provide constructive feedback, potential improvements, and identify any issues.\n\n"
        f"```diff\n{code_diff}\n```"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful code reviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[AI Review] Error generating review for {filename}: {e}")
        return None
