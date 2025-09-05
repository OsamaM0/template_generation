# Template Generation System

A modular system for generating educational content templates including question banks, worksheets, and summaries with **enhanced goal-based question generation**.

## Features

- **Multi-language Support**: Arabic and English
- **Modular Templates**: Question Bank, Worksheet, Summary, Mind Map
- **🎯 Goal-Based Question Generation**: NEW! Generate questions specifically aligned with learning objectives
- **🧠 Mind Map Generation**: NEW! Create detailed mind maps compatible with GoJS visualization
- **Configurable Question Types**: Multiple choice, short answer, complete, true/false
- **Difficulty Levels**: 3 configurable difficulty levels
- **Content-based Generation**: Analyzes input content and goals
- **Two Generation Modes**:
  - **Goals Provided**: Generate questions for specific learning goals
  - **Goals Auto-Generated**: Create goals from content, then generate questions

### New: Multi-pass Mind Map Generation

For long content, the mind map generator can now split the text into overlapping chunks, generate partial mind maps per chunk, and merge them into one comprehensive map. This improves coverage while staying under model context limits.

Control via environment variables:

- MINDMAP_MULTI_PASS=true | false (default: true)
- MINDMAP_CHUNK_SIZE_CHARS=1800 (characters per chunk)
- MINDMAP_CHUNK_OVERLAP_CHARS=250 (overlap between chunks)
- MINDMAP_DEDUPLICATE_NODES=true | false (deduplicate nodes by normalized text under the same parent)

Notes:
- A synthetic root node labeled "Comprehensive Mind Map" (or Arabic equivalent) will appear when merging multiple chunks to keep a single-tree structure.
- Colors and left/right balancing are preserved in post-processing. The total nodes are capped by MINDMAP_MAX_NODES.

## 🚀 New Goal-Based Functionality

### Scenario 1: Goals Provided with Content

When you provide specific learning goals, the system generates questions specifically targeting each goal:

```python
from generators.template_generator import TemplateGenerator

generator = TemplateGenerator()

# Your content and goals
content = "Mathematical content about triangles and geometry..."
goals = [
    "Students understand basic geometry concepts",
    "Students distinguish between triangle types", 
    "Students apply Pythagorean theorem"
]

# Generate goal-based questions
result = generator.generate_goal_based_questions(
    content=content,
    goals=goals,
    question_counts={
        "multiple_choice": 6,
        "short_answer": 4,
        "complete": 2,
        "true_false": 2
    }
)

# Each question is linked to specific goals
print(f"Generated {len(result['learning_goals'])} goals")
print(f"Total questions: {result['_goal_based_metadata']['total_questions']}")

# Access goal-question mapping
for mapping in result['goal_question_mapping']:
    print(f"Goal: {mapping['goal_text']}")
    print(f"Questions: {mapping['question_count']}")
```

### Scenario 2: No Goals Provided (Auto-Generation)

When you don't provide goals, the system first analyzes content to generate appropriate goals, then creates questions:

```python
# Just provide content - no goals
result = generator.generate_goal_based_questions(
    content="Physics content about motion and force...",
    goals=None  # System will generate goals automatically
)

# System generates goals from content analysis
generated_goals = result['learning_goals']
print(f"System generated {len(generated_goals)} goals:")
for goal in generated_goals:
    print(f"• {goal['text']}")
```

## 📊 Enhanced Output Structure

The goal-based generation provides rich output with clear goal-question relationships:

```json
{
  "learning_goals": [
    {
      "id": "goal_1",
      "text": "Students understand basic concepts",
      "priority": 1,
      "cognitive_level": "understand"
    }
  ],
  "goal_question_mapping": [
    {
      "goal_id": "goal_1", 
      "goal_text": "Students understand basic concepts",
      "question_count": 4,
      "question_types": {
        "multiple_choice": 2,
        "short_answer": 1,
        "complete": 1,
        "true_false": 0
      }
    }
  ],
  "questions_by_goal": {
    "goal_1": {
      "multiple_choice": [...],
      "short_answer": [...],
      "complete": [...]
    }
  },
  "multiple_choice": [...], // All questions (traditional structure)
  "short_answer": [...],
  "_goal_based_metadata": {
    "total_goals": 3,
    "total_questions": 14,
    "scenario": "goals_provided"
  }
}
```

## Usage Examples

### Traditional Generation (Backward Compatible)

```python
from generators.template_generator import TemplateGenerator

generator = TemplateGenerator()

# Generate question bank (traditional way)
questions = generator.generate_template(
    template_type="questions",
    content="your educational content here",
    goals=["Students learn addition", "Students understand basic math"],
    question_counts={
        "multiple_choice": 5,
        "short_answer": 3,
        "complete": 2,
        "true_false": 4
    },
    difficulty_levels=[1, 2, 3]
)

# Generate worksheet
worksheet = generator.generate_template(
    template_type="worksheet",
    content="your content here",
    goals=["goal1", "goal2"]
)

# Generate summary
summary = generator.generate_template(
    template_type="summary",
    content="your content here"
)

# Generate mind map
mindmap = generator.generate_template(
    template_type="mindmap",
    content="your content here"
)
```

### Goal-Based Generation (New)

```python
# Method 1: Using the main generator
result = generator.generate_goal_based_questions(
    content="your content",
    goals=["goal1", "goal2"]  # Optional
)

# Method 2: Using template type
result = generator.generate_template(
    template_type="goal_based_questions",
    content="your content",
    goals=["goal1", "goal2"]  # Optional
)
```

### Mind Map Generation (New)

```python
# Generate mind map compatible with GoJS
mindmap = generator.generate_mindmap(content="your content")

# Or using template type
mindmap = generator.generate_template(
    template_type="mindmap",
    content="your content"
)

# The result is a JSON structure ready for GoJS:
# {
#   "class": "go.TreeModel",
#   "nodeDataArray": [
#     {"key": 0, "text": "Main Topic", "loc": "0 0"},
#     {"key": 1, "parent": 0, "text": "Subtopic 1", "brush": "skyblue", "dir": "right"},
#     ...
#   ]
# }
```

## Command Line Usage

### Traditional Templates
```bash
# Generate questions with goals
python main.py questions content.txt --goals "Goal 1" "Goal 2" --mc 5 --sa 3

# Generate worksheet
python main.py worksheet content.txt --goals "Goal 1" "Goal 2"

# Generate mind map
python main.py mindmap content.txt
```

### Goal-Based Generation
```bash
# With provided goals
python main.py goal_based_questions content.txt --goals "Goal 1" "Goal 2" --mc 6 --sa 4

# Without goals (auto-generate)
python main.py goal_based_questions content.txt --mc 6 --sa 4
```

## Demo Scripts

### Run Goal-Based Demo
```bash
# Run both scenarios
python goal_based_demo.py

# Run specific scenario
python goal_based_demo.py scenario1  # Goals provided
python goal_based_demo.py scenario2  # Goals auto-generated
```

### Run Usage Examples
```bash
python usage_examples.py
```

## Setup

1. Install requirements: `pip install -r requirements.txt`
2. Set your OpenAI API key in environment variables or .env file:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
3. Run demos: `python goal_based_demo.py`
4. Or run main script: `python main.py goal_based_questions sample_content.txt`

## Key Benefits of Goal-Based Generation

1. **🎯 Targeted Assessment**: Each question specifically targets a learning objective
2. **📊 Clear Mapping**: Know exactly which questions assess which goals
3. **🔄 Flexible Workflows**: Works with or without predefined goals
4. **📈 Better Analytics**: Track goal achievement through question performance
5. **🎨 Adaptive Content**: System can generate appropriate goals from content analysis
6. **🔗 Cognitive Alignment**: Questions are aligned with appropriate cognitive levels (Bloom's taxonomy)

## Migration Guide

The new functionality is **fully backward compatible**. Your existing code will continue to work unchanged. To adopt goal-based generation:

1. **Replace** `template_type="questions"` with `template_type="goal_based_questions"`
2. **Or use** the new convenience method: `generate_goal_based_questions()`
3. **Optional**: Remove goals parameter to let system auto-generate them
4. **Access** the enhanced output structure for goal-question relationships
