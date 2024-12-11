from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
from .GraphQLAPIWrapper import GraphQLAPIWrapper
import json

class GraphQLToolSchema(BaseModel):
    query: str = Field(description="should be a graphql query")
    #variables: Optional[dict] = Field(description="optinoal dictionary of variables for the query")

class ExecuteGraphQLQueryTool(BaseTool):

    graphql_wrapper: GraphQLAPIWrapper

    name = "ExecuteGraphQLQueryTool"
    description = """\
        Input to this tool is a detailed and correct Hasura GraphQL query.
        If the query is not correct, an error message will be returned.
        If an error is returned tell the user what error was returned
        If an error is returned with 'Unauthorized' in it, do not try again, but tell the user to change their authentication.

        Example Input: query GetCallbacks{callback(where:{_not:{payload:{payloadtype:{_not:{name:{_neq:"iris"}}}}}}){active agent_callback_id architecture description domain external_ip host id init_callback integrity_level ip last_checkin os pid process_name timestamp user}}
        Example Input: query GetCallback {callback(where: {agent_callback_id: {_eq: "a934b822-a3cd-4e34-844b-a715e1170c8a"}}) {active agent_callback_id architecture description domain external_ip host id init_callback integrity_level ip last_checkin os pid process_name timestamp user}}

        use this tool when you need to execute a GraphQL query against an external API

        To use the tool, you must provide at least the 'query' parameter:
        ['query']

        Be sure to close out your query, a valid GraphQL query ends in }
    """
    args_schema: Type[GraphQLToolSchema] = GraphQLToolSchema

    def _run(self, query: str) -> str:
        """
        Execute a GraphQL query and return the response.

        :param query: A string containing a GraphQL query.
        :return: The json response from the GraphQL API.
        """

        result = self.graphql_wrapper.run(query, {})
        return json.dumps(result, indent=2)


    def _arun(self, query: str, variables: dict = {}) -> str:
        raise NotImplementedError("This tool does not support async")