import inspect

from ..library import Class, DataDescriptor, Method


# define this here so we know what "1" indent is and can remove it for inner
# class declarations
DEFAULT_INDENT_WIDTH = 4


def attributes(attributes, indent) -> str:
    attrs = []
    for name, definitions in attributes.items():
        value = definitions[-1].value

        if isinstance(value, str):
            value = f'"{value}"'

        if inspect.isclass(value):
            value = value.__name__

        attrs.append(f"{indent}{name} = {value}\n")
    return "".join(attrs)


def classes(classes, indent) -> str:
    content = [to_string(c, indent=indent + indent) for c in classes]
    return "".join(content)


def declaration(name, parents, indent) -> str:
    indent = indent[:-DEFAULT_INDENT_WIDTH]
    content = f"{indent}class {name}"

    if parents:
        parents = ", ".join([p.__name__ for p in parents])
        content = f"{content}({parents})"

    return f"{content}:"


def docstring(docstring, indent) -> str:
    if not docstring:
        return ""

    quotes = f'{indent}"""\n'
    lines = docstring.split("\n")
    block = "".join([f"{indent}{line}\n" for line in lines])
    return f"{quotes}{block}{quotes}"


def methods(methods: dict[str, list[Method]], indent) -> str:
    content = ""
    for definitions in methods.values():
        for i, method in enumerate(definitions):
            if len(definitions) > 1 and i == 0:
                content += f"{indent}# Defined on: {method.defining_class.name}\n"
            lines = method.code.split("\n")[:-1]
            for line in lines:
                # TODO: dedent code at source so defined indent isn't tied to
                # presentation indent
                content += f"{indent}{line[4:]}\n"
            content += "\n"

    # add strip to remove the trailing newline, rather than polluting the loop
    # with logic to work out if we're on the final loop iteration
    return content.strip("\n")


def properties(properties: dict[str, list[Method]], indent) -> str:
    content = ""
    for definitions in properties.values():
        for i, prop in enumerate(definitions):
            if len(definitions) > 1 and i == 0:
                content += f"{indent}# Defined on: {prop.defining_class.name}\n"
            lines = prop.code.split("\n")[:-1]
            for line in lines:
                # TODO: dedent code at source so defined indent isn't tied to
                # presentation indent
                content += f"{indent}{line[4:]}\n"
            content += "\n"

    return content


def data_descriptors(data_descriptors: dict[str, list[DataDescriptor]], indent) -> str:
    """
    KISS to start: display any methods for a dd as a group
    Loop the definitions of each name
    try each of getter, setter, and deleter, outputting them as a method
    """
    content = ""
    for definitions in data_descriptors.values():
        for i, descriptor in enumerate(definitions):
            for name in ["getter", "setter", "deleter"]:
                func = getattr(descriptor, name)

                if len(definitions) > 1 and i == 0:
                    content += f"{indent}# Defined on: {func.defining_class.name}\n"

                lines = func.code.split("\n")[:-1]
                for line in lines:
                    # TODO: dedent code at source so defined indent isn't tied
                    # to presentation indent
                    content += f"{indent}{line[4:]}\n"
                content += "\n"

    return content


def to_string(structure: Class, indent: str = " " * DEFAULT_INDENT_WIDTH) -> str:
    content = declaration(structure.name, structure.parents, indent)
    content += "\n"
    content += docstring(structure.docstring, indent) if docstring else ""
    content += attributes(structure.attributes, indent)
    content += "\n"
    content += classes(structure.classes, indent)
    content += properties(structure.properties, indent)
    content += data_descriptors(structure.data_descriptors, indent)
    content += methods(structure.methods, indent)

    return content
