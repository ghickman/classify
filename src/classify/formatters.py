INDENT = " " * 4


def html(structure, template):
    return template.render(klass=structure)


def paged(structure):
    def attributes(attributes):
        attrs = []
        for name, definitions in attributes.items():
            obj = definitions[-1]["object"]
            attrs.append(f"{INDENT}{name} = {obj}\n")
        return "".join(attrs)

    def declaration(name, parents):
        parents = ", ".join([p.__name__ for p in parents])
        return f"class {name}({parents}):"

    def docstring(docstring):
        quotes = f'{INDENT}"""\n'
        lines = docstring.split("\n")
        block = "".join([f"{INDENT}{line}\n" for line in lines])
        return f"{quotes}{block}{quotes}"

    def methods(methods):
        content = ""
        for definitions in methods.values():
            for d in definitions:
                lines = d["code"].split("\n")[:-1]
                for line in lines:
                    content += f"{INDENT}{line[4:]}\n"
                content += "\n"
        return content

    def parents(parents):
        return ", ".join([p.__name__ for p in parents])

    content = declaration(structure["name"], structure["parents"])
    content += "\n"
    if docstring:
        content += docstring(structure["docstring"])
    content += attributes(structure["attributes"])
    content += "\n"
    content += methods(structure["methods"])
    return content
