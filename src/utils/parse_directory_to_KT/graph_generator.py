
import ast
import os

def parse_python_file(file_path):
    """ Parse a Python file to extract functions and their docstrings. """
    with open(file_path, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read(), filename=file_path)

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node)
            functions.append((node.name, docstring))

    return functions

def create_graph_for_folder(folder_path, connection):
    # Create a node for the folder
    connection.create_node_with_label("Visualization", {"name": os.path.basename(folder_path)})

    # Iterate over files in the folder
    for file_name in os.listdir(folder_path):
        print(file_name)
        if file_name.endswith('.py'):
            file_path = os.path.join(folder_path, file_name)
            functions = parse_python_file(file_path)
            file_node_name = file_name[:-3]

            # Create a node for each file and connect it to the folder
            connection.create_node_with_label("Framework", {"name": file_node_name})
            print("Trying to write plotly")
            connection.run_query(
                """
                MATCH (v:Field {name: $folder_name}), (f:Framework {name: $file_name})
                MERGE (v)-[:CONTAINS]->(f)
                """,
                parameters={"folder_name": os.path.basename(folder_path), "file_name": file_node_name}
            )

            # Create nodes for functions and link them
            for func_name, docstring in functions:
                connection.create_node_with_label("Function", {"name": func_name, "description": docstring or "No description available"})
                connection.run_query(
                    """
                    MATCH (f:Framework {name: $file_name}), (func:Function {name: $func_name})
                    MERGE (f)-[:IMPLEMENTS]->(func)
                    """,
                    parameters={"file_name": file_node_name, "func_name": func_name}
                )