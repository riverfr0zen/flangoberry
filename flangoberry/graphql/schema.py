import strawberry
from strawberry.types import Info
from . import mutations as core_mutations


@strawberry.type
class Query:
    @strawberry.field
    def egfield(self, info: Info, test_var: str) -> str:
        test_header = info.context["request"].headers.get(
            "Test-Header", "No Test-Header provided"
        )
        return f"Example field, {test_header}, {test_var}"


@strawberry.type
class Mutation:
    get_or_create_note = core_mutations.get_or_create_note
    get_or_create_bookmark = core_mutations.get_or_create_bookmark


schema = strawberry.Schema(query=Query, mutation=Mutation)
