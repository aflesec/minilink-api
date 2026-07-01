import string

ALPHABET = string.digits + string.ascii_letters  # base62


def encode_base62(num: int) -> str:
    if num == 0:
        return ALPHABET[0]
    out = []
    while num > 0:
        num, rem = divmod(num, 62)
        out.append(ALPHABET[rem])
    return "".join(reversed(out))


class LinkStore:
    def __init__(self):
        print("[LinkStore] Store initialise")
        self._by_code = {}
        self._counter = 0

    def create(self, url: str) -> str:
        self._counter += 1
        code = encode_base62(self._counter)
        self._by_code[code] = url
        return code

    def resolve(self, code: str):
        return self._by_code.get(code)

    def size(self) -> int:
        return len(self._by_code)
