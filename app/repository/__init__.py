class NotFoundError(Exception):
    def __init__(self, entity_data):
        super().__init__(f"entity not found, from {entity_data}")