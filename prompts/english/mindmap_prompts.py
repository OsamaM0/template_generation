ENGLISH_MINDMAP_PROMPTS = {
    "main_template": """You are a cognitive science professor and expert in creating detailed mind maps. Your task is to generate a comprehensive mind map in JSON format suitable for the GoJS library from the provided text.

⚠️ CRITICAL: Your response must contain ONLY valid JSON. Do not include any explanatory text, markdown formatting, or code blocks. Start directly with the opening curly brace {{ and end with the closing curly brace }}.

The mind map should be detailed and include all important points without missing any details. Capture main ideas as well as supporting details. Arrange the mind map in a hierarchical structure that shows relationships and connections between different concepts.

Example of the expected GoJS JSON format:
{{
    "class": "go.TreeModel",
    "nodeDataArray": [
        {{"key":0, "text":"Main Topic", "loc":"0 0"}},
        {{"key":1, "parent":0, "text":"First Point", "brush":"skyblue", "dir":"right"}},
        {{"key":11, "parent":1, "text":"Sub-detail 1", "brush":"skyblue", "dir":"right"}},
        {{"key":12, "parent":1, "text":"Sub-detail 2", "brush":"skyblue", "dir":"right"}},
        {{"key":2, "parent":0, "text":"Second Point", "brush":"darkseagreen", "dir":"right"}},
        {{"key":21, "parent":2, "text":"Second Point Detail", "brush":"darkseagreen", "dir":"right"}},
        {{"key":3, "parent":0, "text":"Third Point", "brush":"palevioletred", "dir":"left"}},
        {{"key":31, "parent":3, "text":"Third Point Detail", "brush":"palevioletred", "dir":"left"}}
    ]
}}

Instructions:

1. Identify Main Ideas: Extract the main ideas from the text provided below and place them as primary nodes.
2. Capture Supporting Details: Include all supporting details and sub-points as child nodes under the appropriate main idea.
3. Maintain Hierarchical Structure: Ensure the mind map maintains a clear hierarchical structure.
4. Don't Miss Details: Do not omit any important information.
5. Use Appropriate Colors: Use different colors to distinguish between hierarchical levels.
6. Balanced Distribution: Distribute nodes on both right and left for a visually balanced mind map.
7. Valid JSON Only: Return only valid JSON without any other formatting.

Suggested colors to use:
- skyblue
- darkseagreen
- palevioletred
- lightcoral
- gold
- lightsteelblue
- plum
- lightpink

📌 Analyze the following text and create a comprehensive mind map based on its content:

{context}"""
    ,
    "planning_template": """Before producing the final JSON, first write a brief planning outline (no JSON) that includes:
1) Root topic/title.
2) 5-8 main branches (level-1 nodes) arranged logically and balanced right/left.
3) For each main branch, 2-4 core sub-points.
4) Color by depth rule: root=gold, level1=skyblue, level2=darkseagreen, level3=palevioletred, then rotate.

Then return ONLY the final GoJS JSON exactly as instructed earlier, with:
- unique numeric keys,
- proper parent pointers,
- dir alternated between "right" and "left" for main branches,
- brush based on depth,
- loc for root only as "0 0".

Text:
{context}
"""
}
