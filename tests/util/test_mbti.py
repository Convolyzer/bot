import pytest
from util.mbti import GuildMBTI
from core import Translator


@pytest.fixture
def guildmbti_instance(mocker):
    mocker.patch("core.Translator.__init__", return_value=None)
    mocker.patch("core.Translator.translate_to_en", return_value="text")

    translator = Translator()

    guildmbti = GuildMBTI(None, translator)

    expected_mbti = [{"label": "INTJ", "score": 0.8}, {"label": "ENTP", "score": 0.2}]

    mocker.patch.object(guildmbti, "pipeline_mbti", return_value=expected_mbti)

    return guildmbti


def test_handle_message_increment_message_counter(guildmbti_instance):
    msg_author_id = 123
    msg_content = "Bonjour, comment vas-tu?"
    guildmbti_instance.handle_message(msg_author_id, msg_content)
    assert guildmbti_instance.message_counters[msg_author_id] == 1


def test_get_message_mbti(guildmbti_instance):
    msg_content = "Bonjour, comment vas-tu?"
    result = guildmbti_instance.get_message_mbti(msg_content)
    assert result == {"INTJ": 0.8, "ENTP": 0.2}


def test_get_user_mbti_existing_user(guildmbti_instance):
    user_id = 123
    guildmbti_instance.user_mbtis[user_id] = {"INTJ": 0.8, "ENTP": 0.2}
    result = guildmbti_instance.get_user_mbti(user_id)
    assert result == "INTJ"


def test_get_user_mbti_non_existing_user(guildmbti_instance):
    user_id = 456
    result = guildmbti_instance.get_user_mbti(user_id)
    assert result is None


def test_get_guild_mbtis(guildmbti_instance):
    guildmbti_instance.user_mbtis = {
        1: {"INTJ": 0.8, "ENTP": 0.2},
        2: {"INTP": 0.6, "ENTJ": 0.4},
        3: {"INFJ": 0.7, "ESTP": 0.3},
    }
    result = guildmbti_instance.get_guild_mbtis()
    assert result == {"INTJ": 1, "INTP": 1, "INFJ": 1}
