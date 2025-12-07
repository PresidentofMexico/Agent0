from src.tools.base import BaseTool
import json

class TestTool(BaseTool):
    name: str = "test_tool"
    description: str = "A test tool"
    arg1: int

schema = TestTool.to_openai_schema()
print(json.dumps(schema, indent=2))
