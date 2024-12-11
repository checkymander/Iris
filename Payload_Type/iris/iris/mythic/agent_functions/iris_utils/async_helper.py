import asyncio
import nest_asyncio

def run_async_function(func, *args, **kwargs):
    """
    Wraps the provided asynchronous function and executes it in a synchronous context.

    :param func: The asynchronous function to call.
    :param args: Positional arguments to pass to the function.
    :param kwargs: Keyword arguments to pass to the function.
    :return: The result of the asynchronous function.
    """
    nest_asyncio.apply()
    loop = asyncio.get_running_loop()
    task = loop.create_task(func(*args, **kwargs))
    loop.run_until_complete(task)
    return task.result()