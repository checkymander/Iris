import json
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from pydantic import BaseModel, Extra, root_validator, validator, PrivateAttr

if TYPE_CHECKING:
    from gql import Client


class GraphQLAPIWrapper(BaseModel):
    """Wrapper around GraphQL API.

    To use, you should have the ``gql`` python package installed.
    This wrapper will use the GraphQL API to conduct queries.
    """

    custom_headers: Optional[Dict[str, str]] = None
    graphql_endpoint: str
    gql_client: "Client"  #: :meta private:
    gql_function: Callable[[str], Any]  #: :meta private:


    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that the python package exists in the environment."""

        headers = values.get("custom_headers", {})

        try:
            from gql import Client, gql
            from gql.transport.requests import RequestsHTTPTransport

            transport = RequestsHTTPTransport(
                url=values["graphql_endpoint"],
                headers=headers or None,
                verify=False
            )

            client = Client(transport=transport, fetch_schema_from_transport=True)
            values["gql_client"] = client
            values["gql_function"] = gql
        except ImportError:
            raise ValueError(
                "Could not import gql python package. "
                "Please install it with `pip install gql`."
            )
        return values

    def run(self, query: str, variables: dict) -> str:
        """Run a GraphQL query and get the results."""
        result = self._execute_query(query, variables)
        return json.dumps(result, indent=2)

    def _execute_query(self, query: str, variables: dict) -> Dict[str, Any]:
        """Execute a GraphQL query and return the results."""
        try:
            real_query = "query GetCallbacks{callback(where:{_not:{payload:{payloadtype:{_not:{name:{_neq:\"iris\"}}}}}}){active agent_callback_id architecture description domain external_ip host id init_callback integrity_level ip last_checkin os pid process_name timestamp user}}"
            document_node = self.gql_function(real_query)
            result = self.gql_client.execute(document_node, {})
        except Exception as e:
            return e
        return result