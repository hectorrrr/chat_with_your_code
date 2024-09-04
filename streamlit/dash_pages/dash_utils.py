
def map_graph_data(records):
    mapped_nodes = []
    mapped_relationships = []

    # Helper to create a node mapping
    def create_node(node):
        return {
            'data': {
                'id': node['name'],
                'label': node['name'],
                'description': node.get('description', 'No description provided'),
                "file_path": node.get('file_path'),
                'highlighted': False
            },
            'position': {'x': 75, 'y': 75},  # Static position; adjust as needed for layout
            'classes': list(node.labels)[0]  # Using the first label for CSS class
        }

    seen_nodes = set()  # Track seen nodes to avoid duplication in visualization

    # Process neomodel output
    for record in records[0]:
        start_node = record[0]
        relationship = record[1]
        end_node = record[2]

        start_node_id = start_node['name']
        end_node_id = end_node['name']
        relationship_type = relationship.type

        if start_node_id not in seen_nodes:
            mapped_nodes.append(create_node(start_node))
            seen_nodes.add(start_node_id)

        if end_node_id not in seen_nodes:
            mapped_nodes.append(create_node(end_node))
            seen_nodes.add(end_node_id)

        mapped_relationships.append({
            'data': {
                'source': start_node_id,
                'target': end_node_id,
                'type': relationship_type
            }
        })

    return mapped_nodes, mapped_relationships

def initial_query(db_connection):
    relationships_query = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    """
    output = db_connection.cypher_query(relationships_query)
    mapped_nodes, mapped_relationships = map_graph_data(output)
    return mapped_nodes, mapped_relationships

def specific_query(db_connection, query):
    output = db_connection.cypher_query(query)
    mapped_nodes, mapped_relationships = map_graph_data(output)
    return mapped_nodes, mapped_relationships