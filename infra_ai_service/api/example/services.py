from infra_ai_service.api.example.schemas import ExampleCreateSchema
from infra_ai_service.db.db import db_session
from infra_ai_service.db.models.example import Example
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ExampleService:
    def __init__(self, session: AsyncSession = Depends(db_session)):
        self.session = session

    async def get_all_examples(self) -> list[Example]:
        examples = await self.session.execute(select(Example))

        return examples.scalars().fetchall()

    async def create_example(self, data: ExampleCreateSchema) -> Example:
        example = Example(**data.dict())
        self.session.add(example)
        await self.session.commit()
        await self.session.refresh(example)

        return example
