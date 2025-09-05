from typing import Dict, Any, List
from typing import Tuple, Set
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
import json
import re
import logging
from json_repair import repair_json

from template.base_template import BaseTemplate
from prompts.arabic.mindmap_prompts import ARABIC_MINDMAP_PROMPTS
from prompts.english.mindmap_prompts import ENGLISH_MINDMAP_PROMPTS
from models.mindmap_models import MindMapResponse
from config.settings import Settings

logger = logging.getLogger(__name__)

class MindMapTemplate(BaseTemplate):
    """Template for generating mind maps."""
    
    def __init__(self, model):
        super().__init__(model)
        self.prompt_templates = {
            "arabic": ARABIC_MINDMAP_PROMPTS,
            "english": ENGLISH_MINDMAP_PROMPTS
        }
    
    def get_prompt_template(self, language: str) -> str:
        """Get the appropriate prompt template for the given language."""
        return self.prompt_templates.get(language, self.prompt_templates["english"])["main_template"]
    
    def get_planning_template(self, language: str) -> str:
        """Get the planning prompt for enhanced thinking."""
        prompts = self.prompt_templates.get(language, self.prompt_templates["english"])
        return prompts.get("planning_template")
    
    def clean_and_parse_json(self, response_text: str) -> Dict[str, Any]:
        """
        Clean and parse JSON response from OpenAI API with multiple fallback strategies
        """
        logger.debug(f"Original response: {response_text[:200]}...")
        
        # Strategy 1: Remove markdown code blocks
        cleaned_text = re.sub(r'```json\s*', '', response_text)
        cleaned_text = re.sub(r'```\s*$', '', cleaned_text, flags=re.MULTILINE)
        
        # Strategy 2: Extract JSON from response if it contains other text
        json_match = re.search(r'(\{.*\})', cleaned_text, re.DOTALL)
        if json_match:
            cleaned_text = json_match.group(1)
        
        # Strategy 3: Remove any leading/trailing whitespace and non-JSON characters
        cleaned_text = cleaned_text.strip()
        
        # Strategy 4: Try to find the start and end of JSON object
        start_idx = cleaned_text.find('{')
        end_idx = cleaned_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned_text = cleaned_text[start_idx:end_idx + 1]
        
        logger.debug(f"Cleaned text: {cleaned_text[:200]}...")
        
        # Try parsing strategies in order of preference
        parsing_strategies = [
            # Strategy 1: Direct JSON parsing
            lambda text: json.loads(text),
            
            # Strategy 2: Use json-repair library
            lambda text: json.loads(repair_json(text)),
            
            # Strategy 3: Remove common formatting issues and try again
            lambda text: json.loads(
                text.replace('\n', ' ')
                    .replace('\t', ' ')
                    .replace('  ', ' ')
                    .strip()
            ),
            
            # Strategy 4: Use json-repair on cleaned text
            lambda text: json.loads(repair_json(
                text.replace('\n', ' ')
                    .replace('\t', ' ')
                    .replace('  ', ' ')
                    .strip()
            )),
        ]
        
        for i, strategy in enumerate(parsing_strategies):
            try:
                result = strategy(cleaned_text)
                logger.debug(f"Successfully parsed JSON using strategy {i + 1}")
                return result
            except (json.JSONDecodeError, ValueError) as e:
                logger.debug(f"Strategy {i + 1} failed: {e}")
                continue
        
        # If all strategies fail, log the error and raise exception
        logger.error(f"All JSON parsing strategies failed for text: {cleaned_text[:500]}")
        raise ValueError("Unable to parse response as valid JSON after trying multiple strategies")
    
    def generate(self, content: str, goals: List[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate a mind map based on the provided content.
        
        Args:
            content: The educational content to create a mind map from
            goals: Learning goals (not used in mind map generation but kept for compatibility)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing the mind map in GoJS format
        """
        # Validate input
        self.validate_input(content)
        
        # Get content analysis if provided
        content_analysis = kwargs.get('content_analysis', {})
        
        # Truncate content if it's too long to prevent token overflow
        max_content_length = 2000  # Reduced for better performance with Arabic text
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
            logger.debug(f"Content truncated to {max_content_length} characters")
        
        # Clean the content
        content = content.strip()
        
        content = self._sanitize_content(content)

        # If multi-pass is enabled and content is long, split into chunks and merge
        if Settings.MINDMAP_MULTI_PASS and len(content) > Settings.MINDMAP_CHUNK_SIZE_CHARS:
            logger.debug("Using multi-pass chunking for long content")
            chunks = self._chunk_text(content, Settings.MINDMAP_CHUNK_SIZE_CHARS, Settings.MINDMAP_CHUNK_OVERLAP_CHARS)
            partial_maps: List[Dict[str, Any]] = []
            for idx, ch in enumerate(chunks):
                logger.debug(f"Generating partial mind map for chunk {idx+1}/{len(chunks)} size={len(ch)}")
                mm = self._generate_single_pass(ch)
                partial_maps.append(mm)
            merged = self._merge_mindmaps(partial_maps)
            merged = self._post_process_mindmap(merged)
            return merged
        
        # Single pass generation
        return self._generate_single_pass(content)
        
        # Get the prompt template for the detected language
        prompt_template = self.get_prompt_template(self.language)
        
        # Decide whether to use enhanced planning
        use_planning = Settings.MINDMAP_ENHANCED_THINKING and bool(self.get_planning_template(self.language))
        
        # Create the prompt(s)
        if use_planning:
            planning_prompt = ChatPromptTemplate.from_template(self.get_planning_template(self.language))
            main_prompt = ChatPromptTemplate.from_template(prompt_template)
        else:
            main_prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # Create chain(s)
        main_chain = create_stuff_documents_chain(llm=self.model, prompt=main_prompt)
        docs = [Document(page_content=content)]
        
        try:
            logger.debug(f"Generating mind map for content: {content[:100]}...")
            # Optional: planning phase (ignored output besides priming the model via conversation context)
            if use_planning:
                try:
                    planning_chain = create_stuff_documents_chain(llm=self.model, prompt=planning_prompt)
                    _ = planning_chain.invoke({"context": docs})
                except Exception as e:
                    logger.debug(f"Planning phase failed/ignored: {e}")
            
            # Invoke the main chain
            response = main_chain.invoke({"context": docs})
            
            logger.debug(f"Raw API response: {response[:200]}...")
            
            # Parse the JSON response
            mind_map_data = self.clean_and_parse_json(response)
            
            # Post-processing to improve structure without changing schema
            mind_map_data = self._post_process_mindmap(mind_map_data)
            
            # Validate the structure
            if "nodeDataArray" not in mind_map_data:
                raise ValueError("Invalid mind map structure: missing nodeDataArray")
            
            # Ensure we have the correct class field
            if "class" not in mind_map_data:
                mind_map_data["class"] = "go.TreeModel"
            
            logger.debug(f"Successfully generated mind map with {len(mind_map_data.get('nodeDataArray', []))} nodes")
            
            return mind_map_data
            
        except Exception as e:
            logger.error(f"Error generating mind map: {e}")
            logger.error(f"Full error details: {str(e)}")
            
            # Fallback: return a simple mind map structure
            fallback_map = {
                "class": "go.TreeModel",
                "nodeDataArray": [
                    {"key": 0, "text": "محتوى تعليمي" if self.language == "arabic" else "Educational Content", "loc": "0 0"},
                    {"key": 1, "parent": 0, "text": "نقطة رئيسية" if self.language == "arabic" else "Main Point", "brush": "skyblue", "dir": "right"}
                ]
            }
            
            logger.warning("Using fallback mind map structure")
            return fallback_map

    def _post_process_mindmap(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Improve balance, colors, and enforce safe limits. Output schema unchanged."""
        try:
            if not isinstance(data, dict):
                return data
            nodes = data.get("nodeDataArray")
            if not isinstance(nodes, list) or not nodes:
                return data
            
            # 1) Enforce class
            data.setdefault("class", "go.TreeModel")
            
            # 2) Find root and build index
            root = None
            by_key = {}
            for n in nodes:
                if isinstance(n, dict):
                    by_key[n.get("key")] = n
                    if n.get("parent") is None:
                        root = n
            if root is None:
                return data
            
            # 3) Limit max nodes
            if len(nodes) > Settings.MINDMAP_MAX_NODES:
                data["nodeDataArray"] = nodes[:Settings.MINDMAP_MAX_NODES]
                nodes = data["nodeDataArray"]
                # Rebuild index after trim
                by_key = {n.get("key"): n for n in nodes if isinstance(n, dict)}
            
            # 4) Depth calculation
            children = {}
            for n in nodes:
                p = n.get("parent")
                children.setdefault(p, []).append(n)
            
            def assign_depth(node, depth, visited):
                node["_depth"] = depth
                for ch in children.get(node.get("key"), []):
                    if ch.get("key") in visited:
                        continue
                    visited.add(ch.get("key"))
                    assign_depth(ch, depth + 1, visited)
            assign_depth(root, 0, {root.get("key")})
            
            # 5) Color by depth
            colors = Settings.MINDMAP_COLORS
            for n in nodes:
                depth = max(0, min(n.get("_depth", 0), len(colors) - 1))
                # Only set if missing to not fight the model
                if not n.get("brush"):
                    n["brush"] = colors[depth]
            
            # 6) Balance main branches directions
            main_branches = children.get(root.get("key"), [])
            # Alternate right/left deterministically
            for idx, n in enumerate(sorted(main_branches, key=lambda x: x.get("key", 0))):
                n["dir"] = "right" if idx % 2 == 0 else "left"
            
            # 7) Ensure loc only on root if absent
            if not root.get("loc"):
                root["loc"] = "0 0"
            
            # 8) Cleanup helper fields
            for n in nodes:
                if "_depth" in n:
                    del n["_depth"]
            
            return data
        except Exception as e:
            logger.debug(f"Post-process skipped due to error: {e}")
            return data

    # ---- New helpers for multi-pass generation ----
    def _sanitize_content(self, content: str) -> str:
        content = (content or "").strip()
        # Filter out problematic characters
        content = re.sub(r'[\uf000-\uf8ff]', '', content)
        # Normalize whitespace
        content = " ".join(content.split())
        return content

    def _chunk_text(self, text: str, size: int, overlap: int) -> List[str]:
        if size <= 0:
            return [text]
        chunks: List[str] = []
        start = 0
        n = len(text)
        while start < n:
            end = min(n, start + size)
            # Try to end at a sentence boundary within the window
            window = text[start:end]
            last_period = max(window.rfind('.'), window.rfind('!'), window.rfind('?'), window.rfind('\n'))
            if last_period != -1 and (start + last_period + 1) - start > size * 0.6:
                end = start + last_period + 1
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= n:
                break
            start = max(0, end - max(0, overlap))
        return chunks

    def _generate_single_pass(self, content: str) -> Dict[str, Any]:
        # Get the prompt template for the detected language
        prompt_template = self.get_prompt_template(self.language)
        use_planning = Settings.MINDMAP_ENHANCED_THINKING and bool(self.get_planning_template(self.language))

        # Create the prompt(s)
        if use_planning:
            planning_prompt = ChatPromptTemplate.from_template(self.get_planning_template(self.language))
            main_prompt = ChatPromptTemplate.from_template(prompt_template)
        else:
            main_prompt = ChatPromptTemplate.from_template(prompt_template)

        # Create chain(s)
        main_chain = create_stuff_documents_chain(llm=self.model, prompt=main_prompt)
        docs = [Document(page_content=content)]

        try:
            logger.debug(f"Generating mind map (single-pass) for content: {content[:100]}...")
            if use_planning:
                try:
                    planning_chain = create_stuff_documents_chain(llm=self.model, prompt=planning_prompt)
                    _ = planning_chain.invoke({"context": docs})
                except Exception as e:
                    logger.debug(f"Planning phase failed/ignored: {e}")

            response = main_chain.invoke({"context": docs})
            logger.debug(f"Raw API response: {str(response)[:200]}...")
            mind_map_data = self.clean_and_parse_json(response)
            mind_map_data = self._post_process_mindmap(mind_map_data)

            if "nodeDataArray" not in mind_map_data:
                raise ValueError("Invalid mind map structure: missing nodeDataArray")
            if "class" not in mind_map_data:
                mind_map_data["class"] = "go.TreeModel"
            return mind_map_data
        except Exception as e:
            logger.error(f"Error in single-pass generation: {e}")
            return {
                "class": "go.TreeModel",
                "nodeDataArray": [
                    {"key": 0, "text": "\u0645\u062d\u062a\u0648\u0649 \u062a\u0639\u0644\u064a\u0645\u064a" if self.language == "arabic" else "Educational Content", "loc": "0 0"},
                    {"key": 1, "parent": 0, "text": "\u0646\u0642\u0637\u0629 \u0631\u0626\u064a\u0633\u064a\u0629" if self.language == "arabic" else "Main Point", "brush": "skyblue", "dir": "right"}
                ]
            }

    def _merge_mindmaps(self, maps: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Combine multiple mind maps into a single GoJS tree model
        merged: Dict[str, Any] = {"class": "go.TreeModel", "nodeDataArray": []}
        # Collect roots and children
        all_nodes: List[Dict[str, Any]] = []
        for m in maps:
            nodes = m.get("nodeDataArray") if isinstance(m, dict) else None
            if isinstance(nodes, list):
                all_nodes.extend([n for n in nodes if isinstance(n, dict)])
        if not all_nodes:
            return merged

        # Heuristic: create a single synthetic root and attach each map's root as a main branch
        synthetic_root = {"key": 0, "text": "\u062e\u0631\u064a\u0637\u0629 \u0634\u0627\u0645\u0644\u0629" if self.language == "arabic" else "Comprehensive Mind Map", "loc": "0 0", "brush": Settings.MINDMAP_COLORS[0]}
        merged_nodes: List[Dict[str, Any]] = [synthetic_root]

        # Determine next key and remap keys to keep unique
        next_key = 1
        # Group by parent=None to find roots per map (original)
        roots: List[Dict[str, Any]] = []
        for m in maps:
            nodes = m.get("nodeDataArray") if isinstance(m, dict) else None
            if not isinstance(nodes, list):
                continue
            for n in nodes:
                if n.get("parent") is None:
                    roots.append(n)

        # Map old->new keys across all nodes
        key_map: Dict[Tuple[int, int], int] = {}
        # To deduplicate by parent/text
        seen_by_parent_text: Set[Tuple[int, str]] = set()

        # Helper: normalize text for deduplication
        def norm_text(t: Any) -> str:
            s = str(t or "")
            s = re.sub(r"\s+", " ", s).strip().lower()
            return s

        # Assign main branches for each map's root under synthetic root
        for idx, m in enumerate(maps):
            nodes = m.get("nodeDataArray") if isinstance(m, dict) else None
            if not isinstance(nodes, list) or not nodes:
                continue
            # Find root
            root = None
            for n in nodes:
                if n.get("parent") is None:
                    root = n
                    break
            if root is None:
                continue
            # Create a branch node representing this chunk
            branch_key = next_key; next_key += 1
            chunk_title = root.get("text") or (f"Chunk {idx+1}")
            dir_val = "right" if idx % 2 == 0 else "left"
            branch = {"key": branch_key, "parent": 0, "text": chunk_title, "dir": dir_val, "brush": Settings.MINDMAP_COLORS[1]}
            if (0, norm_text(chunk_title)) not in seen_by_parent_text or not Settings.MINDMAP_DEDUPLICATE_NODES:
                merged_nodes.append(branch)
                seen_by_parent_text.add((0, norm_text(chunk_title)))
            # Build adjacency for this map
            children: Dict[Any, List[Dict[str, Any]]] = {}
            for n in nodes:
                children.setdefault(n.get("parent"), []).append(n)
            # Remap subtree under this branch
            stack = [(root, branch_key)]
            while stack:
                orig_node, new_parent = stack.pop()
                # Skip the original root since we represented it as branch
                if orig_node is root:
                    for ch in children.get(orig_node.get("key"), []):
                        stack.append((ch, branch_key))
                    continue
                new_key = next_key; next_key += 1
                new_node = {
                    "key": new_key,
                    "parent": new_parent,
                    "text": orig_node.get("text"),
                    "brush": orig_node.get("brush"),
                    "dir": orig_node.get("dir")
                }
                parent_text_key = (new_parent, norm_text(new_node.get("text")))
                if Settings.MINDMAP_DEDUPLICATE_NODES and parent_text_key in seen_by_parent_text:
                    # skip duplicate under same parent
                    pass
                else:
                    merged_nodes.append(new_node)
                    seen_by_parent_text.add(parent_text_key)
                    for ch in children.get(orig_node.get("key"), []):
                        stack.append((ch, new_key))

        # Enforce max nodes
        if len(merged_nodes) > Settings.MINDMAP_MAX_NODES:
            merged_nodes = merged_nodes[:Settings.MINDMAP_MAX_NODES]

        merged["nodeDataArray"] = merged_nodes
        return merged
