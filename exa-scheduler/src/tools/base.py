from abc import ABC, abstractmethod
from typing import Any, Dict, Type
from pydantic import BaseModel, ConfigDict
from pydantic.json_schema import models_json_schema

class BaseTool(BaseModel, ABC):
    """
    Abstract base class for all tools.
    Inherits from Pydantic's BaseModel for automatic schema generation.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    description: str

    @abstractmethod
    def run(self, **kwargs) -> Any:
        """
        Execute the tool with the given arguments.
        """
        pass

    @classmethod
    def to_openai_schema(cls) -> Dict[str, Any]:
        """
        Generates the JSON schema for this tool formatted for OpenAI's API.
        This strips out the 'run' method and other internal fields, focusing on
        the arguments required by the tool.
        """
        # We need the schema of the inputs, which might be the model itself
        # excluding 'name' and 'description' if they are just metadata,
        # but for simplicity, let's assume the tool arguments are defined as fields 
        # on the subclass.
        
        properties = cls.model_json_schema().get("properties", {})
        
        # Remove metadata fields from the parameters schema
        if "name" in properties:
            del properties["name"]
        if "description" in properties:
            del properties["description"]

        # Create the parameters object
        parameters = {
            "type": "object",
            "properties": properties,
            "required": [k for k in properties.keys()] # Assume all remaining fields are arguments
        }
        
        return {
            "type": "function",
            "function": {
                "name": cls.model_fields['name'].default if cls.model_fields.get('name') and cls.model_fields['name'].default else cls.__name__,
                "description": cls.model_fields['description'].default if cls.model_fields.get('description') and cls.model_fields['description'].default else cls.__doc__,
                "parameters": parameters,
            }
        }
