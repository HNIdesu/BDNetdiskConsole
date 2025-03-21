from version import get_version
class Context:
    def __init__(self) -> None:
        self.username:str = None
        self.access_token:str = None
        self.current_directory:str = "/"
        self.need_relogin = False
    @property
    def is_logged_in(self)->str:
        return (not self.need_relogin) and self.access_token
    @property
    def version(self)->str:
        return get_version()
    @property
    def prompt(self)->str:
        if self.is_logged_in:
            return f"{self.username}:{self.current_directory}$ "
        else:
            return "$ "