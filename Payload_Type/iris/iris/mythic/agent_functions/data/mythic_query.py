from .irisgraphql import IrisGraphQLReader

async def query_all_data(reader: IrisGraphQLReader):
    await query_task_output(reader)
    await query_payloads(reader)
    await query_callbacks(reader)

async def query_task_output(reader: IrisGraphQLReader):
    task_query = """query GetTasks{task{id agent_task_id callback_id command_name completed display_params display_id is_interactive_task operator_id operation_id responses{id response_escape}parent_task_id}}"""
    await query_generic(reader,task_query)

async def query_payloads(reader:IrisGraphQLReader):
    await query_generic(reader, """query GetPayloads{payload(where:{_not:{payloadtype:{_not:{name:{_neq:"iris"}}}}}){id callbacks{agent_callback_id architecture crypto_type description display_id domain external_ip extra_info host id init_callback integrity_level ip last_checkin os operator_id operation_id pid process_name registered_payload_id timestamp user}}}""")

async def query_callbacks(reader: IrisGraphQLReader):
    await query_generic(reader, """query MyQuery{callback(where:{_not:{payload:{payloadtype:{_not:{name:{_neq:"iris"}}}}}}){active agent_callback_id architecture crypto_type current_time description display_id domain external_ip extra_info host id init_callback integrity_level ip last_checkin operation_id operator_id os pid process_name registered_payload_id sleep_info timestamp user loadedcommands{command{help_cmd cmd}}}}""")

async def query_generic(reader: IrisGraphQLReader, query: str):
    reader.load_data(query, variables={})