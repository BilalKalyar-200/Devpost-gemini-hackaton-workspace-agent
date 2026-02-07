from connectors.classroom_connector import ClassroomConnector
from config import config
import asyncio

async def test():
    print("Testing Classroom connection...\n")
    
    classroom = ClassroomConnector(
        credentials_file=config.CREDENTIALS_FILE,
        token_file=config.TOKEN_FILE,
        scopes=config.SCOPES
    )
    
    try:
        assignments = await classroom.get_upcoming_assignments(days_ahead=14)
        
        print(f"✅ Found {len(assignments)} assignments\n")
        
        if assignments:
            for i, a in enumerate(assignments, 1):
                print(f"{i}. {a.course_name}: {a.title}")
                print(f"   Due: {a.due_date.strftime('%B %d, %Y at %I:%M %p')}")
                print(f"   Points: {a.points_possible}")
                print(f"   Status: {a.status}")
                print()
        else:
            print("No upcoming assignments.")
            print("\nNote: This only shows assignments due in the next 14 days.")
        
        print("\n✅ Classroom is working!")
        
    except Exception as e:
        print(f"❌ Classroom error: {e}")
        print("\nThis is normal if:")
        print("- You're not enrolled in any Google Classroom courses")
        print("- You're a teacher (not a student)")
        print("- You don't use Google Classroom")
        print("\nThe agent will work fine with just Gmail and Calendar!")

if __name__ == "__main__":
    asyncio.run(test())