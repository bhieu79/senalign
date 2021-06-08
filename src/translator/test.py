from client import Translator


if __name__ == '__main__':
    text = """
    Hello, I am Tran Quang Khai. I live in Bac Ninh.
    """
    translator = Translator()

    trans = translator.translate(text=text, src='en', dest='vi')
    print(trans)
