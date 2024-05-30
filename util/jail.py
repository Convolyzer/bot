from typing import Dict, Optional, List
from core.store import Store
from time import time


class JailConfig:
    RULE_FIELD = "rule"
    CHANNEL_FIELD = "channel"
    ROLE_FIELD = "role"
    PRISONERS_FILED = "prisoners"
    WARNS_FIELD = "warn"

    def __init__(self, config: Dict[str, int] = {}) -> None:
        self.__rule = config.get(self.RULE_FIELD)
        self.__channel = config.get(self.CHANNEL_FIELD)
        self.__role = config.get(self.ROLE_FIELD)
        prisonners = config.get(self.PRISONERS_FILED, dict())
        self.__prisoners = {int(k): v for k, v in prisonners.items()}
        warns = config.get(self.WARNS_FIELD, dict())
        self.__warns = {int(k): v for k, v in warns.items()}

    # Getters ---------------------------------------------

    def get_rule(self) -> int:
        return self.__rule

    def get_channel(self) -> int:
        return self.__channel

    def get_role(self) -> int:
        return self.__role

    # Manager warns ---------------------------------------

    def get_warns_count(self, user_id: int) -> int:
        """Returns the warns count of this user."""
        return self.__warns.get(user_id, 0)

    def warn(self, user_id: int):
        """Increments the warns count of this user by one."""
        self.__warns[user_id] = self.__warns.get(user_id, 0) + 1
    
    def warn3(self, user_id: int):
        """Increments the warns count of this user by one."""
        self.__warns[user_id] = self.__warns.get(user_id, 0) + 3

    # Manage prisoners ------------------------------------

    def get_nb_prisoners(self) -> int:
        """Returns the number of prisoners."""
        return len(self.__prisoners)

    def has_prisoner(self, user_id: int) -> bool:
        """Returns true if this user is a prisoner."""
        return user_id in self.__prisoners

    def add_prisoner(self, user_id: int):
        """Add this user in the jail."""
        print(self.__prisoners)
        self.__prisoners[user_id] = time() + 5 * 60
        print(self.__prisoners)

    def pardon(self, user_id: int):
        self.__prisoners[user_id] -= 1 * 60

    def free_prisoner(self, user_id: int):
        del self.__prisoners[user_id]
        self.__warns[user_id] = 0

    def free_prisoners(self) -> List[int]:
        res = []
        now = time()
        for user_id, free_time in list(self.__prisoners.items()):
            if free_time <= now:
                res.append(user_id)
                self.free_prisoner(user_id)
        return res

    # Export ----------------------------------------------

    def to_dict(self) -> Dict[str, int]:
        res = dict()
        res[self.RULE_FIELD] = self.__rule
        res[self.CHANNEL_FIELD] = self.__channel
        res[self.ROLE_FIELD] = self.__role
        res[self.PRISONERS_FILED] = self.__prisoners
        res[self.WARNS_FIELD] = self.__warns
        return res


class JailStore:
    GUILDS_TO_LOAD = "guilds_to_load"

    def __init__(self, store: Store) -> None:
        self.__store = store
        self.__cache = dict()
        # load guild with muted people in the cache
        guilds_to_load = self.__store.get(self.GUILDS_TO_LOAD) or list()
        for guild_id in guilds_to_load:
            self.get(guild_id)

    def create_jail(self, guild_id: int, rule_id: int, role_id: int, channel_id: int):
        """Create a new jail."""
        config = dict()
        config[JailConfig.RULE_FIELD] = rule_id
        config[JailConfig.ROLE_FIELD] = role_id
        config[JailConfig.CHANNEL_FIELD] = channel_id
        self.__cache[guild_id] = JailConfig(config)

    def delete_jail(self, guild_id):
        if guild_id in self.__cache:
            del self.__cache[guild_id]

    def get(self, guild_id: int) -> Optional[JailConfig]:
        if not guild_id in self.__cache:
            res = self.__store.get(str(guild_id))
            if res is None:
                self.__cache[guild_id] = None
            else:
                self.__cache[guild_id] = JailConfig(res)
        return self.__cache[guild_id]

    def free_prisoners(self) -> Dict[int, List[int]]:
        res = dict()
        for guild_id, jailconf in self.__cache.items():
            if not jailconf:
                continue
            users = jailconf.free_prisoners()
            if len(users) > 0:
                res[guild_id] = users
        return res

    def flush(self):
        guilds_to_load = []
        for guild_id, jailconfig in self.__cache.items():
            if jailconfig.get_nb_prisoners() > 0:
                guilds_to_load.append(guild_id)
            self.__store.set(str(guild_id), jailconfig.to_dict())
        # save guild id in with a specific key
        self.__store.set(self.GUILDS_TO_LOAD, guilds_to_load)
