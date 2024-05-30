import pytest
from util.subject import Subjector, Feed

RSS_FEED = """\
<rss version="2.0">
<channel>
    <title>XUL</title>
    <link>https://www.xul.fr</link>
    <description></description>
    <item>
        <title>XUL news</title>
        <link>https://www.xul.fr/index.php</link>
        <description>... some text...</description>
    </item> 
</channel>
</rss>
"""

# Fixtures ------------------------------------------------


@pytest.fixture
def feed_instance(mocker):
    patch_feed(mocker)
    feed = Feed(None, None)
    return feed


# Utilities -----------------------------------------------


def patch_feed(mocker):
    mocker.patch("util.subject.Feed._Feed__fetch_feed", return_value=RSS_FEED)


def check_entry(entry):
    assert isinstance(entry.title, str)
    assert isinstance(entry.link, str)
    assert isinstance(entry.description, str)


# Tests ---------------------------------------------------


@pytest.mark.asyncio
async def test_feed(feed_instance):
    await feed_instance.update()
    entry = feed_instance.get_random_entry()
    check_entry(entry)


@pytest.mark.asyncio
async def test_subjector(mocker):
    patch_feed(mocker)
    subjector = Subjector()
    await subjector.update()
    entry = subjector.get_random_entry("Politique")
    check_entry(entry)
    subjector.close()
