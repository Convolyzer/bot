import time
import pytest

from util import SocialGraph


@pytest.fixture
def socialgraph(tmpdir):
    filepath = tmpdir.join("123456")

    sg = SocialGraph(filepath)

    msgs = [
        (12, [15, 18], time.time()),
        (15, [12], time.time()),
        (18, [15], time.time()),
    ]

    other_msgs = [
        (18, time.time()),
        (15, time.time()),
    ]

    for msg in msgs:
        sg.handle_message(msg, other_msgs)

    return sg


def test_overview(socialgraph):
    socialgraph.overview()

def test_to_pygraphviz(socialgraph):
    pg = socialgraph.to_pygraphviz(12)

    assert len(pg.nodes()) == 3
    assert len(pg.neighbors(12)) == 2


def test_get_importance(socialgraph):
    socialgraph.update()
    assert isinstance(socialgraph.get_importance(12), float)


def test_get_rank(socialgraph):
    socialgraph.update()
    assert isinstance(socialgraph.get_rank(12), int)
    assert socialgraph.get_rank(12) == 1


def test_get_rank_no_data(socialgraph):
    assert socialgraph.get_rank(10) is None


def test_get_top_ranks(socialgraph):
    socialgraph.update()
    for rank in socialgraph.get_top_ranks():
        assert isinstance(rank, int)


def test_get_social_path(socialgraph):
    socialgraph.update()
    for _ in range(2):
        sc_path = socialgraph.get_social_path(18, 12)
        assert len(sc_path) == 3
        assert sc_path == [18, 15, 12]
    sc_path = socialgraph.get_social_path(12, 18)
    assert len(sc_path) == 2
    assert sc_path == [12, 18]


def test_get_interactions(socialgraph):
    socialgraph.update()
    interactions = socialgraph.get_interactions(12)
    assert len(interactions) == 2
    for inter in interactions:
        assert isinstance(inter, int)
