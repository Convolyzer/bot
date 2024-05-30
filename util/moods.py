from collections import defaultdict
from textblob_fr import PatternTagger, PatternAnalyzer
from textblob import Blobber
from datetime import datetime, timedelta
from enum import Enum


class Mood(Enum):
    JOY = 'joie'
    SURPRISE = 'surprise'
    LOVE = 'amour'
    ANGER = 'colère'
    SADNESS = 'tristesse'
    FEAR = 'peur'


class MessageMood:
    """Class to represent message mood."""

    def __init__(self, message_id, time, pov, mood, positivity):
        """
        Initializes a MessageMood object.

        @param message_id: The ID of the message.
        @type message_id: int
        @param time: The time the message was sent.
        @type time: real
        @param pov: The point of view of the message.
        @type pov: real
        @param mood: The mood of the message should be one of the Mood enum values.
        @type mood: list [label,score(float)]
        @param positivity: The positivity of the message.
        @type positivity: float
        """
        self.__message_id = message_id
        self.__time = time
        self.__pov = pov
        self.__mood = mood
        self.__positivity = positivity

    def get_message_id(self):
        """Returns the ID of the message."""
        return self.__message_id

    def get_time(self):
        """Returns the time the message was sent."""
        return self.__time

    def get_pov(self):
        """Returns the point of view of the message."""
        return self.__pov

    def get_mood(self):
        """Returns the mood of the message."""
        return self.__mood

    def get_positivity(self):
        """Returns the positivity of the message."""
        return self.__positivity


class GuildMoods:
    """
    Class to manage and analyze the mood of messages within a guild.
    """

    def __init__(self, pipeline_mood, pipeline_positivity):
        """
        Class to manage and analyze the mood of messages within a guild.
        """
        # Cache for user messages
        self.user_messages = defaultdict(list)

        # Text classification model for mood analysis
        self.analyzer = pipeline_mood  # pipeline(task='text-classification',
        # model='botdevringring/fr-naxai-ai-emotion-classification-081808122023',
        # tokenizer='botdevringring/fr-naxai-ai-emotion-classification-081808122023')

        # Text classification model for positivity analysis
        self.sentiment_classifier = pipeline_positivity  # pipeline("text-classification",
        # model="citizenlab/twitter-xlm-roberta-base-sentiment-finetunned",
        # tokenizer="citizenlab/twitter-xlm-roberta-base-sentiment-finetunned")

        # TextBlob French analyzer for pov analysis
        self.tb_fr = Blobber(pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())

        self.mood_translation = {
            'joy': 'joie',
            'surprise': 'surprise',
            'love': 'amour',
            'anger': 'colère',
            'sadness': 'tristesse',
            'fear': 'peur'
        }
        
    def _add_message(self, msg_author_id, message):
        """
        Adds message information to the user's message list.

        @param msg_author_id: The ID of the message author.
        @type msg_author_id: int
        @param message: The message content.
        @type message: MessageMood
        """
        if message not in self.user_messages[msg_author_id]:
            self.user_messages[msg_author_id].append(message)

    def garbage_collector(self):
        """
        Removes expired messages from the cache.
        """
        current_time = datetime.now()
        expired_messages = []

        for user_id, messages in self.user_messages.items():
            for message in messages:
                # Check if the message has passed 24 hours since creation
                if (current_time - message.get_time()) >= timedelta(hours=24):
                    expired_messages.append((user_id, message))

        # Remove expired messages from the user_messages cache
        for user_id, message in expired_messages:
            self.user_messages[user_id].remove(message)

    def handle_message(self, msg_author_id, msg_content, msg_id, msg_created_at):
        """
       Handles a new message by analyzing its sentiment and mood.

       @param msg_author_id: The ID of the message author.
       @type msg_author_id: int
       @param msg_content: The content of the message.
       @type msg_content: str
       @param msg_id: The ID of the message.
       @type msg_id: int
       @param msg_created_at: The creation timestamp of the message.
       @type msg_created_at: datetime.datetime
       """

        if msg_content.startswith(('@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '[', ']',
                                   '{', '}', ';', ':', ',', '<', '>', '.', '/', '?', 'https')):
            return

        # Perform sentiment analysis on the message content
        sentiment_result = self.sentiment_classifier(msg_content, top_k=None)

        positive_score = 0.0

        # Find the entry with the label "Positive"
        for entry in sentiment_result:
            if entry['label'] == 'Positive':
                positive_score = entry['score']
                break  # Exit the loop once "Positive" is found

        # Perform sentiment analysis on the message content
        blob = self.tb_fr(msg_content)
        # Calculate subjectivity score
        subjectivity_score = blob.sentiment[1]

        # Analyse moods
        mood_scores = self.analyzer(msg_content)

        # Extraction of dominant mood {['fear', 0.9997491240501404]}
        label_mood = self.mood_translation[mood_scores[0]['label']]
        score_mood = mood_scores[0]['score']

        mood_resultat = [label_mood, score_mood]

        # Create a Message object with the message content and sentiment score
        message = MessageMood(message_id=msg_id, time=msg_created_at, pov=subjectivity_score, mood=mood_resultat,
                              positivity=positive_score)

        # Add the message to the GuildMood
        self._add_message(msg_author_id, message)

    def get_user_positivity(self, msg_author_id):
        """
        Get the positivity score for a given user based on their messages.

        @param msg_author_id: The ID of the user.
        @type msg_author_id: int
        @return: the user's positivity score.
        @rtype: float
        """
        # Get the positivity scores from the user's messages
        positive_score = sum(msg.get_positivity() for msg in self.user_messages.get(msg_author_id, []))

        # Calculate the total activity
        user_activity = len(self.user_messages.get(msg_author_id, []))
        # Calculate the normalized score
        normalized_positive = positive_score / user_activity if user_activity > 0 else 0

        # Return the sentiment score
        return normalized_positive

    def get_user_pov(self, msg_author_id):
        """
        Get the point of view score for a given user based on their messages.

        @param msg_author_id: The ID of the user.
        @type msg_author_id: int
        @return: the user's point of view score.
        @rtype: float
        """
        # Get the pov scores from the user's messages
        pov_score = sum(msg.get_pov() for msg in self.user_messages.get(msg_author_id, []))

        # Calculate the total of messages of user
        user_activity = len(self.user_messages.get(msg_author_id, []))
        # Calculate the normalized score
        normalized_pov = pov_score / user_activity if user_activity > 0 else 0

        # Return the score
        return normalized_pov

    def get_user_mood(self, user_id):
        """
        Get the mood chart for a given user based on their messages.

        @param user_id: The ID of the user.
        @type user_id: int
        @return: the user's mood distribution.
        @rtype: dict
        """
        user_mood = self._calculate_user_mood(user_id)

        # Filter out moods with zero frequency
        labels = []
        sizes = []

        for label, frequency in user_mood.items():
            if frequency > 0:
                labels.append(label)
                sizes.append(frequency)

        return {label: size for label, size in zip(labels, sizes)}

    def _calculate_user_mood(self, user_id):
        """
        Calculate the mood distribution for a given user based on their messages.

        @param user_id: The ID of the user.
        @type user_id: int
        @return: Dictionary containing mood frequencies for the user.
        @rtype: dict
        """

        # Initialize mood accumulator
        mood_accumulator = {
            Mood.JOY.value: 0,
            Mood.SURPRISE.value: 0,
            Mood.LOVE.value: 0,
            Mood.ANGER.value: 0,
            Mood.SADNESS.value: 0,
            Mood.FEAR.value: 0
        }

        # Iterate through all messages from the user
        for message in self.user_messages.get(user_id, []):
            # Get mood scores from the message
            mood_data = message.get_mood()

            # Extraction label because the max label is always first
            mood_label = mood_data[0]

            mood_accumulator[mood_label] += 1

        # Return the mood accumulator dictionary {label: frequency}
        return mood_accumulator

    def _check_message_cache(self, message_id):
        """
        Get the message from cache

        @param message_id: The ID of the message.
        @type message_id: int
        @return: The message in cache or None
        @rtype: MessageMood or None
        """
        # Check if the message id exists in any user's messages
        for messages in self.user_messages.values():
            for msg in messages:
                if msg.get_message_id() == message_id:
                    return msg
        return None

    def _get_pov_message(self, msg_content):
        """
        Get the pov of a message

        @param msg_content: The content of the message.
        @type msg_content: str
        @return: the score pov of the message
        @rtype: float
        """
        # Perform sentiment analysis on the message content
        blob = self.tb_fr(msg_content)
        # Calculate subjectivity score
        subjectivity_score = blob.sentiment[1]
        return subjectivity_score

    def get_message_pov(self, message_id, msg_content):
        """
        Get the point of view score for a specific message.

        @param message_id: The ID of the message.
        @type message_id: int
        @param msg_content: The content of the message.
        @type msg_content: str
        @return: the point of view score.
        @rtype: float
        """
        msg = self._check_message_cache(message_id)
        if msg:
            # If the message id is found, get the pov score
            pov_score = msg.get_pov()
            # Use the progress_bar function if the score is obtained from a message object
            return pov_score
        subjectivity_score = self._get_pov_message(msg_content)

        return subjectivity_score

    def _get_positivity_message(self, msg_content):
        """
        Get the positivity of a message

        @param msg_content: The content of the message.
        @type msg_content: str
        @return: the score positivity of the message
        @rtype: float
        """
        # Perform sentiment analysis on the message content
        sentiment_result = self.sentiment_classifier(msg_content, top_k=None)

        positive_score = 0.0
        # Find the entry with the label "Positive"
        for entry in sentiment_result:
            if entry['label'] == 'Positive':
                positive_score = entry['score']
                break  # Exit the loop once "Positive" is found
        return positive_score

    def get_message_positivity(self, message_id, msg_content):
        """
       Get the positivity score for a specific message.

       @param message_id: The ID of the message.
       @type message_id: int
       @param msg_content: The content of the message.
       @type msg_content: str
       @return: the positivity score.
       @rtype: float
       """
        msg = self._check_message_cache(message_id)
        if msg:
            # If the message id is found, get the pov score
            positivity_score = msg.get_positivity()
            # Use the progress_bar function if the score is obtained from a message object
            return positivity_score
        positivity_score = self._get_positivity_message(msg_content)
        return positivity_score

    def _get_mood_message(self, msg_content):
        """
        Get the mood of a message

        @param msg_content: The content of the message.
        @type msg_content: str
        @return: the score mood and the label mood of the message
        @rtype: float, str
        """
        # Analyse moods
        mood_scores = self.analyzer(msg_content)  # top_k=None

        # Extraction of dominant mood
        score_mood = mood_scores[0]['score']
        label_mood = mood_scores[0]['label']
        return score_mood, label_mood

    def get_message_mood(self, message_id, msg_content):
        """
        Get the mood score for a specific message.

        @param message_id: The ID of the message.
        @type message_id: int
        @param msg_content: The content of the message.
        @type msg_content: str
        @return: the mood score and the mood label.
        @rtype: float, str
        """
        msg = self._check_message_cache(message_id)
        if msg:
            # If the message id is found, get the mood score
            mood_score = msg.get_mood()[1]
            mood_label = msg.get_mood()[0]
            # Use the progress_bar function if the score is obtained from a message object
            return mood_score, mood_label
        score_mood, label_mood = self._get_mood_message(msg_content)
        return score_mood, label_mood

    def get_guild_pov(self):
        """
        Get a pie chart representing the distribution of subjective and objective messages.

        @return: the distribution of subjective and objective messages [labels],[counts].
        @rtype: dict
        """
        # Initialize counts for subjective and objective scores
        subjective_count = 0
        objective_count = 0

        # Iterate through all messages from all users
        for messages in self.user_messages.values():
            for msg in messages:
                # Increment counts based on the pov score
                if msg.get_pov() > 0.5:
                    subjective_count += 1
                else:
                    objective_count += 1

        # Create labels and sizes for the pie chart
        labels = ['Subjectif', 'Objectif']
        counts = [subjective_count, objective_count]

        return {label: count for label, count in zip(labels, counts)}

    def get_guild_positivity(self):
        """
        Get a pie chart representing the distribution of positive and negative messages.

        @return: the distribution of positive and negative messages [labels],[counts].
        @rtype: dict
        """
        # Initialize counts for positive and negative scores
        positive_count = 0
        negative_count = 0

        # Iterate through all messages from all users
        for messages in self.user_messages.values():
            for msg in messages:
                # Increment counts based on the positivity score
                positivity_score = msg.get_positivity()
                if positivity_score > 0.5:
                    positive_count += 1
                else:
                    negative_count += 1

        # Create labels and sizes for the pie chart
        labels = ['Positif', 'Negatif']
        counts = [positive_count, negative_count]

        return {label: count for label, count in zip(labels, counts)}

    def get_guild_mood(self):
        """
        Get a pie chart representing the distribution of different moods.

        @return: the distribution of different moods [labels],[counts].
        @rtype: dict
        """
        # Initialize mood accumulator
        mood_accumulator = {
            Mood.JOY.value: 0,
            Mood.SURPRISE.value: 0,
            Mood.LOVE.value: 0,
            Mood.ANGER.value: 0,
            Mood.SADNESS.value: 0,
            Mood.FEAR.value: 0
        }

        # Iterate over all users and accumulate mood frequencies
        for user_id in self.user_messages:
            user_mood = self._calculate_user_mood(user_id)
            for mood_label, frequency in user_mood.items():
                mood_accumulator[mood_label] += frequency

        # Filter out moods with zero frequency
        labels = []
        sizes = []

        for label, frequency in mood_accumulator.items():
            if frequency > 0:
                labels.append(label)
                sizes.append(frequency)

        return {label: size for label, size in zip(labels, sizes)}
