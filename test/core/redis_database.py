from fnewscrawler.core import get_redis



def test_set_key():

    client = get_redis()
    client.set("key", "value")
    assert client.get("key") == "value"
    get_key = client.get("key")
    print(get_key)


if __name__ == '__main__':
    test_set_key()

