import json

from core import Config


def create_config(path, data):
    with open(path, mode="w") as file:
        json.dump(data, file)


def test_valid_config(tmpdir):
    conf_data = {
        "token": "TOKEN",
        "staff_team": [123, 456, 789],
        "debug": True,
        "test_guild": 123,
        "color": "#5e17eb",
        "prefix": "!"
    }
    conf_path = tmpdir.join("valid_conf.json")
    create_config(conf_path, conf_data)
    conf = Config(conf_path)
    assert conf.get_token() == "TOKEN"
    assert len(conf.get_staff_team()) == 3
    assert conf.is_in_staff_team(456)
    assert not conf.is_in_staff_team(321)
    assert conf.is_debug() == True
    assert conf.get_test_guild() == 123
    assert conf.get_color() == "#5e17eb"
    assert conf.get_prefix() == "!"
