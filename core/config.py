import json
from typing import List
import re

class Config:
    def __init__(self, path) -> None:
        with open(path) as file:
            self.__data = json.load(file)
        # check the file
        assert isinstance(self.__data["token"], str)
        assert isinstance(self.__data["staff_team"], list)
        assert all(map(lambda e: isinstance(e, int), self.__data["staff_team"]))
        assert isinstance(self.__data["debug"], bool)
        assert isinstance(self.__data["test_guild"], int)
        assert isinstance(self.__data["color"], str)
        assert re.match(r"#[0-9a-f]{6}", self.__data["color"])
        assert isinstance(self.__data["prefix"], str)

    def get_token(self) -> str:
        """Returns the bot token"""
        return self.__data.get("token")

    def get_staff_team(self) -> List[int]:
        """Returns the list of user_id in the staff team"""
        return self.__data.get("staff_team")

    def is_in_staff_team(self, user_id) -> bool:
        """Returns True if the user_id is in the staff team"""
        staff_team = self.get_staff_team()
        return user_id in staff_team

    def is_debug(self) -> bool:
        """Returns True if the bot is in debug mode, False otherwise."""
        return self.__data.get("debug")

    def get_test_guild(self) -> int:
        """
        Returns the id of the test guild in which to deploy application commands in debug mode.
        """
        return self.__data.get("test_guild")

    def get_color(self) -> str:
        """Returns the colour to use in the bot."""
        return self.__data.get("color")

    def get_prefix(self) -> str:
        """Returns the bot's prefix."""
        return self.__data.get("prefix")