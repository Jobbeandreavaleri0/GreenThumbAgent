import re

class InMemorySessionService:
    @staticmethod
    def get_or_create(session_id):
        return {"session_id": session_id, "history": []}

class Agent:
    def __init__(self, name, instructions, tools=None):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []

    def run(self, user_input, context=None):
        print(f"[{self.name}] Thinking...")
        import json
        import re
        
        if self.name == "QueryClassifierAgent":
            # Mock NLU extraction to handle context (Italian/English)
            # Split by common punctuation or keywords to separate plant from context
            parts = re.split(r'[.,;]|\b(the soil is|my soil is|il terreno è|il terreno|soil)\b', user_input, 1, flags=re.IGNORECASE)
            
            plant_name = parts[0].strip()
            # Clean up plant name just in case
            prefixes = ["how do i care for my", "tell me about", "what is a", "is the", "care for"]
            for p in prefixes:
                if plant_name.lower().startswith(p):
                    plant_name = plant_name[len(p):].strip()
            plant_name = plant_name.strip("?.! ")
            
            soil_context = ""
            if len(parts) > 1 and parts[-1]:
                soil_context = parts[-1].strip("?.! ")
            else:
                soil_context = "No specific soil context provided."
                
            return json.dumps({
                "plant_name": plant_name,
                "soil_context": soil_context
            })
            
        elif self.name == "BotanistAgent":
            try:
                data = json.loads(user_input)
                plant_name = data.get("plant_name", "").strip()
            except:
                # Fallback for old tests without NLU
                clean_input = user_input.lower()
                prefixes_to_remove = ["how do i care for my", "tell me about", "what is a", "is the", "care for"]
                for prefix in prefixes_to_remove:
                    if clean_input.startswith(prefix):
                        clean_input = clean_input.replace(prefix, "")
                plant_name = clean_input.strip("?.! ")
            
            if self.tools:
                tool_result = self.tools[0](plant_name)
                if "ERROR:" in tool_result:
                    return f"I couldn't find '{plant_name}' in the plant database. Are you sure that's a plant?"
                # Prefix the actual plant name so the Scheduler knows it
                return f"Name: {plant_name.title()}\n{tool_result}"
            return f"Botanist advice for: {user_input}"
            
        elif self.name == "SoilAnalystAgent":
            try:
                data = json.loads(user_input)
                soil_context = data.get("soil_context", "")
            except:
                soil_context = ""
                
            if "couldn't find" in user_input:
                return "No plant found, so no soil advice needed."
                
            if soil_context and soil_context != "No specific soil context provided.":
                return f"Taking into account the user's soil condition ('{soil_context}'), adjust your watering and use appropriate potting mix."
            return "Based on the botanist's report, ensure the soil has good drainage."
            
        elif self.name == "SchedulerAgent":
            if "couldn't find" in user_input:
                return "I'm sorry, but I can only create care schedules for real plants!"
                
            botanist_text = user_input.split("Botanist: ")[-1].split("Soil Analyst:")[0].replace("Found this info: ", "").strip()
            soil_text = user_input.split("Soil Analyst:")[-1].strip() if "Soil Analyst:" in user_input else "Check the drainage."
            
            # Extract the precise plant name passed by the Botanist
            plant_name = "Your Plant"
            if "Name: " in botanist_text:
                plant_name = botanist_text.split("\n")[0].replace("Name: ", "").strip()
                botanist_text = "\n".join(botanist_text.split("\n")[1:])
            
            # Split the wikipedia summary
            sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', botanist_text) if s.strip()]
            facts = " ".join([s for s in sentences if not s.startswith("For care")])
            
            # --- DYNAMIC SCHEDULE GENERATION based on Wikipedia text analysis ---
            lower_facts = facts.lower()
            lower_soil = soil_text.lower()
            is_tree = "tree" in lower_facts or "orchard" in lower_facts
            
            # 1. Determine watering needs based on habitat AND soil condition
            if "clay" in lower_soil or "argilla" in lower_soil:
                mon_task = f"CAUTION: Your soil is clay-heavy and retains water! Check moisture deep down for {plant_name} and hold off watering until it's completely dry to prevent root rot."
            elif "sand" in lower_soil or "sabbia" in lower_soil:
                mon_task = f"Since your sandy soil drains very quickly, check {plant_name} today. You may need to water it more frequently (e.g., twice a week)."
            elif "dry" in lower_soil or "secco" in lower_soil:
                mon_task = f"The soil was reported as very dry. Give {plant_name} a deep, slow soaking today to fully rehydrate the root zone."
            elif any(w in lower_facts for w in ["succulent", "cactus", "drier", "desert", "arid", "dry"]):
                mon_task = f"Check soil moisture. {plant_name} prefers dry conditions, so only water if the soil is bone dry."
            elif any(w in lower_facts for w in ["tropical", "rainforest", "humid", "moist", "water"]):
                mon_task = f"Water {plant_name} thoroughly. Consider misting the leaves to replicate its humid native environment."
            else:
                if is_tree:
                    mon_task = f"Check the soil around the base of the {plant_name}. Water deeply if the weather has been dry."
                else:
                    mon_task = f"Check soil moisture for {plant_name}. Water if the top inch feels dry."
                
            # 2. Determine maintenance tasks based on plant type
            if "flower" in lower_facts or "bloom" in lower_facts:
                wed_task = f"Inspect {plant_name}'s flowers. Remove any spent blooms (deadheading) to encourage new growth."
            elif is_tree or "shrub" in lower_facts:
                wed_task = f"Inspect {plant_name}'s branches. Prune any dead or crossing stems to maintain its structure."
            elif "vine" in lower_facts or "climb" in lower_facts:
                wed_task = f"Guide {plant_name}'s vines along its trellis or support structure."
            else:
                wed_task = f"Wipe {plant_name}'s leaves with a damp cloth to remove dust and help it photosynthesize."
                
            # 3. Determine lighting/placement based on native climate
            if is_tree:
                fri_task = f"Clear away any weeds or debris from the base of the {plant_name} and ensure the mulch layer is intact."
            elif any(w in lower_facts for w in ["sun", "mediterranean", "direct", "bright"]):
                fri_task = f"Ensure {plant_name} is getting plenty of direct sunlight. Rotate it 90 degrees."
            elif any(w in lower_facts for w in ["shade", "indirect", "understory", "forest"]):
                fri_task = f"Make sure {plant_name} is protected from harsh direct rays. Rotate it 90 degrees."
            else:
                fri_task = f"Rotate {plant_name} 90 degrees to ensure even, upright growth on all sides."

            # Build the final output
            schedule = f"🌿 **Botanical Info:**\n{facts}\n\n"
            
            # Make the Soil Analyst report clearly visible as a separate block
            if soil_text and soil_text != "Check the drainage.":
                schedule += f"🪨 **Soil Analyst Report:**\n{soil_text}\n\n"
                
            schedule += f"✨ **Your Weekly Care Schedule for {plant_name}** ✨\n\n"
            
            schedule += f"- **Monday**: {mon_task}\n"
            schedule += f"- **Wednesday**: {wed_task}\n"
            schedule += f"- **Friday**: {fri_task}\n"
            
            # Put a generic task for Sunday since the soil advice is now at the top
            if soil_text == "Check the drainage.":
                schedule += f"- **Sunday**: {soil_text}\n"
            else:
                schedule += f"- **Sunday**: Review the Soil Analyst report and monitor {plant_name}'s overall health.\n"
                        
            return schedule
        
        return "Task complete."

class Workflow:
    pass
