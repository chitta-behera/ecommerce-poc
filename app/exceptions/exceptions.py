class NotFoundException(Exception):
    def __init__(self, entity_name: str, entity_id: int):
        self.entity_name = entity_name
        self.entity_id = entity_id
        super().__init__(f"{entity_name} with id {entity_id} not found")


class ValidationException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
