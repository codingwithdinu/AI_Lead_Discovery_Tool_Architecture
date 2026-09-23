from abc import ABC,abstractmethod
from datetime import datetime
from app.activity import LinkedInActivity

class LinkedInActivityProvider(ABC):
    name="base"

    @abstractmethod
    async def search(
        self,
        query:str,
        start:datetime,
        end:datetime,
        limit:int=100,
        country:str|None=None,
        location:str|None=None,
    )->list[LinkedInActivity]:
        raise NotImplementedError
