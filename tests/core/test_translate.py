from core import Translator


def test_translate_to_en(mocker):
    mocker.patch("core.Translator.__init__", return_value = None)
    mocker.patch("core.Translator.translate_to_en", return_value = "text")
    #test
    translator = Translator()
    texts = ("Salut, ça va?", "Tu fais quoi?", "J'aime Python", "J'aime Python")
    for text in texts:
        res = translator.translate_to_en(text)
        assert res is not None
        assert len(res) > 0