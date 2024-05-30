from typing import Optional

from transformers import pipeline
from collections import defaultdict


class GuildMBTI:
    def __init__(self, pipeline_mbti: pipeline, translator: pipeline) -> None:
        """
        Initialize the GuildMBTI class with the specified pipeline and translator.

        Args:
            pipeline_mbti (pipeline): The MBTI classification pipeline.
            translator (pipeline): The translator pipeline.
        """
        self.pipeline_mbti = pipeline_mbti  # Type: pipeline
        self.translator = translator  # Type: Translator
        self.user_mbtis = {}  # Type: Dict[int, dict[str, float]]
        self.message_counters = defaultdict(int)  # Type: Dict[int, int]

    def handle_message(self, user_id: int, msg_content: str) -> None:
        """
        Handle a new message by updating the MBTI distribution data for the user.

        Args:
            user_id (int): The ID of the message author.
            msg_content (str): The content of the message.
        """
        self.message_counters[user_id] += 1

        mbti_result = self.get_message_mbti(msg_content)

        if user_id in self.user_mbtis:
            user_result = self.user_mbtis[user_id]
            merged_result = self._merge_mbti_results(user_id, user_result, mbti_result)
            self.user_mbtis[user_id] = merged_result

        else:
            self.user_mbtis[user_id] = mbti_result

    def _merge_mbti_results(self, user_id: int, existing_result: dict[str, float], new_result: dict[str, float]) -> (
            dict)[str, float]:
        """
        Merge two MBTI classification results.

        Args:
            existing_result (dict): The existing MBTI classification result.
            new_result (dict): The new MBTI classification result to merge.
            user_id (int): The ID of the user.

        Returns:
            dict: The merged MBTI classification result.
        """
        merged_result = {}
        for mbti_type, score in new_result.items():
            merged_result[mbti_type] = ((self.message_counters[user_id] - 1) * existing_result.get(mbti_type, 0) +
                                        score) / self.message_counters[user_id]
        return merged_result

    def get_message_mbti(self, msg_content: str) -> dict[str, float]:
        """
        Get MBTI classification for a message.

        Args:
            msg_content (str): The content of the message.

        Returns:
            dict: The MBTI classification result.
        """
        translated_message = self.translator.translate_to_en(msg_content)

        result = self.pipeline_mbti(translated_message, top_k=None)

        mbti_result = {res["label"]: res["score"] for res in result}

        return mbti_result

    def get_user_mbti(self, user_id: int) -> Optional[str]:
        """
        Get the dominant MBTI type for a user.

        Args:
            user_id (int): The user ID.

        Returns:
            Optional[str]: The dominant MBTI type for the user, or None if no result is found.
        """
        user_result = self.user_mbtis.get(user_id)

        if user_result:
            max_mbti = max(user_result, key=user_result.get)
            return max_mbti
        else:
            return None

    def get_guild_mbtis(self) -> dict[str, int]:
        """
        Get the distribution of MBTI types for the guild.

        Returns:
            dict: The distribution of MBTI types.
        """
        mbti_counts = {}

        for user_result in self.user_mbtis.values():
            dominant_mbti = max(user_result, key=user_result.get)
            mbti_counts[dominant_mbti] = mbti_counts.get(dominant_mbti, 0) + 1

        return mbti_counts
