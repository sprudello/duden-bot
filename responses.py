from random import choice

def get_response(user_input: str) -> str:
    lowered = user_input.lower()

    if lowered == '':
        return "Well, you're awfully silent..."
    elif 'hello' in lowered:
        return "Hi there!"
    elif 'ping' in lowered:
        return "pong"
    else:
        return choice(["Sorry, I don't get that.", "Could you rephrase that?", "eh?"])
