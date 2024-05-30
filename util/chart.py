import io
import matplotlib.pyplot as plt


class ChartHelper:
    """
    Helper class to generate pie charts.
    """

    @staticmethod
    def create_pie_chart(data, colors=None, title=None):
        """
        Generate a pie chart image.

        @param data: Dictionary where keys are labels and values are counts for each category.
        @type data: dict
        @param colors: List of colors for each category (optional).
        @type colors: list[str], optional
        @param title: Title of the pie chart (optional).
        @type title: str, optional
        @return: BytesIO object containing the image.
        @rtype: io.BytesIO
        """
        # Extract labels and counts from the dictionary
        labels = list(data.keys())
        counts = list(data.values())

        # Create a pie chart
        fig, ax = plt.subplots()
        ax.pie(counts, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors)
        ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle

        # Add title to the pie chart
        if title:
            plt.title(title)

        # Convert the plot to bytes
        byte_io = io.BytesIO()
        plt.savefig(byte_io, format="png")
        plt.close()

        # Return the byte_io object
        byte_io.seek(0)
        return byte_io
