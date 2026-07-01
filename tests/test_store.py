from src.store import LinkStore, encode_base62
 
 
def test_encode_base62():
    assert encode_base62(0) == "0"
    assert encode_base62(61) == "Z"
 
 
def test_create_and_resolve():
    store = LinkStore()
    code = store.create("https://example.com")
    assert store.resolve(code) == "https://example.com"
