"""Reprocess existing mind maps stored in MongoDB.

Goal:
- Load existing mindmaps from ai.mindmaps collection
- Preserve ONLY key, text, parent fields from stored mindmap.nodeDataArray
- Recompute (dir, brush, loc root, colors, balancing) using shared post_process_mindmap
- Update the document in-place adding metadata.reprocessed_at and metadata.reprocess_changes

Safety:
- Dry run mode (default unless --apply specified) prints proposed changes summary
- Limit processing via --limit N
- Filter by filename / custom_id / contains-text (search node text) via CLI args
- Skip documents lacking minimal structure

Usage examples:
  Dry run first 10:
    python reprocess_mindmaps.py --limit 10
  Apply to all mindmaps containing Arabic word "الطاقة":
    python reprocess_mindmaps.py --apply --contains-text الطاقة
  Filter by filename substring:
    python reprocess_mindmaps.py --apply --filename lesson1

"""
from __future__ import annotations
import argparse
from datetime import datetime
from typing import Dict, Any, List
import copy
import sys
import os

# Ensure local imports work if run directly
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from clients.mongo_client import MongoDBClient  # type: ignore
from utils.mindmap_postprocess import post_process_mindmap
from config.settings import Settings  # type: ignore


def extract_minimal(node: Dict[str, Any]) -> Dict[str, Any]:
    """Extract only required fields from a node for rebuilding working model."""
    return {
        "key": node.get("key"),
        "text": node.get("text"),
        "parent": node.get("parent")  # can be None for root
    }



def rebuild_working_model(original_mm: Dict[str, Any]) -> Dict[str, Any]:
    """Return a minimal model (class + nodeDataArray) with only required fields."""
    nodes = original_mm.get("nodeDataArray") if isinstance(original_mm, dict) else None
    if not isinstance(nodes, list):
        return {}
    minimal_nodes: List[Dict[str, Any]] = []
    for n in nodes:
        if not isinstance(n, dict):
            continue
        # Must have key + text; parent can be None
        if "key" not in n or "text" not in n:
            continue
        minimal_nodes.append(extract_minimal(n))
    if not minimal_nodes:
        return {}
    return {"class": "go.TreeModel", "nodeDataArray": minimal_nodes}


def diff_brief(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    """Create a summary of changes (counts) rather than full diff for brevity."""
    b_nodes = before.get("nodeDataArray", []) if isinstance(before, dict) else []
    a_nodes = after.get("nodeDataArray", []) if isinstance(after, dict) else []
    changes = {
        "before_nodes": len(b_nodes),
        "after_nodes": len(a_nodes),
        "dir_assigned": sum(1 for n in a_nodes if n.get("dir") in ("left", "right")),
        "brush_assigned": sum(1 for n in a_nodes if "brush" in n),
        "root_loc": next((n.get("loc") for n in a_nodes if n.get("parent") is None), None)
    }
    return changes


def process_record(record: Dict[str, Any]) -> Dict[str, Any] | None:
    mindmap = record.get("mindmap")
    if not isinstance(mindmap, dict):
        return None
    minimal = rebuild_working_model(mindmap)
    if not minimal:
        return None
    processed = post_process_mindmap(copy.deepcopy(minimal))
    return processed


def main():
    parser = argparse.ArgumentParser(description="Reprocess existing mind maps (balance, colors, directions)")
    parser.add_argument("--apply", action="store_true", help="Apply updates (omit for dry run)")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of documents processed (0 = no limit)")
    parser.add_argument("--filename", type=str, help="Filter by filename substring", default=None)
    parser.add_argument("--custom-id", type=str, help="Filter by custom_id", default=None)
    parser.add_argument("--contains-text", type=str, help="Filter by node text substring (case-insensitive)", default=None)

    args = parser.parse_args()

    client = MongoDBClient()
    if not client.connect():
        print("Failed to connect to MongoDB")
        sys.exit(1)

    collection = client.storage_db["mindmaps"]  # type: ignore

    query = {}
    if args.custom_id:
        query["custom_id"] = args.custom_id
    if args.filename:
        query["filename"] = {"$regex": args.filename, "$options": "i"}

    cursor = collection.find(query)
    processed_count = 0
    updated_count = 0

    for record in cursor:
        if args.limit and processed_count >= args.limit:
            break

        # Early text filter using existing nodes if requested
        if args.contains_text:
            mm = record.get("mindmap", {})
            nodes = mm.get("nodeDataArray", []) if isinstance(mm, dict) else []
            if not any(args.contains_text.lower() in str(n.get("text", "")).lower() for n in nodes):
                continue

        before_model = rebuild_working_model(record.get("mindmap", {}))
        if not before_model:
            continue

        after_model = process_record(record)
        if after_model is None:
            continue

        change_summary = diff_brief(before_model, after_model)
        processed_count += 1

        print(f"[{processed_count}] filename={record.get('filename')} doc_uuid={record.get('document_uuid')} changes={change_summary}")

        if args.apply:
            # Merge updated computed fields back into original mindmap while preserving original node order
            # Create mapping for updated nodes by (key)
            updated_by_key = {n.get("key"): n for n in after_model.get("nodeDataArray", [])}
            original_nodes = record.get("mindmap", {}).get("nodeDataArray", [])
            new_nodes = []
            for orig in original_nodes:
                if not isinstance(orig, dict):
                    continue
                k = orig.get("key")
                upd = updated_by_key.get(k)
                if upd:
                    # Preserve key,text,parent; copy brush/dir/loc if present
                    merged = {
                        "key": upd.get("key"),
                        "text": upd.get("text")
                    }
                    if upd.get("parent") is not None:
                        merged["parent"] = upd.get("parent")
                    if "dir" in upd:
                        merged["dir"] = upd["dir"]
                    if "brush" in upd:
                        merged["brush"] = upd["brush"]
                    if orig.get("parent") is None:  # root only
                        if upd.get("loc"):
                            merged["loc"] = upd["loc"]
                        elif orig.get("loc"):
                            merged["loc"] = orig.get("loc")
                    new_nodes.append(merged)
                else:
                    # Node got pruned (depth/exclusion). We drop it.
                    pass
            # Replace mindmap structure
            record["mindmap"]["nodeDataArray"] = new_nodes
            record.setdefault("mindmap", {}).setdefault("class", "go.TreeModel")
            # Update metadata
            md = record.setdefault("metadata", {})
            md["reprocessed_at"] = datetime.utcnow()
            md.setdefault("reprocess_runs", 0)
            md["reprocess_runs"] += 1
            md["reprocess_changes"] = change_summary

            res = collection.update_one({"_id": record["_id"]}, {"$set": {
                "mindmap": record["mindmap"],
                "metadata": md
            }})
            if res.modified_count:
                updated_count += 1

    print("--- Summary ---")
    print(f"Processed: {processed_count}")
    if args.apply:
        print(f"Updated:   {updated_count}")
    else:
        print("(Dry run) Use --apply to persist changes")

    client.disconnect()

if __name__ == "__main__":
    main()
