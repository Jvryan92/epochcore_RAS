```
╔═════════════════════════════════════════════════════╗
║  ███████╗████████╗██████╗  █████╗ ████████╗███████╗ ║
║  ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝██╔════╝ ║
║  ███████╗   ██║   ██████╔╝███████║   ██║   █████╗   ║
║  ╚════██║   ██║   ██╔══██╗██╔══██║   ██║   ██╔══╝   ║
║  ███████║   ██║   ██║  ██║██║  ██║   ██║   ███████╗ ║
║  ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ║
║                                                     ║
║  ██████╗ ███████╗ ██████╗██╗  ██╗                   ║
║  ██╔══██╗██╔════╝██╔════╝██║ ██╔╝                   ║
║  ██║  ██║█████╗  ██║     █████╔╝                    ║
║  ██║  ██║██╔══╝  ██║     ██╔═██╗                    ║
║  ██████╔╝███████╗╚██████╗██║  ██╗                   ║
║  ╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝                   ║
╚═════════════════════════════════════════════════════╝

# StrategyDECK Collaboration Thread Integration

## AGENT THREAD RESOURCE

I've integrated the StrategyDECK icon system into our collaboration thread. This system provides visual assets for our collaborative workflows and decision processes.

### Quick Integration for Thread Participants

Copy and paste this code to use StrategyDECK icons in your thread responses:

```python
from scripts.generate_icons import get_thread_icon

# Get an appropriate icon for the current context
icon_path = get_thread_icon(
    thread_id="collaboration-thread-1",
    context="decision",  # Options: decision, analysis, synthesis, proposal
    mode="light",        # Options: light, dark
    size=32              # Options: 16, 32, 48
)

# Include the icon in your response
response = f"""
<img src="{icon_path}" alt="Decision Icon" width="32" height="32" />

## Decision Point
Based on our collaborative analysis, I recommend proceeding with Option B.
"""
```

### Available Icon Contexts

Each context has a specific icon design to help visually distinguish different types of contributions:

1. **Decision** - Use when proposing or making a decision
2. **Analysis** - Use when breaking down information
3. **Synthesis** - Use when combining multiple perspectives
4. **Proposal** - Use when suggesting new ideas
5. **Question** - Use when seeking clarification
6. **Agreement** - Use when confirming consensus
7. **Divergence** - Use when presenting alternative views

### Thread-Specific Icon Set

For this collaboration thread, we've created a custom icon set with:
- Brand-aligned color schemes
- Consistent visual language
- Semantic color coding (green for agreement, yellow for proposals, etc.)
- Accessible designs that work in both light and dark modes

### Integration with Thread Tools

The icons integrate seamlessly with our thread tools:

```python
from thread_tools import CollaborationCanvas
from scripts.generate_icons import get_icon_set

# Create a visual collaboration canvas
canvas = CollaborationCanvas(
    title="Project Planning Session",
    icon_set=get_icon_set(
        context="collaboration",
        style="flat",
        include_states=True
    )
)

# Add contributions to the canvas with appropriate icons
canvas.add_contribution(
    author="@analyst_1",
    content="We should prioritize the north region first",
    contribution_type="proposal"  # Will automatically use proposal icon
)

# Generate the visual map for the thread
canvas_image = canvas.render()
```

### Thread Status Indication

Icons are also available to indicate thread status:
- 🟢 Active thread (accepting contributions)
- 🟡 Review phase (synthesizing inputs)
- 🔴 Decision phase (finalizing conclusions)
- ✅ Completed (implementation phase)

Let me know if you need help integrating these icons into your thread responses!
```
