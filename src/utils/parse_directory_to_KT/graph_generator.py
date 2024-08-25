
import os
import ast
import inspect
from neomodel import db

def parse_python_file(file_path):
    """
    Parses a Python file to extract class names, their docstrings, and functions with their details.
    
    Args:
        file_path (str): The path of the Python file to parse.

    Returns:
        dict: A dictionary containing lists of class names and functions with their details.
    """
    functions = []
    classes = []

    with open(file_path, "r") as file:
        file_content = file.read()
        tree = ast.parse(file_content)

        class_blocks = []  # To store class code blocks

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                class_docstring = ast.get_docstring(node) or ""
                class_code = ast.get_source_segment(file_content, node)
                sanitized_code = " ".join(class_code.splitlines())[:1000]  # Truncate to 1000 chars
                classes.append({
                    'name': class_name,
                    'description': class_docstring[:1000],  # Truncate to 1000 chars
                    'code': sanitized_code
                })
                # Store class blocks to help determine if a function is inside a class
                class_blocks.append(class_code)

            elif isinstance(node, ast.FunctionDef):
                func_name = node.name
                func_docstring = ast.get_docstring(node) or ""
                func_code = ast.get_source_segment(file_content, node)
                # Check if the function is inside any class block
                inside_class = any(func_code in class_code for class_code in class_blocks)

                # If not inside any class block, treat it as a standalone function
                if not inside_class:
                    sanitized_code = " ".join(func_code.splitlines())[:1000]  # Truncate to 1000 chars
                    functions.append({
                        'name': func_name,
                        'description': func_docstring[:1000],  # Truncate to 1000 chars
                        'code': sanitized_code
                    })

    return {"functions": functions, "classes": classes}

def create_graph_for_directory(db,base_path, nodes_relationships):
    """
    Iterates over a directory structure and creates nodes and relationships in the Neo4j graph using neomodel.
    
    Args:
        base_path (str): The base path of the directory to start creating nodes and relationships.
        nodes_relationships (list): The list containing node types and their relationships.
    """
    created_nodes = {}

    # First, create all nodes
    for root, dirs, files in os.walk(base_path):
        folder_name = os.path.basename(root)
        node_info = get_node_info(folder_name, nodes_relationships)

        if node_info:
            label = node_info['label']
            node_name = node_info['name']

            # Create parent nodes like Area, SubArea, or Framework
            if label not in created_nodes:
                created_nodes[label] = {}
            if node_name not in created_nodes[label]:
                query = f"MERGE (n:{label} {{name: $name}}) RETURN n"
                print("Executing query for node creation:", query)
                db.cypher_query(query, {'name': node_name})
                created_nodes[label][node_name] = True
                print(f"Created node: {label} - {node_name}")
                print("Runned query--->", f"MERGE (n:{label} name: {node_name}) RETURN n")

            # Process files within the folder to create class and function nodes
            for file_name in files:
                if file_name.endswith('.py'):
                    file_path = os.path.join(root, file_name)
                    relative_file_path = os.path.relpath(file_path, base_path)
                    parsed_data = parse_python_file(file_path)

                    # Create nodes for classes
                    for class_data in parsed_data["classes"]:
                        query = """
                        MERGE (c:Class {name: $name})
                        ON CREATE SET c.description = $description, c.code = $code, c.file_path = $file_path
                        RETURN c
                        """
                        print("Executing query for class node creation:", query)
                        db.cypher_query(query, {
                            'name': class_data['name'],
                            'description': class_data['description'],
                            'code': class_data['code'],
                            'file_path': relative_file_path
                        })
                        print(f"Created Class node: {class_data['name']} with file path {relative_file_path}")
                        print("Runned query--->", f"""
                                        MERGE (c:Class name:{class_data['name']})
                                        ON CREATE SET c.description = $description, c.code = $code, c.file_path = $file_path
                                        RETURN c
                                        """)

                    # Create nodes for standalone functions
                    for function in parsed_data["functions"]:
                        query = """
                        MERGE (f:Function {name: $name})
                        ON CREATE SET f.description = $description, f.code = $code, f.file_path = $file_path
                        RETURN f
                        """
                        print("Executing query for function node creation:", query)
                        db.cypher_query(query, {
                            'name': function['name'],
                            'description': function['description'],
                            'code': function['code'],
                            'file_path': relative_file_path
                        })
                        print(f"Created Function node: {function['name']} with file path {relative_file_path}")
                        print("Query--->", f"""
                        MERGE (f:Function name:{function['name']})
                        ON CREATE SET f.description = $description, f.code = $code, f.file_path = $file_path
                        RETURN f
                        """)

    # Now, establish the relationships after all nodes are created
    for item in nodes_relationships:
        node_name = item['name']
        label = item['label']
        relationships = item.get('relationships', {})
        
        for rel_type, targets in relationships.items():
            for target_name in targets:
                target_label = None
                # Determine the label of the target node
                for target_item in nodes_relationships:
                    if target_item['name'] == target_name:
                        target_label = target_item['label']
                        break
                
                if target_label:
                    # Create relationship based on the target's label
                    relationship_query = (
                        f"MATCH (p:{label} {{name: $parent_name}}), (t:{target_label} {{name: $target_name}}) "
                        f"MERGE (p)-[:{rel_type.upper()}]->(t)"
                    )
                    print("Executing relationship query:", relationship_query)
                    db.cypher_query(relationship_query, {'parent_name': node_name, 'target_name': target_name})
                    print(f"Created relationship: {label} - {node_name} -> {rel_type.upper()} -> {target_label} - {target_name}")
                    print("With query--->", f"MATCH (p:{label} name: {node_name}), (t:{target_label} name:{target_name}) ")

    # Establish relationships between Frameworks and their classes/functions
    for root, dirs, files in os.walk(base_path):
        folder_name = os.path.basename(root)
        node_info = get_node_info(folder_name, nodes_relationships)

        if node_info:
            label = node_info['label']
            node_name = node_info['name']

            # Process files within the folder to create relationships between frameworks and their classes/functions
            for file_name in files:
                if file_name.endswith('.py'):
                    parsed_data = parse_python_file(os.path.join(root, file_name))

                    # Create relationship between parent node (Framework) and Class
                    for class_data in parsed_data["classes"]:
                        relationship_query = (
                            f"MATCH (p:{label} {{name: $parent_name}}), (c:Class {{name: $class_name}}) "
                            "MERGE (p)-[:CONTAINS_CLASS]->(c)"
                        )
                        print("Executing class relationship query:", relationship_query)
                        db.cypher_query(relationship_query, {'parent_name': node_name, 'class_name': class_data['name']})
                        print(f"Created relationship: {label} - {node_name} -> Class {class_data['name']}")

                    # Create relationship between parent node (Framework) and Function
                    for function in parsed_data["functions"]:
                        relationship_query = (
                            f"MATCH (p:{label} {{name: $parent_name}}), (f:Function {{name: $func_name}}) "
                            "MERGE (p)-[:CONTAINS_FUNCTION]->(f)"
                        )
                        print("Executing function relationship query:", relationship_query)
                        db.cypher_query(relationship_query, {'parent_name': node_name, 'func_name': function['name']})
                        print(f"Created relationship: {label} - {node_name} -> Function {function['name']}")

def get_node_info(folder_name, nodes_relationships):
    """
    Retrieves the node information (label and name) for a given folder based on predefined relationships.
    
    Args:
        folder_name (str): The name of the folder to be mapped to a node type.
        nodes_relationships (list): The list containing node types and their relationships.

    Returns:
        dict: A dictionary containing the label and name of the node if found, otherwise None.
    """
    for item in nodes_relationships:
        if item['name'].lower() == folder_name.lower():
            return {'label': item['label'], 'name': item['name']}
    return None

