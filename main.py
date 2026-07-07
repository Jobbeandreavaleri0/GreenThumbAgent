from workflow import plant_care_workflow

def main():
    print("Welcome to the Green Thumb Plant Care Assistant!")
    print("-------------------------------------------------")
    print("Type 'quit' or 'exit' to stop.")
    
    session_id = "interactive_session"
    
    while True:
        user_input = input("\nWhat plant do you need help with? ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye! Happy planting!")
            break
            
        try:
            schedule = plant_care_workflow(user_input, session_id)
            print("\nPlant Care Schedule:")
            print(schedule)
        except Exception as e:
            print(f"\nError running workflow: {e}")

if __name__ == "__main__":
    main()
