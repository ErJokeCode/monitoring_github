from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, Self, dataclass_transform
from infrastructure.context import StoryContext


@dataclass_transform()
class BaseStory:
    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "__annotations__"):
            dataclass(cls)

    @asynccontextmanager
    async def begin(self) -> AsyncIterator[Self]:
        async with StoryContext.begin():
            yield self

    async def begin_in_depends(self) -> AsyncIterator[Self]:
        async with StoryContext.begin():
            yield self
    
    @asynccontextmanager
    async def begin_without_transaction(self) -> AsyncIterator[Self]:
        yield self
