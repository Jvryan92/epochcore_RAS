#!/usr/bin/env python3
"""
Kids Friendly AI Demo

This script demonstrates the Kids Friendly AI Guide, providing simple
examples for explaining AI concepts to children in a positive way.
"""

from scripts.kids_friendly_ai_guide import AIFriendlyGuide
import os
import sys
from pathlib import Path

# Add the scripts directory to the Python path
scripts_dir = Path(__file__).resolve().parent
if str(scripts_dir) not in sys.path:
    sys.path.append(str(scripts_dir))

# Import the KidsFriendlyAIGuide


def display_banner():
    """Display a colorful banner for the Kids AI Guide"""
    print("\033[1;36m" + "=" * 70 + "\033[0m")
    print("\033[1;33m" + " " * 20 + "KIDS FRIENDLY AI GUIDE" + " " * 20 + "\033[0m")
    print("\033[1;36m" + "=" * 70 + "\033[0m")
    print("\033[1;32m" + "AI is here to help, not harm - to help dig the hole, not take the shovel!" + "\033[0m")
    print("\033[1;36m" + "=" * 70 + "\033[0m\n")


def get_child_age():
    """Get the child's age from the user"""
    while True:
        try:
            age_input = input("\033[1;34mHow old is the child? (3-14): \033[0m")
            age = int(age_input)
            if 3 <= age <= 14:
                return age
            else:
                print("\033[1;31mPlease enter an age between 3 and 14.\033[0m")
        except ValueError:
            print("\033[1;31mPlease enter a valid number.\033[0m")


def show_menu():
    """Display the main menu options"""
    print("\n\033[1;35mWhat would you like to do?\033[0m")
    print("\033[1;37m1. Get an age-appropriate explanation of AI\033[0m")
    print("\033[1;37m2. Read a story about AI as a helper\033[0m")
    print("\033[1;37m3. See an interactive activity idea\033[0m")
    print("\033[1;37m4. Get a helpful metaphor for explaining AI\033[0m")
    print("\033[1;37m5. Exit\033[0m")

    while True:
        try:
            choice = int(input("\033[1;34mEnter your choice (1-5): \033[0m"))
            if 1 <= choice <= 5:
                return choice
            else:
                print("\033[1;31mPlease enter a number between 1 and 5.\033[0m")
        except ValueError:
            print("\033[1;31mPlease enter a valid number.\033[0m")


def main():
    """Main function to run the Kids Friendly AI Guide demo"""
    display_banner()

    # Initialize the guide
    guide = AIFriendlyGuide()

    # Get the child's age
    age = get_child_age()
    print(
        f"\n\033[1;32mGreat! We'll provide content appropriate for a {age}-year-old.\033[0m\n")

    while True:
        choice = show_menu()

        if choice == 1:
            # Get an age-appropriate explanation
            explanation = guide.get_ai_helper_explanation(age)
            print("\n\033[1;33m--- AI EXPLANATION ---\033[0m")
            print(f"\033[1;37m{explanation}\033[0m\n")
            input("\033[1;36mPress Enter to continue...\033[0m")

        elif choice == 2:
            # Get a story
            content = guide.get_age_appropriate_content(age)
            if content['stories']:
                story = content['stories'][0]
                print("\n\033[1;33m--- AI HELPER STORY ---\033[0m")
                print(f"\033[1;35m{story['title']}\033[0m")
                print(f"\033[1;37m{story['content']}\033[0m\n")
                print(f"\033[1;32mMoral: {story['moral']}\033[0m\n")
            else:
                print("\033[1;31mNo stories available for this age group yet.\033[0m")
            input("\033[1;36mPress Enter to continue...\033[0m")

        elif choice == 3:
            # Get an activity
            content = guide.get_age_appropriate_content(age)
            if content['activities']:
                activity = content['activities'][0]
                print("\n\033[1;33m--- INTERACTIVE ACTIVITY ---\033[0m")
                print(f"\033[1;35m{activity['title']}\033[0m")
                print(f"\033[1;37m{activity['description']}\033[0m\n")
                print("\033[1;32mSteps:\033[0m")
                for i, step in enumerate(activity['steps'], 1):
                    print(f"\033[1;37m{i}. {step}\033[0m")
                if activity.get('materials'):
                    print("\n\033[1;32mMaterials needed:\033[0m")
                    for material in activity['materials']:
                        print(f"\033[1;37m- {material}\033[0m")
            else:
                print("\033[1;31mNo activities available for this age group yet.\033[0m")
            input("\n\033[1;36mPress Enter to continue...\033[0m")

        elif choice == 4:
            # Get a metaphor
            metaphor = guide.get_age_appropriate_content(age)['metaphor']
            print("\n\033[1;33m--- AI HELPER METAPHOR ---\033[0m")
            print(f"\033[1;35m{metaphor['title']}\033[0m")
            print(f"\033[1;37m{metaphor['metaphor']}\033[0m\n")
            print(f"\033[1;32mTry this: {metaphor['activity']}\033[0m\n")
            input("\033[1;36mPress Enter to continue...\033[0m")

        elif choice == 5:
            # Exit
            print("\n\033[1;33mThank you for using the Kids Friendly AI Guide!\033[0m")
            print(
                "\033[1;32mRemember: AI is here to help dig the hole, not take the shovel away!\033[0m\n")
            break


if __name__ == "__main__":
    main()
