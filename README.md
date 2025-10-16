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

### New: Smart Mind Map Generation Workflow

**Two-Phase Approach for Better Quality:**

1. **AI Generation Phase**: The AI focuses on content and structure, generating only:
   - `key`: Unique identifier
   - `parent`: Parent relationship
   - `text`: Node content
   - `loc`: Location (root only)

2. **System Enhancement Phase**: Automatic intelligent assignment of:
   - `brush`: Colors based on node depth (gold → skyblue → darkseagreen → palevioletred...)
   - `dir`: Balanced left/right distribution with direction propagation

**Benefits:**
- ✅ Higher quality content structure (AI focuses on what it does best)
- ✅ Consistent visual styling across all mind maps
- ✅ Faster generation and lower token usage
- ✅ Balanced and professional appearance

See docs/MINDMAP_SMART_WORKFLOW.md for detailed documentation and docs/ARCHITECTURE.md for the full system architecture.

### Multi-pass Mind Map Generation

For long content, the mind map generator can split text into overlapping chunks, generate partial mind maps per chunk, and merge them into one comprehensive map.

Control via environment variables:

- MINDMAP_MULTI_PASS=true | false (default: true)
- MINDMAP_CHUNK_SIZE_CHARS=1800 (characters per chunk)
- MINDMAP_CHUNK_OVERLAP_CHARS=250 (overlap between chunks)
- MINDMAP_DEDUPLICATE_NODES=true | false (deduplicate nodes by normalized text under the same parent)
- MINDMAP_MAX_NODES=120 (maximum nodes in final output)
- MINDMAP_COLORS=[...] (color array for depth-based coloring)

Notes:
- A synthetic root node labeled "Comprehensive Mind Map" (or Arabic equivalent) will appear when merging multiple chunks.
- Colors and left/right balancing are automatically applied in post-processing.

### Mind Map Professional Mode (Concise Depth-Limited)

New environment variables to control conciseness and relevance:

| Variable | Default | Description |
|----------|---------|-------------|
| `MINDMAP_MAX_DEPTH` | 3 | Maximum depth (root=0). 3 = root + level-1 + level-2. Deeper nodes are pruned. |
| `MINDMAP_EXCLUDE_EXAMPLES` | true | When true, nodes detected as examples / stories / scenarios (multi-lingual keywords) are removed. |

Prompt instructions (Arabic & English) were updated to:
- Focus strictly on concepts directly tied to the lesson title
- Avoid narrative examples, stories, case studies, filler
- Limit node text to short noun phrases (≈ ≤6 words)
- Keep balanced 4–7 main branches when possible

Post-processing automatically:
1. Prunes nodes deeper than `MINDMAP_MAX_DEPTH`
2. Filters nodes containing example/story keywords (Arabic & English)
3. Recomputes depth and assigns standardized colors & directions

This yields cleaner, professional classroom-ready mind maps without tangential detail.

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

## Mind Map Reprocessing (Existing Database)

If you already have mind maps stored in MongoDB (collection `ai.mindmaps`) that were generated before the enhanced post-processing (balanced `dir`, depth pruning, color assignment), you can retrofit them **without re-generating via the LLM**.

### What It Does
The script `reprocess_mindmaps.py`:
- Loads each existing record
- Extracts only: `key`, `text`, `parent` from each node
- Recomputes: `brush` (color by depth), `dir` (balanced left/right), root `loc` (if missing)
- Applies depth limit + example filtering (based on current `Settings`)
- Prunes disallowed nodes (depth > `MINDMAP_MAX_DEPTH`, example/story nodes if enabled)
- Updates document with:
  - `mindmap.nodeDataArray` (with new visual fields)
  - `metadata.reprocessed_at`
  - `metadata.reprocess_runs` (incremented)
  - `metadata.reprocess_changes` (summary counts)

It never changes original `key`, `text`, `parent` ordering except when pruning is required by config.

### Dry Run First (Recommended)
Dry run prints a summary but does NOT modify the database:

```bash
python reprocess_mindmaps.py --limit 10
```

Example output line:
```
[3] filename=lesson_12.txt doc_uuid=123e... changes={'before_nodes': 58, 'after_nodes': 52, 'dir_assigned': 51, 'brush_assigned': 52, 'root_loc': '0 0'}
```

### Apply Changes
```bash
python reprocess_mindmaps.py --apply
```

### Filtering Options
```bash
python reprocess_mindmaps.py --apply --filename chemistry
python reprocess_mindmaps.py --apply --custom-id 652fa1c4b3...
python reprocess_mindmaps.py --apply --contains-text الطاقة
python reprocess_mindmaps.py --apply --limit 25 --contains-text geometry
```

Flags:
- `--limit N`          Process only first N matched documents
- `--filename SUBSTR`  Case-insensitive substring match on stored filename
- `--custom-id ID`     Exact match on `custom_id`
- `--contains-text T`  Any node whose text contains substring T (case-insensitive)
- `--apply`            Persist changes (omit for dry run)

### Idempotency
Running multiple times is safe— it recomputes visual fields deterministically from the preserved structure. Pruning decisions remain consistent as long as `Settings` values (depth, exclusion flags) don’t change.

### Configuration Sensitivity
The script relies on current environment / `Settings` values:
- `MINDMAP_MAX_DEPTH`
- `MINDMAP_EXCLUDE_EXAMPLES`
- `MINDMAP_MAX_NODES`
- `MINDMAP_COLORS`

Adjust them before running if you want different pruning or color palette.

### Metadata Audit
Each updated record gains:
```json
"metadata": {
  ...,
  "reprocessed_at": "2025-10-05T12:34:56Z",
  "reprocess_runs": 2,
  "reprocess_changes": {
    "before_nodes": 58,
    "after_nodes": 52,
    "dir_assigned": 51,
    "brush_assigned": 52,
    "root_loc": "0 0"
  }
}
```

This enables tracking improvements without losing provenance.

