from datetime import datetime, timedelta
from transformers import pipeline
import pytest

from util.moods import GuildMoods  # Noqa

# Fixtures


@pytest.fixture
def guildmoods_instance(mocker):
    guildmoods = GuildMoods(None, None)

    # Define the message content (author_id, content, msg_id, date)
    current_time = datetime.now()

    msg1 = (111, "j'ai peur, je suis triste", 1, current_time)
    msg1_mood = [
        {"label": "fear", "score": 0.9997491240501404},
        {"label": "sadness", "score": 0.00013639261305797845},
        {"label": "surprise", "score": 3.117524829576723e-05},
        {"label": "anger", "score": 2.8739656045218e-05},
        {"label": "joy", "score": 2.8585869586095214e-05},
        {"label": "love", "score": 2.596615013317205e-05},
    ]
    msg1_sentiment = [
        {"label": "Negative", "score": 0.9699232578277588},
        {"label": "Neutral", "score": 0.018443167209625244},
        {"label": "Positive", "score": 0.011633623391389847},
    ]

    msg2 = (111, "je suis hyper emballé !", 2, current_time - timedelta(hours=25))
    msg2_mood = [
        {"label": "joy", "score": 0.9666299223899841},
        {"label": "surprise", "score": 0.030188731849193573},
        {"label": "love", "score": 0.0017519814427942038},
        {"label": "anger", "score": 0.0009560974431224167},
        {"label": "fear", "score": 0.0003136172890663147},
        {"label": "sadness", "score": 0.00015963378245942295},
    ]
    msg2_sentiment = [
        {"label": "Positive", "score": 0.9239315390586853},
        {"label": "Negative", "score": 0.046250421553850174},
        {"label": "Neutral", "score": 0.029818061739206314},
    ]

    msg3 = (222, "angry", 3, current_time)
    msg3_mood = [
        {"label": "anger", "score": 0.9975276589393616},
        {"label": "fear", "score": 0.001394064398482442},
        {"label": "sadness", "score": 0.0006730123423039913},
        {"label": "joy", "score": 0.00024746180861257017},
        {"label": "love", "score": 0.00013722728181164712},
        {"label": "surprise", "score": 2.0611565560102463e-05},
    ]
    msg3_sentiment = [
        {"label": "Negative", "score": 0.9331047534942627},
        {"label": "Neutral", "score": 0.061473116278648376},
        {"label": "Positive", "score": 0.005422092974185944},
    ]

    # Handle message and mock the result!!
    mocker.patch.object(guildmoods, "analyzer", return_value=msg1_mood)
    mocker.patch.object(guildmoods, "sentiment_classifier", return_value=msg1_sentiment)
    guildmoods.handle_message(*msg1)

    mocker.patch.object(guildmoods, "analyzer", return_value=msg2_mood)
    mocker.patch.object(guildmoods, "sentiment_classifier", return_value=msg2_sentiment)
    guildmoods.handle_message(*msg2)

    mocker.patch.object(guildmoods, "analyzer", return_value=msg3_mood)
    mocker.patch.object(guildmoods, "sentiment_classifier", return_value=msg3_sentiment)
    guildmoods.handle_message(*msg3)

    return guildmoods


# Tests


def test_get_user_positivity(guildmoods_instance):
    assert guildmoods_instance.get_user_positivity(111) > 0.4


def test_get_user_pov(guildmoods_instance):
    assert guildmoods_instance.get_user_pov(111) > 0.2


def test_get_user_mood(guildmoods_instance):
    assert guildmoods_instance.get_user_mood(111) == {"peur": 1, "joie": 1}


# BAD


def test_get_message_pov(guildmoods_instance):
    assert guildmoods_instance.get_message_pov(9, "joyeux") > 0.5


def test_get_message_positivity(mocker, guildmoods_instance):
    msg_sentiment = [
        {"label": "Negative", "score": 0.974903404712677},
        {"label": "Neutral", "score": 0.015142282471060753},
        {"label": "Positive", "score": 0.009954242035746574},
    ]
    mocker.patch.object(
        guildmoods_instance, "sentiment_classifier", return_value=msg_sentiment
    )
    assert guildmoods_instance.get_message_positivity(9, "je suis triste") < 0.25


def test_get_message_mood(mocker, guildmoods_instance):
    msg_mood = [
        {"label": "sadness", "score": 0.9997403025627136},
        {"label": "fear", "score": 7.415805157506838e-05},
        {"label": "surprise", "score": 6.697947537759319e-05},
        {"label": "anger", "score": 4.27668601332698e-05},
        {"label": "joy", "score": 3.9327314880210906e-05},
        {"label": "love", "score": 3.6444664146983996e-05},
    ]
    mocker.patch.object(guildmoods_instance, "analyzer", return_value=msg_mood)
    score_mood, _ = guildmoods_instance.get_message_mood(9, "je suis triste")
    assert score_mood > 0.8


# END BAD


def test_get_pie_chart_util_pov(guildmoods_instance):
    assert guildmoods_instance.get_guild_pov() == ({"Subjectif": 1, "Objectif": 2})


def test_get_pie_chart_util_positivity(guildmoods_instance):
    assert guildmoods_instance.get_guild_positivity() == ({"Positif": 1, "Negatif": 2})


def test_get_pie_chart_util_mood(guildmoods_instance):
    assert guildmoods_instance.get_guild_mood() == ({"joie": 1, "colère": 1, "peur": 1})


def test_get_mood(guildmoods_instance):
    assert guildmoods_instance.get_guild_mood() == ({"joie": 1, "colère": 1, "peur": 1})


def test_get_positivity(guildmoods_instance):
    assert guildmoods_instance.get_guild_positivity() == ({"Positif": 1, "Negatif": 2})


def test_get_pov(guildmoods_instance):
    assert guildmoods_instance.get_guild_pov() == ({"Subjectif": 1, "Objectif": 2})


def test_garbage_collector(guildmoods_instance):
    # Ensure two messages older than 24 hours are removed for user ID 111
    assert len(guildmoods_instance.user_messages[111]) == 2
    assert len(guildmoods_instance.user_messages[222]) == 1

    guildmoods_instance.garbage_collector()

    # Ensure one message with user_id 111 is removed after garbage collection
    assert len(guildmoods_instance.user_messages[111]) == 1

    # Ensure one message with user_id 222 is retained after garbage collection
    assert len(guildmoods_instance.user_messages[222]) == 1
