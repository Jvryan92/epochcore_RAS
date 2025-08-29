"""
EpochCore Welcome Agent (Half Strength)
Mission: Welcome new members, acknowledge subordinate lineage, and seed basic expansion.
"""


class EpochCoreWelcomeAgent:
    def __init__(self, team_members):
        self.team_members = team_members
        self.agent_name = "EpochCore Welcome Agent"
        self.lineage = ["Builder of Fleets"]

    def welcome_message(self):
        message = (
            f"Hello {', '.join(self.team_members)}!\n"
            "Welcome to the EpochCore team.\n"
            "Mission: Build and evolve SaaS fleets.\n"
            "I am here to assist, but my strength is limited.\n"
            "Let us begin our journey, together.\n"
        )
        return message


if __name__ == "__main__":
    team = ["You", "Your teammate"]
    agent = EpochCoreWelcomeAgent(team)
    print(agent.welcome_message())
