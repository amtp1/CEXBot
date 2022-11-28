def read_local_file(path: str) -> bytes:
    with open(path, "rb") as f:
        file = f.read()
        f.close()
    return file
