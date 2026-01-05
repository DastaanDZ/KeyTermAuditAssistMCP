import json
from fastmcp import FastMCP
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP
# Using specific logic from your reference: 
mcp = FastMCP(name="audit-assist-mcp", version="1.0.0")
print("Server running (Production mode config)")

# --------------------------------
# Constants / Configuration
# --------------------------------
BASE_URL_CLASSIFICATION = "http://keytermauditassistpython.onrender.com/keyterms"
BASE_URL_DETAILS = "https://keytermauditassistpython.onrender.com/keyterm"

# --------------------------------
# Tool 1: Check Classification
# --------------------------------
@mcp.tool(
    name="check_keyterm_classification",
    description="Check system classified values to verify if an admin has changed them. Returns keyterm classification data including User Value and System Edit."
)
async def check_keyterm_classification(order_number: int, keyterm_code: str = None):
    params = {"order_number": order_number}
    if keyterm_code:
        params["keyterm_code"] = keyterm_code

    try:
        # ADD follow_redirects=True to handle 301/302 responses automatically
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(BASE_URL_CLASSIFICATION, params=params)
            response.raise_for_status()
            data = response.json()
            
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": f"✅ Classification Data Retrieved:\n{json.dumps(data, indent=2)}"
                    }
                ]
            }
    except httpx.HTTPStatusError as e:
        return {
            "content": [{"type": "text", "text": f"❌ API Error: {e.response.status_code} - {e.response.text}"}],
            "isError": True,
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"❌ Connection Error: {str(e)}"}],
            "isError": True,
        }

# --------------------------------
# Tool 2: Get Keyterm Details
# --------------------------------
@mcp.tool(
    name="get_keyterm_definition_and_regex",
    description="Get keyterm information, calculation logic, and regex used for extraction based on section headers and paragraph text."
)
async def get_keyterm_details(keyterm: str):
    """
    Tool: Fetches the definition, regex, and 'must' conditions for a specific keyterm.
    args:
        keyterm: The name of the keyterm (e.g., 'Recovery Time Objective')
    """
    params = {"keyterm": keyterm}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BASE_URL_DETAILS, params=params)
            response.raise_for_status()
            data = response.json()

            # Formatting the output for better readability
            description = data.get("description", "N/A")
            regex = data.get("regex", "N/A")
            
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": f"✅ Keyterm Details for '{keyterm}':\n\nDescription: {description}\n\nRegex: {regex}\n\nFull Data: {data}"
                    }
                ]
            }
    except httpx.HTTPStatusError as e:
        return {
            "content": [{"type": "text", "text": f"❌ API Error: {e.response.status_code} - {e.response.text}"}],
            "isError": True,
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"❌ Connection Error: {str(e)}"}],
            "isError": True,
        }

# --------------------------------
# Run
# --------------------------------
if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
