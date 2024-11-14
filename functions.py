def to_good_text(text: str):
    text = text.replace('.', '\.')
    text = text.replace('-', '\-')
    text = text.replace('+', '\+')
    return text
