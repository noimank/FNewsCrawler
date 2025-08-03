import pandas as pd

from fnewscrawler.core import get_redis



def test_set_key():

    client = get_redis()
    client.set("key", "value")
    assert client.get("key") == "value"
    get_key = client.get("key")
    print(get_key)



def    test_df():
    client = get_redis()
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    client.set("df", df, serializer="pickle")
    get_df = client.get("df", serializer="pickle")
    print(get_df)


def test_list():
    client = get_redis()
    client.lpush("list", "1", "2", "3")
    get_list = client.lrange("list", 0, -1)
    print(get_list)

def test_set_text():
    client = get_redis()
    client.set("text", "value")
    assert client.get("text") == "value"


if __name__ == '__main__':
    # test_df()
    # test_list()
    test_set_text()

