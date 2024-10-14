import inspect

from IPython.display import Markdown, display


def display_class_definition(class_name: type) -> None:
    """
    Display the source code of a given class using Markdown formatting.

    Args:
        class_name (type): The class whose source code is to be displayed.

    Returns:
        None
    """
    display(Markdown(f"```{inspect.getsource(class_name)}```"))