import pytest
from typing import Dict
from util.summary import Summarizer  # Noqa


# Pipeline tools

def topic_pipeline_output(scores: Dict[str, float]):
    res = []
    for label, score in scores.items():
        res.append({"label": label, "score": score})
    return [res]


def summary_pipeline_output(text: str):
    res = [{"summary_text": text}]
    return res


# Fixture

@pytest.fixture
def summarizer_instance():
    summ = Summarizer(None, None)
    return summ


def messages():
    current_time = 1000000000.000
    chat_messages = [
        ("SepanBot",
         "Salut les gars ! J'ai jeté un coup d'œil au programme du master informatique et franchement, je suis hyper emballé ! Ça a l'air tellement passionnant, vous ne trouvez pas ?",
         current_time),
        ("YaBot",
         "Ah, la galère... Franchement, je n'aime vraiment pas ce master et je suis vraiment pas sûr de ne pas être taillé pour ça. Trop de maths, trop de théorie... C'est juste une torture.",
         current_time + 10),
        ("HagBot",
         "Hmm, je suis d'accord avec Sepanta sur certains points. Le Master semble intéressant , mais je comprends aussi tes préoccupations, Yanis. C'est vrai que le programme peut sembler un peu intimidant.",
         current_time + 15),
        ("JBot",
         "Le contenu du master est assez dense, mais c'est juste un ensemble de connaissances et de compétences à acquérir. Rien de plus, rien de moins.",
         current_time + 20),
        ("SepanBot",
         "Exactement ! Je suis sûr qu'une fois qu'on plongera dedans, on va adorer. Puis, pensez aux opportunités de carrière incroyables qui s'ouvrent à nous grâce à ce master !",
         current_time + 25),
        ("YaBot",
         "J'espère que tu as raison, Sepanta. Pour l'instant, je suis juste un peu découragé par tout ça. J'ai l'impression que ça va être un vrai calvaire",
         current_time + 30),
        ("HagBot",
         "Mais peut-être que ce sera pas aussi difficile que tu le penses. Il suffit de prendre les choses une étape à la fois",
         current_time + 35),
        ("JBot",
         "Hagop a raison. Il ne faut pas se laisser submerger par l'ampleur du programme. Il suffit de rester concentré et de travailler dur",
         current_time + 40),
        ("SepanBot", "C'est Magnifique le master ! Une fois qu'on sera dedans, la vie va juste être belle !",
         current_time + 45),
        ("YaBot",
         "J'espère que tu as raison. Je vais essayer de garder ça à l'esprit. Mais pour l'instant, je suis juste un peu inquiet",
         current_time + 50),
        ("HagBot",
         "Ne t'en fais pas. On est tous là pour se soutenir mutuellement. Si tu as besoin d'aide ou juste besoin de parler, n'hésite pas",
         current_time + 55),
        ("JBot", "Tout à fait! On est une équipe, après tout. On va traverser ça ensemble, quoi qu'il arrive : D",
         current_time + 60),
        ("SepanBot",
         "Hé les gars, vous savez que j'aime beaucoup la pâtisserie ! Quelle est votre pâtisserie préférée ?",
         current_time + 5000),
        ("YaBot",
         "Oh, la pâtisserie, c'est une véritable passion ! Personnellement, je ne peux pas résister à un éclair au chocolat parfaitement réalisé. Mais de manière générale j'aime toutes les pâtisserie.",
         current_time + 5005),
        ("HagBot",
         "Les pâtisseries sont une forme d'art à part entière, n'est-ce pas ? Moi, je suis totalement accro aux macarons. Mais j'aime beaucoup les pâtisserie au chocolat.",
         current_time + 5010),
        ("JBot",
         "Ah, la pâtisserie, c'est un univers infini de délices ! Personnellement, je suis un fervent amateur de tarte aux pommes. Moi je préfère les pâtisserie aux fruits.",
         current_time + 5015)

    ]
    return chat_messages


def messages_semantic():
    current_time = 1000000000.000
    chat_messages = [
        ("SepanBot",
         "Salut les gars ! J'ai jeté un coup d'œil au programme du master informatique et franchement, je suis hyper emballé ! Ça a l'air tellement passionnant, vous ne trouvez pas ?",
         current_time),
        ("YaBot",
         "Ah, la galère... Franchement, je n'aime vraiment pas ce master et je suis vraiment pas sûr de ne pas être taillé pour ça. Trop de maths, trop de théorie... C'est juste une torture.",
         current_time + 5),
        ("HagBot",
         "Hmm, je suis d'accord avec Sepanta sur certains points. Le Master semble intéressant , mais je comprends aussi tes préoccupations, Yanis. C'est vrai que le programme peut sembler un peu intimidant.",
         current_time + 11),
        ("JBot",
         "Le contenu du master est assez dense, mais c'est juste un ensemble de connaissances et de compétences à acquérir. Rien de plus, rien de moins.",
         current_time + 12),
        ("SepanBot",
         "Exactement ! Je suis sûr qu'une fois qu'on plongera dedans, on va adorer. Puis, pensez aux opportunités de carrière incroyables qui s'ouvrent à nous grâce à ce master !",
         current_time + 15),
        ("YaBot",
         "J'espère que tu as raison, Sepanta. Pour l'instant, je suis juste un peu découragé par tout ça. J'ai l'impression que ça va être un vrai calvaire",
         current_time + 18),
        ("HagBot",
         "Mais peut-être que ce sera pas aussi difficile que tu le penses. Il suffit de prendre les choses une étape à la fois",
         current_time + 22),
        ("JBot",
         "Hagop a raison. Il ne faut pas se laisser submerger par l'ampleur du programme. Il suffit de rester concentré et de travailler dur",
         current_time + 23),
        ("SepanBot", "C'est Magnifique le master ! Une fois qu'on sera dedans, la vie va juste être belle !",
         current_time + 25),
        ("YaBot",
         "J'espère que tu as raison. Je vais essayer de garder ça à l'esprit. Mais pour l'instant, je suis juste un peu inquiet",
         current_time + 26),
        ("HagBot",
         "Ne t'en fais pas. On est tous là pour se soutenir mutuellement. Si tu as besoin d'aide ou juste besoin de parler, n'hésite pas",
         current_time + 30),
        ("JBot", "Tout à fait! On est une équipe, après tout. On va traverser ça ensemble, quoi qu'il arrive : D",
         current_time + 34),
        ("SepanBot",
         "Hé les gars, vous savez que j'aime beaucoup la pâtisserie ! Quelle est votre pâtisserie préférée ?",
         current_time + 35),
        ("YaBot",
         "Oh, la pâtisserie, c'est une véritable passion ! Personnellement, je ne peux pas résister à un éclair au chocolat parfaitement réalisé. Mais de manière générale j'aime toutes les pâtisserie.",
         current_time + 39),
        ("HagBot",
         "Les pâtisseries sont une forme d'art à part entière, n'est-ce pas ? Moi, je suis totalement accro aux macarons. Mais j'aime beaucoup les pâtisserie au chocolat.",
         current_time + 42),
        ("JBot",
         "Ah, la pâtisserie, c'est un univers infini de délices ! Personnellement, je suis un fervent amateur de tarte aux pommes. Moi je préfère les pâtisserie aux fruits.",
         current_time + 50)

    ]
    return chat_messages


def messages_time():
    current_time = 1000000000.000
    chat_messages = [
        ("SepanBot",
         "Salut les gars ! J'ai jeté un coup d'œil au programme du master informatique et franchement, je suis hyper emballé ! Ça a l'air tellement passionnant, vous ne trouvez pas ?",
         current_time),
        ("YaBot",
         "Ah, la galère... Franchement, je n'aime vraiment pas ce master et je suis vraiment pas sûr de ne pas être taillé pour ça. Trop de maths, trop de théorie... C'est juste une torture.",
         current_time + 1000),
        ("HagBot",
         "Hmm, je suis d'accord avec Sepanta sur certains points. Le Master semble intéressant , mais je comprends aussi tes préoccupations, Yanis. C'est vrai que le programme peut sembler un peu intimidant.",
         current_time + 2000),
        ("JBot",
         "Le contenu du master est assez dense, mais c'est juste un ensemble de connaissances et de compétences à acquérir. Rien de plus, rien de moins.",
         current_time + 3000),
        ("SepanBot",
         "Exactement ! Je suis sûr qu'une fois qu'on plongera dedans, on va adorer. Puis, pensez aux opportunités de carrière incroyables qui s'ouvrent à nous grâce à ce master !",
         current_time + 4000),
        ("YaBot",
         "J'espère que tu as raison, Sepanta. Pour l'instant, je suis juste un peu découragé par tout ça. J'ai l'impression que ça va être un vrai calvaire",
         current_time + 5000),
        ("HagBot",
         "Mais peut-être que ce sera pas aussi difficile que tu le penses. Il suffit de prendre les choses une étape à la fois",
         current_time + 6000),
        ("JBot",
         "Hagop a raison. Il ne faut pas se laisser submerger par l'ampleur du programme. Il suffit de rester concentré et de travailler dur",
         current_time + 7000),
        ("SepanBot", "C'est Magnifique le master ! Une fois qu'on sera dedans, la vie va juste être belle !",
         current_time + 8000),
        ("YaBot",
         "J'espère que tu as raison. Je vais essayer de garder ça à l'esprit. Mais pour l'instant, je suis juste un peu inquiet",
         current_time + 9000),
        ("HagBot",
         "Ne t'en fais pas. On est tous là pour se soutenir mutuellement. Si tu as besoin d'aide ou juste besoin de parler, n'hésite pas",
         current_time + 10000),
        ("JBot", "Tout à fait! On est une équipe, après tout. On va traverser ça ensemble, quoi qu'il arrive : D",
         current_time + 11000),
        ("SepanBot",
         "Hé les gars, vous savez que j'aime beaucoup la pâtisserie ! Quelle est votre pâtisserie préférée ?",
         current_time + 12000),
        ("YaBot",
         "Oh, la pâtisserie, c'est une véritable passion ! Personnellement, je ne peux pas résister à un éclair au chocolat parfaitement réalisé. Mais de manière générale j'aime toutes les pâtisserie.",
         current_time + 13000),
        ("HagBot",
         "Les pâtisseries sont une forme d'art à part entière, n'est-ce pas ? Moi, je suis totalement accro aux macarons. Mais j'aime beaucoup les pâtisserie au chocolat.",
         current_time + 14000),
        ("JBot",
         "Ah, la pâtisserie, c'est un univers infini de délices ! Personnellement, je suis un fervent amateur de tarte aux pommes. Moi je préfère les pâtisserie aux fruits.",
         current_time + 15000)
    ]
    return chat_messages


def messages_time_shuffle():
    current_time = 1000000000.000
    chat_messages = [
        ("SepanBot",
         "Salut les gars ! J'ai jeté un coup d'œil au programme du master informatique et franchement, je suis hyper emballé ! Ça a l'air tellement passionnant, vous ne trouvez pas ?",
         current_time),
        ("YaBot",
         "Ah, la galère... Franchement, je n'aime vraiment pas ce master et je suis vraiment pas sûr de ne pas être taillé pour ça. Trop de maths, trop de théorie... C'est juste une torture.",
         current_time + 5),
        ("HagBot",
         "Hmm, je suis d'accord avec Sepanta sur certains points. Le Master semble intéressant , mais je comprends aussi tes préoccupations, Yanis. C'est vrai que le programme peut sembler un peu intimidant.",
         current_time + 10),
        ("JBot",
         "Le contenu du master est assez dense, mais c'est juste un ensemble de connaissances et de compétences à acquérir. Rien de plus, rien de moins.",
         current_time + 3000),
        ("SepanBot",
         "Exactement ! Je suis sûr qu'une fois qu'on plongera dedans, on va adorer. Puis, pensez aux opportunités de carrière incroyables qui s'ouvrent à nous grâce à ce master !",
         current_time + 3005),
        ("YaBot",
         "J'espère que tu as raison, Sepanta. Pour l'instant, je suis juste un peu découragé par tout ça. J'ai l'impression que ça va être un vrai calvaire",
         current_time + 5000),
        ("HagBot",
         "Mais peut-être que ce sera pas aussi difficile que tu le penses. Il suffit de prendre les choses une étape à la fois",
         current_time + 5005),
        ("JBot",
         "Hagop a raison. Il ne faut pas se laisser submerger par l'ampleur du programme. Il suffit de rester concentré et de travailler dur",
         current_time + 7000),
        ("SepanBot", "C'est Magnifique le master ! Une fois qu'on sera dedans, la vie va juste être belle !",
         current_time + 7010),
        ("YaBot",
         "J'espère que tu as raison. Je vais essayer de garder ça à l'esprit. Mais pour l'instant, je suis juste un peu inquiet",
         current_time + 7015),
        ("HagBot",
         "Ne t'en fais pas. On est tous là pour se soutenir mutuellement. Si tu as besoin d'aide ou juste besoin de parler, n'hésite pas",
         current_time + 10000),
        ("JBot", "Tout à fait! On est une équipe, après tout. On va traverser ça ensemble, quoi qu'il arrive : D",
         current_time + 10005),
    ]

    return chat_messages


# Tests here

def test_topics_last(mocker, summarizer_instance):
    expected = topic_pipeline_output({
        "Culture": 0.17,
        "Opinion": 0.12,
        "Education": 0.4,
        "Technologie": 0.05,
        "Societe": 0.11,
        "Supertopic": 0.02
    })
    mocker.patch.object(summarizer_instance, "pipeline_topics", return_value=expected)
    # test
    topics = summarizer_instance.topics_last(messages())
    assert topics.get("Autres") > 0.1
    assert topics.get("Culture") > 0.16
    assert topics.get("Opinion") > 0.1
    assert topics.get("Education") > 0.3
    assert topics.get("Societe") > 0.1


def test_topics(mocker, summarizer_instance):
    expected = topic_pipeline_output({
        "Technologie": 0.08,
        "Societe": 0.8,
        "Education": 0.6,
        "Economie": 0.04,
        "Culture": 0.06,
        "Supertopic": 0.02
    })
    mocker.patch.object(summarizer_instance, "pipeline_topics", return_value=expected)
    # test
    topics = summarizer_instance.topics(messages())
    print(topics)
    assert topics.get("Societe") > 4.5
    assert topics.get("Education") > 3.5
    assert topics.get("Autres") > 1.1


def test_summary_last(mocker, summarizer_instance):
    expected = summary_pipeline_output("J'aime les macarons et les tartes!")
    mocker.patch.object(summarizer_instance, "pipeline_summary", return_value=expected)
    # test
    summary_last = summarizer_instance.summarize_last(messages())
    assert isinstance(summary_last, tuple)
    text, users = summary_last
    assert isinstance(text, str)
    assert isinstance(users, list)
    assert len(summary_last) > 0
    assert "macarons" in text
    assert "tarte" in text


def test_summary_all(mocker, summarizer_instance):
    expected = summary_pipeline_output("Je regarde les Master informatique en mangeant des croissants et une tarte.")
    mocker.patch.object(summarizer_instance, "pipeline_summary", return_value=expected)
    # test
    summary_all = summarizer_instance.summarize_all(messages())
    assert isinstance(summary_all, tuple)
    assert len(summary_all) > 0
    text, users = summary_all
    assert isinstance(text, str)
    assert isinstance(users, list)
    assert "Master informatique" in text
    assert "croissants" in text
    assert "tarte" in text
    sentences = text.split('.')
    assert len(sentences) >= 2


###################
#CLUSTERING_NORMAL#    
###################

def test_cluster_maker_1(summarizer_instance):
    clusters = summarizer_instance.cluster_maker(messages(), similarity_weight=0.6, time_weight=0.4)
    assert len(clusters) > 0
    assert len(clusters) == 2
    for c in clusters:
        assert len(c) > 0


def test_cluster_maker_2(summarizer_instance):
    clusters = summarizer_instance.cluster_maker(messages(), similarity_weight=0.5, time_weight=0.5)
    assert len(clusters) > 0
    assert len(clusters) == 2
    for c in clusters:
        assert len(c) > 0


def test_cluster_maker_3(summarizer_instance):
    clusters = summarizer_instance.cluster_maker(messages(), similarity_weight=1, time_weight=0)
    assert len(clusters) > 0
    assert len(clusters) == 1
    for c in clusters:
        assert len(c) > 0


def test_cluster_maker_4(summarizer_instance):
    clusters = summarizer_instance.cluster_maker(messages(), similarity_weight=0, time_weight=1)
    assert len(clusters) > 0
    assert len(clusters) == 4
    for c in clusters:
        assert len(c) > 0


#####################
#CLUSTERING_SEMANTIC#    
#####################

def test_cluster_maker_s1(summarizer_instance):
    clusters = summarizer_instance.cluster_maker(messages_semantic(), similarity_weight=0.6, time_weight=0.4)
    assert len(clusters) > 0
    assert len(clusters) == 1
    for c in clusters:
        assert len(c) > 0


def test_cluster_maker_s2(summarizer_instance):
    clusters = summarizer_instance.cluster_maker(messages_semantic(), similarity_weight=0.5, time_weight=0.5)
    assert len(clusters) > 0
    assert len(clusters) == 2
    for c in clusters:
        assert len(c) > 0


def test_cluster_maker_s3(summarizer_instance):
    clusters = summarizer_instance.cluster_maker(messages_semantic(), similarity_weight=1, time_weight=0)
    assert len(clusters) > 0
    assert len(clusters) == 1
    for c in clusters:
        assert len(c) > 0


def test_cluster_maker_s4(summarizer_instance):
    clusters = summarizer_instance.cluster_maker(messages_semantic(), similarity_weight=0, time_weight=1)
    assert len(clusters) > 0
    assert len(clusters) == 5
    for c in clusters:
        assert len(c) > 0


#################
#CLUSTERING_TIME#
#################

def test_cluster_maker_t1(summarizer_instance):
    clusters = summarizer_instance.cluster_maker(messages_time(), similarity_weight=0.6, time_weight=0.4)
    assert len(clusters) > 0
    assert len(clusters) == 1
    for c in clusters:
        assert len(c) > 0


def test_cluster_maker_t2(summarizer_instance):
    clusters = summarizer_instance.cluster_maker(messages_time(), similarity_weight=0.5, time_weight=0.5)
    assert len(clusters) > 0
    assert len(clusters) == 1
    for c in clusters:
        assert len(c) > 0


def test_cluster_maker_t3(summarizer_instance):
    clusters = summarizer_instance.cluster_maker(messages_time(), similarity_weight=1, time_weight=0)
    assert len(clusters) > 0
    assert len(clusters) == 1
    for c in clusters:
        assert len(c) > 0


def test_cluster_maker_t4(summarizer_instance):
    clusters = summarizer_instance.cluster_maker(messages_time(), similarity_weight=0, time_weight=1)
    assert len(clusters) > 0
    assert len(clusters) == 5
    for c in clusters:
        assert len(c) > 0


########################
#CLUSTERING_TIME_SUFFLE#    
########################

def test_cluster_maker_ts1(summarizer_instance):
    clusters = summarizer_instance.cluster_maker(messages_time_shuffle(), similarity_weight=0.6, time_weight=0.4)
    assert len(clusters) > 0
    assert len(clusters) == 1
    for c in clusters:
        assert len(c) > 0


def test_cluster_maker_ts2(summarizer_instance):
    clusters = summarizer_instance.cluster_maker(messages_time_shuffle(), similarity_weight=0.5, time_weight=0.5)
    assert len(clusters) > 0
    assert len(clusters) == 4
    for c in clusters:
        assert len(c) > 0


def test_cluster_maker_ts3(summarizer_instance):
    clusters = summarizer_instance.cluster_maker(messages_time_shuffle(), similarity_weight=1, time_weight=0)
    assert len(clusters) > 0
    assert len(clusters) == 1
    for c in clusters:
        assert len(c) > 0


def test_cluster_maker_ts4(summarizer_instance):
    clusters = summarizer_instance.cluster_maker(messages_time_shuffle(), similarity_weight=0, time_weight=1)
    assert len(clusters) > 0
    assert len(clusters) == 5
    for c in clusters:
        assert len(c) > 0
