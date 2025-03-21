class ErrnoError(Exception):
    def __init__(self, errno:int) -> None:
        self.errno = errno
    def __str__(self) -> str:
        return f"错误码：{self.errno}"