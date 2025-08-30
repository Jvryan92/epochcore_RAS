#!/usr/bin/env python3
"""
Kids Friendly AI Guide - EpochCore RAS

This module provides child-friendly explanations and interactive experiences
to help kids understand that AI is a helpful tool designed to assist people,
not replace or harm them. Using storytelling, simple explanations, and 
interactive examples, it teaches the collaborative nature of AI.
"""

import json
import logging
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("KidsFriendlyAIGuide")

# Constants
RESOURCES_DIR = Path(__file__).resolve().parent.parent / \
    "thread_resources" / "kids_ai_guide"
STORIES_DIR = RESOURCES_DIR / "stories"
ACTIVITIES_DIR = RESOURCES_DIR / "activities"
ILLUSTRATIONS_DIR = RESOURCES_DIR / "illustrations"

# Ensure directories exist
RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
STORIES_DIR.mkdir(exist_ok=True)
ACTIVITIES_DIR.mkdir(exist_ok=True)
ILLUSTRATIONS_DIR.mkdir(exist_ok=True)


class KidsFriendlyMetaphor:
    """Collection of kid-friendly metaphors to explain AI concepts"""

    HELPER_METAPHORS = [
        {
            "title": "AI is like a Friendly Helper Robot",
            "metaphor": "AI is like a friendly robot that helps you build with blocks. "
                        "It doesn't take your blocks away - it hands you the ones you need "
                        "and suggests cool ways to build your tower!",
            "activity": "Let's build something together! I'll suggest pieces, but you decide where they go."
        },
        {
            "title": "AI is like a Magical Library Assistant",
            "metaphor": "AI is like a helpful library assistant who knows where all the books are. "
                        "They don't read the books for you - they help you find the perfect story "
                        "and let you enjoy reading it yourself!",
            "activity": "Tell me what kind of story you like, and I'll help you find one!"
        },
        {
            "title": "AI is like a Gardening Buddy",
            "metaphor": "AI is like a gardening buddy who helps you dig the holes for your seeds. "
                        "They don't take your shovel away - they help you dig and water so your "
                        "plants can grow big and strong!",
            "activity": "Let's design a garden together! You pick the plants, and I'll help figure out where to put them."
        },
        {
            "title": "AI is like a Cooking Helper",
            "metaphor": "AI is like a cooking helper in the kitchen. They don't eat your cookies - "
                        "they help measure ingredients and set timers so your treats turn out yummy!",
            "activity": "Let's make a pretend recipe together! You pick the ingredients, and I'll help mix them."
        },
        {
            "title": "AI is like a Map Guide",
            "metaphor": "AI is like a friendly guide with a map. They don't decide where you go - "
                        "they help you find the best way to get to the playground or anywhere you want to explore!",
            "activity": "Let's go on an imaginary adventure! You pick where we go, and I'll help find the way."
        }
    ]

    @classmethod
    def get_random_metaphor(cls) -> Dict[str, str]:
        """Get a random metaphor from the collection"""
        return random.choice(cls.HELPER_METAPHORS)

    @classmethod
    def get_all_metaphors(cls) -> List[Dict[str, str]]:
        """Get all metaphors"""
        return cls.HELPER_METAPHORS


class AIExplanationLevel:
    """Different levels of explanation based on age/understanding"""
    PRESCHOOL = "preschool"  # Ages 3-5
    EARLY_ELEMENTARY = "early_elementary"  # Ages 6-8
    LATE_ELEMENTARY = "late_elementary"  # Ages 9-11
    MIDDLE_SCHOOL = "middle_school"  # Ages 12-14


class AIHelperStory:
    """Stories that illustrate AI as a helper through narratives"""

    def __init__(self, title: str, age_level: str, content: str, moral: str):
        self.title = title
        self.age_level = age_level
        self.content = content
        self.moral = moral

    def to_dict(self) -> Dict[str, str]:
        """Convert story to dictionary"""
        return {
            "title": self.title,
            "age_level": self.age_level,
            "content": self.content,
            "moral": self.moral
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'AIHelperStory':
        """Create story from dictionary"""
        return cls(
            title=data["title"],
            age_level=data["age_level"],
            content=data["content"],
            moral=data["moral"]
        )

    @classmethod
    def get_sample_stories(cls) -> List['AIHelperStory']:
        """Get sample stories for different age levels"""
        return [
            cls(
                title="Robo and the Sand Castle",
                age_level=AIExplanationLevel.PRESCHOOL,
                content=(
                    "Mia was at the beach trying to build a sand castle. Her friend Robo the Robot "
                    "came to play. 'Can I help?' asked Robo. 'Yes please!' said Mia. Robo helped "
                    "carry water and smooth the sand. Mia built the towers and windows. Together "
                    "they made the biggest, best sand castle on the beach!"
                ),
                moral="AI like Robo helps us do things better and faster, but we're still the ones creating and deciding what to build."
            ),
            cls(
                title="The Homework Helper",
                age_level=AIExplanationLevel.EARLY_ELEMENTARY,
                content=(
                    "Sam had a big math homework assignment. His digital assistant Ada offered to help. "
                    "'I can show you how to solve these problems,' Ada said. Ada didn't just give Sam "
                    "the answers - that wouldn't help him learn! Instead, Ada showed examples and gave "
                    "hints when Sam got stuck. By working together, Sam finished his homework and "
                    "understood the math much better!"
                ),
                moral="AI can teach us and give us tips, but we still need to do the learning ourselves."
            ),
            cls(
                title="The Garden Grows",
                age_level=AIExplanationLevel.LATE_ELEMENTARY,
                content=(
                    "Li wanted to grow vegetables in the backyard. Their family's garden assistant bot, Terra, "
                    "helped analyze the soil and suggested which vegetables would grow best. Terra reminded Li "
                    "when to water the plants and pointed out when bugs appeared. But Li did the planting, "
                    "watering, and picking. When the vegetables were ready, everyone thanked Li for the "
                    "delicious food. 'Terra helped,' Li said, 'but growing the garden was still my job!'"
                ),
                moral="AI can give us information and reminders, but the important work still depends on us humans."
            ),
            cls(
                title="The Bicycle Design Team",
                age_level=AIExplanationLevel.MIDDLE_SCHOOL,
                content=(
                    "Jordan's school had a project to design a better bicycle. Jordan worked with an AI design "
                    "program called Blueprint. Jordan told Blueprint about their ideas for a safer bike for kids. "
                    "Blueprint suggested materials and showed simulations of different designs. But Jordan made "
                    "all the final decisions about how the bike should look and work. When Jordan presented the "
                    "design, the teacher asked, 'Did you do this yourself?' Jordan replied, 'I used an AI program "
                    "as my assistant, but the ideas and decisions were all mine. The AI was like having another "
                    "tool in my toolbox - it helped me create my vision, but didn't create for me.'"
                ),
                moral="AI is a powerful tool that can help us create, but humans provide the vision, purpose, and make the important decisions."
            )
        ]


class InteractiveActivity:
    """Interactive activities that demonstrate collaborative AI-human partnership"""

    def __init__(self, title: str, age_level: str, description: str, steps: List[str], materials: List[str] = None):
        self.title = title
        self.age_level = age_level
        self.description = description
        self.steps = steps
        self.materials = materials or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert activity to dictionary"""
        return {
            "title": self.title,
            "age_level": self.age_level,
            "description": self.description,
            "steps": self.steps,
            "materials": self.materials
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InteractiveActivity':
        """Create activity from dictionary"""
        return cls(
            title=data["title"],
            age_level=data["age_level"],
            description=data["description"],
            steps=data["steps"],
            materials=data.get("materials", [])
        )

    @classmethod
    def get_sample_activities(cls) -> List['InteractiveActivity']:
        """Get sample interactive activities"""
        return [
            cls(
                title="AI Drawing Helper",
                age_level=AIExplanationLevel.PRESCHOOL,
                description="Draw a picture together with an AI helper to see how you can create art together!",
                steps=[
                    "Get a large piece of paper and some crayons or markers",
                    "The child starts by drawing one part of a picture (like the head of an animal)",
                    "The AI (played by a parent or the app) suggests what to draw next (like adding a body)",
                    "The child decides whether to follow the suggestion or draw something else",
                    "Take turns adding to the drawing",
                    "At the end, discuss how the AI helped with ideas but the child made the decisions"
                ],
                materials=["Paper", "Crayons or markers"]
            ),
            cls(
                title="Recipe Assistant Game",
                age_level=AIExplanationLevel.EARLY_ELEMENTARY,
                description="Make a pretend meal with the help of an AI cooking assistant!",
                steps=[
                    "Set up a pretend kitchen area",
                    "The child decides what meal they want to make",
                    "The AI assistant (played by a parent or the app) suggests ingredients",
                    "The child picks which ingredients to use",
                    "The AI can suggest cooking steps, but the child is the 'chef' who makes all decisions",
                    "Discuss how the AI helped with information but the child was in charge"
                ],
                materials=["Pretend food items", "Toy cooking tools"]
            ),
            cls(
                title="Treasure Hunt Helper",
                age_level=AIExplanationLevel.LATE_ELEMENTARY,
                description="Go on a treasure hunt where an AI gives hints but you make the decisions!",
                steps=[
                    "Hide a small prize or 'treasure' somewhere in your home or yard",
                    "The AI (played by a parent or the app) provides clues when asked",
                    "The child decides where to look and can ask for hints",
                    "The AI can say 'warmer' or 'colder' but doesn't directly tell the location",
                    "After finding the treasure, discuss how the AI provided helpful information, but the child did the actual searching and decision-making"
                ]
            ),
            cls(
                title="AI City Planner",
                age_level=AIExplanationLevel.MIDDLE_SCHOOL,
                description="Design a city with the help of an AI assistant who provides information and suggestions!",
                steps=[
                    "Get a large piece of paper, markers, and small objects to represent buildings",
                    "The child decides what kind of city they want to create",
                    "The AI (played by a parent or the app) suggests considerations like 'where will people get food?' or 'how will people travel?'",
                    "The child designs the city layout, deciding where to put homes, schools, parks, etc.",
                    "The AI can offer information about real city planning but doesn't make decisions",
                    "Discuss how the AI provided expertise but the child was the actual city planner making the important decisions"
                ],
                materials=["Large paper", "Markers",
                           "Small objects for buildings", "Optional: craft supplies"]
            )
        ]


class AIFriendlyGuide:
    """Main class for interacting with the Kids Friendly AI Guide"""

    def __init__(self):
        self.stories = self._load_stories()
        self.activities = self._load_activities()

    def _load_stories(self) -> List[AIHelperStory]:
        """Load stories from files or use samples"""
        sample_stories = AIHelperStory.get_sample_stories()

        try:
            stories_file = STORIES_DIR / "stories.json"
            if stories_file.exists():
                with open(stories_file, "r", encoding="utf-8") as f:
                    stories_data = json.load(f)
                return [AIHelperStory.from_dict(story_data) for story_data in stories_data]
            else:
                # Save sample stories
                self._save_stories(sample_stories)
                return sample_stories
        except Exception as e:
            logger.warning(f"Could not load stories: {e}")
            return sample_stories

    def _save_stories(self, stories: List[AIHelperStory]):
        """Save stories to file"""
        try:
            stories_file = STORIES_DIR / "stories.json"
            with open(stories_file, "w", encoding="utf-8") as f:
                json.dump([story.to_dict() for story in stories], f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save stories: {e}")

    def _load_activities(self) -> List[InteractiveActivity]:
        """Load activities from files or use samples"""
        sample_activities = InteractiveActivity.get_sample_activities()

        try:
            activities_file = ACTIVITIES_DIR / "activities.json"
            if activities_file.exists():
                with open(activities_file, "r", encoding="utf-8") as f:
                    activities_data = json.load(f)
                return [InteractiveActivity.from_dict(activity_data) for activity_data in activities_data]
            else:
                # Save sample activities
                self._save_activities(sample_activities)
                return sample_activities
        except Exception as e:
            logger.warning(f"Could not load activities: {e}")
            return sample_activities

    def _save_activities(self, activities: List[InteractiveActivity]):
        """Save activities to file"""
        try:
            activities_file = ACTIVITIES_DIR / "activities.json"
            with open(activities_file, "w", encoding="utf-8") as f:
                json.dump([activity.to_dict() for activity in activities], f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save activities: {e}")

    def get_age_appropriate_content(self, age: int) -> Dict[str, Any]:
        """Get age-appropriate content for a given age"""
        if age <= 5:
            level = AIExplanationLevel.PRESCHOOL
        elif age <= 8:
            level = AIExplanationLevel.EARLY_ELEMENTARY
        elif age <= 11:
            level = AIExplanationLevel.LATE_ELEMENTARY
        else:
            level = AIExplanationLevel.MIDDLE_SCHOOL

        # Find appropriate stories and activities
        stories = [story for story in self.stories if story.age_level == level]
        activities = [
            activity for activity in self.activities if activity.age_level == level]

        # Get a random metaphor
        metaphor = KidsFriendlyMetaphor.get_random_metaphor()

        return {
            "age_level": level,
            "metaphor": metaphor,
            "stories": [story.to_dict() for story in stories],
            "activities": [activity.to_dict() for activity in activities]
        }

    def get_ai_helper_explanation(self, age: int) -> str:
        """Get an age-appropriate explanation of AI as a helper"""
        if age <= 5:
            return (
                "AI is like a friendly helper robot! It helps you find things, learn new stuff, "
                "and create cool pictures. But you're still the boss - you make the important decisions. "
                "AI is here to help, not take over. Just like a friend who helps you dig in the sandbox "
                "but doesn't take your shovel away!"
            )
        elif age <= 8:
            return (
                "AI is a computer program that can learn and help people. Think of AI like a really smart "
                "assistant who can help you with homework, answer questions, or suggest games to play. "
                "AI doesn't take over your job or make decisions for you - it just gives you information "
                "and suggestions. You're still in charge! It's like having a helper who can hold the ladder "
                "while you climb the tree, but YOU decide which tree to climb and how high to go."
            )
        elif age <= 11:
            return (
                "Artificial Intelligence (AI) is technology that helps computers learn from information "
                "and solve problems. AI is designed to be a tool that assists humans, not replace them. "
                "Think of it like this: if you're building something, AI can hand you the right tools and "
                "suggest ways to build it better, but YOU are still the builder making the important decisions. "
                "AI helps doctors find diseases, helps scientists discover new things, and can even help you "
                "with your homework - but in each case, humans are still the ones in charge. AI is here to "
                "help dig the hole, not take your shovel away!"
            )
        else:
            return (
                "Artificial Intelligence (AI) refers to computer systems designed to perform tasks that would "
                "typically require human intelligence. These systems learn from data to recognize patterns and "
                "make predictions or recommendations. It's important to understand that AI is created to be a "
                "collaborative tool that enhances human capabilities, not replace them. \n\n"
                "For example, AI can help doctors analyze medical images to spot potential issues, but doctors "
                "make the final diagnosis and treatment decisions. AI can suggest math problem-solving strategies, "
                "but you develop the critical thinking skills by working through problems. AI can generate creative "
                "ideas for writing or art, but human creativity and judgment determine which ideas have real value. \n\n"
                "Think of AI as a powerful assistant that's there to help you accomplish more - it's designed to "
                "help dig the hole, not take the shovel away from you. Humans still provide the direction, purpose, "
                "creativity, and ethical judgment that give our work meaning."
            )

    def get_interactive_dialogue(self, age: int) -> List[Dict[str, str]]:
        """Get an interactive dialogue explaining AI as a helper"""
        if age <= 5:
            return [
                {"speaker": "Child", "text": "What is AI?"},
                {"speaker": "Guide", "text": "AI is like a friendly helper robot! It can help you find things and make cool pictures."},
                {"speaker": "Child", "text": "Will the robot take my toys?"},
                {"speaker": "Guide", "text": "No! AI helpers don't take your toys. They help you find new ways to play with them!"},
                {"speaker": "Child", "text": "Can the robot draw for me?"},
                {"speaker": "Guide", "text": "AI can help you draw, but YOU get to decide what to draw and what colors to use. It's like having a friend who suggests ideas, but you're the artist!"},
                {"speaker": "Child", "text": "Will the robot do my chores?"},
                {"speaker": "Guide", "text": "AI can help remind you about chores and make them more fun, but you still get to do them. Just like a friend who helps clean up but doesn't take your broom away!"}
            ]
        elif age <= 8:
            return [
                {"speaker": "Child", "text": "What exactly is AI?"},
                {"speaker": "Guide", "text": "AI stands for Artificial Intelligence. It's like a computer brain that can learn things and help people."},
                {"speaker": "Child", "text": "Is AI going to take over my video games?"},
                {"speaker": "Guide", "text": "Not at all! AI might be IN your video games to make them fun, but YOU still control the game controller. AI is there to make the game more exciting for you!"},
                {"speaker": "Child", "text": "Can AI do my homework for me?"},
                {"speaker": "Guide", "text": "AI can help explain things you don't understand and give you practice problems, but it won't do your homework for you. That would be like someone else learning to ride your bike - you wouldn't get better at riding!"},
                {"speaker": "Child", "text": "What if the AI gets smarter than people?"},
                {"speaker": "Guide", "text": "AI is built by people to solve specific problems. It might be really good at math or finding patterns, but it doesn't have feelings or imagination like you do. People create AI to be helpful, not to take over. It's here to help dig the hole, not take your shovel away!"}
            ]
        else:
            return [
                {"speaker": "Student", "text": "What exactly is artificial intelligence?"},
                {"speaker": "Guide", "text": "Artificial Intelligence, or AI, refers to computer systems designed to perform tasks that would typically require human intelligence. These systems learn from data to recognize patterns and make predictions or recommendations."},
                {"speaker": "Student",
                    "text": "Are AI systems going to replace humans for most jobs?"},
                {"speaker": "Guide", "text": "AI is designed to augment human capabilities, not replace them entirely. While AI may automate certain repetitive tasks, it creates new opportunities and jobs. The most effective approach is human-AI collaboration, where AI handles routine tasks while humans provide creativity, ethical judgment, and interpersonal skills."},
                {"speaker": "Student", "text": "Can AI make decisions on its own?"},
                {"speaker": "Guide", "text": "AI can make recommendations based on patterns it identifies in data, but humans set the objectives, provide the data, and decide how to use AI's output. AI doesn't have consciousness or independent goals - it's a tool created to help humans achieve their objectives."},
                {"speaker": "Student", "text": "So is AI dangerous?"},
                {"speaker": "Guide", "text": "Like any powerful technology, AI requires responsible development and use. The real focus should be on how humans design, deploy, and regulate AI systems. When developed ethically with proper oversight, AI is designed to be helpful, not harmful. Think of AI as being here to help dig the hole, not take your shovel away - it's a collaborative tool, not a replacement for human judgment."}
            ]


# Example usage
def main():
    """Example usage of the Kids Friendly AI Guide"""
    guide = AIFriendlyGuide()

    print("=" * 60)
    print("KIDS FRIENDLY AI GUIDE - EXAMPLE OUTPUTS")
    print("=" * 60)

    # Test explanations for different ages
    ages = [4, 7, 10, 13]
    for age in ages:
        print(f"\n\n{'-' * 40}")
        print(f"EXPLANATION FOR {age}-YEAR-OLD:")
        print(f"{'-' * 40}")
        print(guide.get_ai_helper_explanation(age))

    # Test getting age-appropriate content
    age = 5  # Test for a 5-year-old
    content = guide.get_age_appropriate_content(age)

    print(f"\n\n{'-' * 40}")
    print(f"AGE-APPROPRIATE CONTENT FOR {age}-YEAR-OLD:")
    print(f"{'-' * 40}")
    print(f"Age Level: {content['age_level']}")
    print(f"\nMetaphor: {content['metaphor']['title']}")
    print(content['metaphor']['metaphor'])

    print(f"\nStories available: {len(content['stories'])}")
    if content['stories']:
        sample_story = content['stories'][0]
        print(f"\nSample Story: {sample_story['title']}")
        print(sample_story['content'])
        print(f"\nMoral: {sample_story['moral']}")

    print(f"\nActivities available: {len(content['activities'])}")
    if content['activities']:
        sample_activity = content['activities'][0]
        print(f"\nSample Activity: {sample_activity['title']}")
        print(sample_activity['description'])
        print("\nSteps:")
        for i, step in enumerate(sample_activity['steps'], 1):
            print(f"{i}. {step}")

    print("\n" + "=" * 60)
    print("END OF EXAMPLE")
    print("=" * 60)


if __name__ == "__main__":
    main()
