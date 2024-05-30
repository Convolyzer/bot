class AsciiHelper:
    """
    Helper class to generate ASCII progress bars.
    """

    @staticmethod
    def get_progress_bar(normalized_score):
        """
        Generate an ASCII progress bar based on a normalized score.

        @param normalized_score: The normalized score representing progress (between 0 and 1).
        @type normalized_score: float
        @return: ASCII progress bar.
        @rtype: str
        """
        # Construct the progress bar
        bar_length = 20
        filled_length = int(normalized_score * bar_length)
        filled_char = '█'
        empty_char = '░'
        progress_bar = filled_char * filled_length + empty_char * (bar_length - filled_length)
        # Add % representation of the score
        score_percentage = int(normalized_score * 100)
        score_str = f"{score_percentage}%"
        # Construct the final message with the progress bar and score
        message_content = f"[{progress_bar}] {score_str}"
        # Send the message
        return message_content

