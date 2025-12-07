from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Optional, ClassVar
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
    args_model: ClassVar[Optional[Type[BaseModel]]] = None

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
        """
        schema_src = cls
        parameters = {}
        
        # Check if the class has an 'args_model' ClassVar set
        if cls.args_model is not None:
            schema_src = cls.args_model
            properties = schema_src.model_json_schema().get("properties", {})
            parameters = {
                "type": "object",
                "properties": properties,
                "required": list(properties.keys())
            }
        else:
            # Fallback to current behavior: Schema of the tool itself minus metadata
            properties = cls.model_json_schema().get("properties", {})
            if "name" in properties: del properties["name"]
            if "description" in properties: del properties["description"]
            
            parameters = {
                "type": "object",
                "properties": properties,
                "required": list(properties.keys())
            }
        
        return {
            "type": "function",
            "function": {
                "name": cls.model_fields['name'].default if cls.model_fields.get('name') and cls.model_fields['name'].default else cls.__name__,
                "description": cls.model_fields['description'].default if cls.model_fields.get('description') and cls.model_fields['description'].default else cls.__doc__,
                "parameters": parameters,
            }
        }
