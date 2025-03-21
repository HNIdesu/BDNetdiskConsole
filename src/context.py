from version import get_version
class Context:
    def __init__(self) -> None:
        self.username:str = None
        self.access_token:str = None
        self.current_directory:str = "/"
    @property
    def version(self)->str:
        return get_version()
    @property
    def prompt(self)->str:
        if self.access_token:
            return f"{self.username}:{self.current_directory}$ "
        else:
            return "$ "