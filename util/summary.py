import numpy as np
from sklearn.cluster import MeanShift
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Summarizer:

    def __init__(self,pipeline_summary,pipeline_topics):
        self.pipeline_summary = pipeline_summary
        self.pipeline_topics = pipeline_topics 

    #########
    #SUMMARY#
    #########

    def summarize_all(self, messages):
        """
        Make the summary of N messages.
        @param messages : Messages to summarize
        @type messages : List[tuple]
        @return: Summary of the messages and list of display names
        @rtype: Tuple[str, List[str]]
        """
        if messages:
            clusters = self.cluster_maker(messages)
            summary_all = ""
            users = set()  # Set to store unique user display names
            
            for cluster in clusters:
                cluster_content = ""
                previous_user = None
                for message in cluster:
                    users.add(message[0])  # Add the fucking name to set
                    if previous_user != message[0]: 
                        cluster_content += f"{message[0]}: {message[1]}\n"
                    else:
                        cluster_content += f"{message[1]}\n"
                    previous_user = message[0]
                
                chunks = self.split_input_by_max_length(cluster_content)  # Split content into chunks
                for chunk in chunks:
                    cl_summary = self.pipeline_summary(chunk)  # Process each chunk
                    summary_part = "".join(summary['summary_text'] for summary in cl_summary)
                    summary_all += summary_part
            
            return summary_all, list(users)  # Return summary and list of display names
        return None, []

    def summarize_last(self, messages):
            """
            Make the summary of the last conversation on N messages.
            @param messages : Messages to summarize
            @type messages : List[tuple]
            @return: Summary of the last conversation and list of display names
            @rtype: Tuple[str, List[str]]      
            """
            if messages:
                clusters = self.cluster_maker(messages)
                for c in clusters:
                    content = ""
                    users = set()  # Set to store shit user display names
                    previous_user = None
                    if messages[1] in c: 
                        for cl in c:
                            users.add(cl[0])  # Add user name to the set if not I will cry
                            if previous_user != cl[0]:  
                                content += f"{cl[0]}: {cl[1]}\n"
                            else:
                                content += f"{cl[1]}\n"
                            previous_user = cl[0]
                        chunks = self.split_input_by_max_length(content)  # Split content into chunks
                        summary_last = ""
                        for chunk in chunks:
                            cl_summary = self.pipeline_summary(chunk)  # Process each chunk
                            summary_part = "".join(summary['summary_text'] for summary in cl_summary)
                            summary_last += summary_part
                        return summary_last, list(users)  # Return summary and list of display names
            return None, []

 

    def split_input_by_max_length(self,text, max_length=512):
        """
        Split the input text into chunks of maximum length.
        """
        if len(text) <= max_length:
            return [text]  # No need to split

        chunks = []
        current_chunk = ""
        for token in text.split("\n"):
            if len(current_chunk) + len(token) + 1 <= max_length:  # +1 to account for '\n'
                if current_chunk:  # Add '\n' if it's not the beginning of the chunk
                    current_chunk += "\n"
                current_chunk += token
            else:
                chunks.append(current_chunk)
                current_chunk = token  # Start a new chunk with the token

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def semantic_similarity(self, messages):
        """
        Compute the matrix of semantic similarity between messages.
        
        :param messages: Messages to be clustered
        :type messages: List[tuple]
        :return: Matrix of similarity
        :rtype: numpy.ndarray
        """
        text_messages = [message[1] for message in messages]
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(text_messages)
        similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        return similarity_matrix

    def time_matrix(self, messages):
        """
        Create the matrix of time differences between messages.
        
        :param messages: Messages to be clustered
        :type messages: List[tuple]
        :return: Matrix of time differences
        :rtype: numpy.ndarray
        """
        n = len(messages)
        time_matrix = [[abs((messages[i][2] - messages[j][2])) for j in range(n)] for i in range(n)]
        return time_matrix
    
    def normalize_matrix(self, matrix):
        """
        Normalize the input matrix using Min-Max scaling.
        
        :param matrix: Input matrix to be normalized
        :type matrix: numpy.ndarray
        :return: Normalized matrix
        :rtype: numpy.ndarray
        """
        scaler = MinMaxScaler()
        normalized_matrix = scaler.fit_transform(matrix)
        return normalized_matrix

    def cluster_maker(self, messages, similarity_weight=0.7, time_weight=0.3):
        """
        Cluster conversations based on combined similarity and time proximity.
        
        :param messages: Messages to be clustered
        :type messages: List[tuple]
        :param similarity_weight: Weight for semantic similarity
        :type similarity_weight: float
        :param time_weight: Weight for time proximity
        :type time_weight: float
        :return: Detected conversations
        :rtype: List[List[tuple]]
        """
        conversations = []
        
        # Compute semantic similarity matrix
        similarity_matrix = self.semantic_similarity(messages)
        
        # Compute time matrix
        time_matrix = self.time_matrix(messages)
        
        # Normalize matrices
        normalized_similarity_matrix = self.normalize_matrix(similarity_matrix)
        normalized_time_matrix = self.normalize_matrix(time_matrix)
        
        # Combine matrices
        combined_matrix = similarity_weight * normalized_similarity_matrix + time_weight * normalized_time_matrix
        
        # Apply Mean Shift clustering
        clustering = MeanShift().fit(combined_matrix)
        
        # Create clusters based on cluster centers
        cluster_centers = clustering.cluster_centers_
        labels = clustering.labels_
        clusters = {}
        for i, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(messages[i])
        
        # Add clusters to conversations
        conversations.extend(clusters.values())
        return conversations

    """
    def cluster_maker(self, messages, bandwidth=0.5, time_threshold=3600):
        
        Cluster messages based on their semantic similarity and when they was send.
        @param messages: Messages to be clustered
        @type messages: List[tuple]
        @return: Clustered messages
        @rtype: List[List[tuple]]
        
        clusters = []
        n_messages = len(messages)
        similarity_matrix = self.semantic_similarity(messages)
        clustering = MeanShift(bandwidth=bandwidth)
        cluster_labels = clustering.fit_predict(similarity_matrix)
        for cluster_id in range(max(cluster_labels) + 1):
            cluster = []
            for idx, label in enumerate(cluster_labels):
                if label == cluster_id:
                    cluster.append(messages[idx])
            clusters.append(cluster)
        final_clusters = []
        for cluster in clusters:
            if not final_clusters:
                final_clusters.append(cluster)
            else:
                merged = False
                for existing_cluster in final_clusters:
                    if abs(cluster[0][2] - existing_cluster[-1][2]) <= time_threshold:
                        existing_cluster.extend(cluster)
                        merged = True
                        break
                if not merged:
                    final_clusters.append(cluster)
        return final_clusters
    """

    ########
    #TOPICS#
    ########
    
    def topics_last(self, messages):
        """
        Extract topics from the given messages, focusing on the last cluster of messages.
        @param messages: Messages to extract topics from
        @type messages : List[tuple]
        @return: Dictionary containing topics and their scores
        @rtype: Dict[str, float]
        """
        if not messages or len(messages) < 2:
            return {}

        clusters = self.cluster_maker(messages)

        # Initialize dictionary to store topic distributions
        topics_distribution = {}

        for c in clusters:
            if messages[1] in c:
                content = ""
                for cl in c:
                    content += f"{cl[1]}\n"
                # Split content into chunks to avoid large clusters
                chunks = self.split_input_by_max_length(content)
                for chunk in chunks:
                    # Extract topics from each chunk
                    distributions = self.pipeline_topics([chunk], top_k=None)
                    other_score = 0
                    for i, distribution in enumerate(distributions[0]):
                        label = distribution['label']
                        score = distribution['score']
                        if i < 5 and score > 0.08:
                            topics_distribution[label] = topics_distribution.get(label, 0) + score
                        else:
                            other_score += score
                    topics_distribution['Autres'] = topics_distribution.get('Autres', 0) + other_score

        return topics_distribution

    def topics(self, messages):
        """
        Extract topics from the given messages.
        @param messages: Messages to extract topics from
        @type messages : List[tuple]
        @return: Dictionary containing topics and their scores
        @rtype: Dict[str, float]
        """
        # Cluster all messages
        clusters = self.cluster_maker(messages)
        
        # Initialize dictionary to store topic distributions
        topics_distribution = {}
        
        for cluster_index, cluster_messages in enumerate(clusters):
            content = ""
            for message in cluster_messages:
                content += f"{message[1]}\n"
            
            # Split content into chunks to avoid large clusters
            chunks = self.split_input_by_max_length(content)
            
            # Initialize temporary dictionary to accumulate topic scores for each chunk
            temp_distribution = {}
            
            for chunk in chunks:
                # Extract topics from each chunk
                cluster_topics = self.pipeline_topics([chunk], top_k=None)
                
                # Accumulate topic scores for this chunk
                other_score = 0
                for i, distribution in enumerate(cluster_topics[0]):
                    label = distribution['label']
                    score = distribution['score']
                    if i < 5 and score > 0.08:
                        temp_distribution[label] = temp_distribution.get(label, 0) + score
                    else:
                        other_score += score
                temp_distribution['Autres'] = temp_distribution.get('Autres', 0) + other_score
            
            # Update final topic distribution with accumulated scores from all chunks
            for label, score in temp_distribution.items():
                topics_distribution[label] = topics_distribution.get(label, 0) + score
        
        return topics_distribution
