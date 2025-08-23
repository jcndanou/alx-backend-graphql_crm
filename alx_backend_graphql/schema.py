# alx_backend_graphql_crm/schema.py
import graphene
import crm.schema


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")


class Mutation(crm.schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)