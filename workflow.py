import requests
import urllib.parse
import warnings

# Suppress insecure request warnings for local testing
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def lookup_plant_care(plant_name: str) -> str:
    """Fetches real info from Wikipedia using their REST API."""
    try:
        # Format the plant name for the URL
        query = urllib.parse.quote(plant_name.title())
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        
        # We use verify=False to bypass local SSL certificate issues on your Windows machine
        headers = {'User-Agent': 'GreenThumbMockBot/1.0'}
        response = requests.get(url, verify=False, headers=headers)
        
        if response.status_code != 200:
            return f"ERROR: '{plant_name}' is not recognized."
            
        data = response.json()
        if 'extract' not in data:
            return f"ERROR: '{plant_name}' is not recognized."
            
        summary = data['extract'].lower()
        
        # Check if the summary mentions plant-related keywords
        plant_keywords = ['plant', 'tree', 'flower', 'fruit', 'herb', 'shrub', 'succulent', 'vine', 'fern', 'grass', 'leaf', 'botanical']
        if any(keyword in summary for keyword in plant_keywords):
            # Return real wiki summary + a generic fallback schedule
            return f"Found this info: {data['extract']} For care, generally water when topsoil is dry and ensure good light."
        else:
            return f"ERROR: '{plant_name}' does not seem to be a plant (Wikipedia thinks it is something else)."
            
    except Exception as e:
        return f"ERROR: '{plant_name}' could not be found."

# 2. DEFINE THE MULTI-AGENT SYSTEM USING ADK
from antigravity_adk import Agent, Workflow, InMemorySessionService

query_classifier_agent = Agent(
    name="QueryClassifierAgent",
    instructions="You are an expert in Natural Language Understanding. Extract the plant name and soil context into a JSON structure."
)

# Agent 1: The Botanist
botanist_agent = Agent(
    name="BotanistAgent",
    instructions="You are an expert botanist. Use the lookup_plant_care tool to find care rules and explain them simply to the user.",
    tools=[lookup_plant_care]
)

# Agent 2: The Soil Analyst
soil_agent = Agent(
    name="SoilAnalystAgent",
    instructions="You analyze the plant's soil needs based on the botanist's report and recommend soil mixtures."
)

# Agent 3: The Scheduler
scheduler_agent = Agent(
    name="SchedulerAgent",
    instructions="You take raw plant care rules and soil advice, and format them into a crisp, bulleted Monday-to-Sunday weekly care schedule."
)

# 3. DEFINE THE WORKFLOW (Sequential Execution)
def plant_care_workflow(plant_name: str, session_id: str):
    session = InMemorySessionService.get_or_create(session_id)
    
    # 1. NLU Router processes raw input into JSON
    nlu_response = query_classifier_agent.run(plant_name, context=session)
    
    # 2. Botanist gets JSON and fetches info
    botanist_response = botanist_agent.run(nlu_response, context=session)
    
    # 3. Soil Analyst gets JSON to check custom soil context
    soil_response = soil_agent.run(nlu_response, context=session)
    
    combined_context = f"Botanist: {botanist_response}\nSoil Analyst: {soil_response}"
    final_schedule = scheduler_agent.run(combined_context, context=session)
    
    return final_schedule
