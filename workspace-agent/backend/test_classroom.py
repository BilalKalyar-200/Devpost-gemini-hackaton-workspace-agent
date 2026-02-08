import asyncio
from connectors.classroom_connector import ClassroomConnector
from config import config

async def test():
    print("="*60)
    print("🔍 GOOGLE CLASSROOM DEBUG TEST")
    print("="*60)
    
    classroom = ClassroomConnector(
        credentials_file=config.CREDENTIALS_FILE,
        token_file=config.TOKEN_FILE,
        scopes=config.SCOPES
    )
    
    # Test with 30 days window to catch more
    assignments = await classroom.get_upcoming_assignments(days_ahead=30)
    
    print("\n" + "="*60)
    print(f"📊 RESULTS: Found {len(assignments)} assignments")
    print("="*60)
    
    if assignments:
        for i, a in enumerate(assignments, 1):
            print(f"\n{i}. {a.title}")
            print(f"   Course: {a.course_name}")
            print(f"   Due: {a.due_date}")
            print(f"   Points: {a.points_possible}")
            print(f"   Status: {a.status}")
    else:
        print("\n⚠️ No assignments found!")
        print("\nPossible reasons:")
        print("1. You're enrolled as a TEACHER, not a STUDENT")
        print("2. Assignments are outside the 30-day window")
        print("3. Assignments have no due date set")
        print("4. You're not enrolled in any active courses")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(test())