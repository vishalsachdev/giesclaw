"""
Knowledge Graph - Track relationships between business entities.

Maintains a graph of companies, industries, concepts, people, and their
relationships discovered during investigations.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any


class KnowledgeGraph:
    """Graph of business entities and their relationships."""

    def __init__(self, agent_name: str, base_dir: Optional[str] = None):
        self.agent_name = agent_name
        if base_dir is None:
            base_dir = os.path.expanduser("~/.giesclaw/knowledge")
        self.kg_dir = Path(base_dir) / agent_name
        self.kg_dir.mkdir(parents=True, exist_ok=True)
        self.nodes_path = self.kg_dir / "nodes.json"
        self.edges_path = self.kg_dir / "edges.json"
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if self.nodes_path.exists():
            try:
                with open(self.nodes_path) as f:
                    self.nodes = json.load(f)
            except Exception:
                pass
        if self.edges_path.exists():
            try:
                with open(self.edges_path) as f:
                    self.edges = json.load(f)
            except Exception:
                pass

    def _save(self):
        with open(self.nodes_path, "w") as f:
            json.dump(self.nodes, f, indent=2)
        with open(self.edges_path, "w") as f:
            json.dump(self.edges, f, indent=2)

    def add_entity(
        self,
        entity_id: str,
        entity_type: str,
        name: str,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """
        Add a business entity to the knowledge graph.

        Entity types: company, industry, person, concept, market, product,
                      technology, regulation, metric
        """
        self.nodes[entity_id] = {
            "id": entity_id,
            "type": entity_type,
            "name": name,
            "properties": properties or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save()

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship: str,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """
        Add a relationship between entities.

        Relationship types: competes_with, supplies_to, acquires, invests_in,
                            operates_in, leads, disrupts, regulates, correlates_with
        """
        self.edges.append({
            "source": source_id,
            "target": target_id,
            "relationship": relationship,
            "properties": properties or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        self._save()

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        return self.nodes.get(entity_id)

    def get_relationships(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get all relationships involving an entity."""
        return [e for e in self.edges if e["source"] == entity_id or e["target"] == entity_id]

    def get_competitors(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get competitors of an entity."""
        rels = [e for e in self.edges
                if e["relationship"] == "competes_with"
                and (e["source"] == entity_id or e["target"] == entity_id)]
        competitor_ids = set()
        for r in rels:
            competitor_ids.add(r["target"] if r["source"] == entity_id else r["source"])
        return [self.nodes[cid] for cid in competitor_ids if cid in self.nodes]

    def search_entities(self, query: str, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search entities by name or properties."""
        query_lower = query.lower()
        results = []
        for node in self.nodes.values():
            if entity_type and node["type"] != entity_type:
                continue
            if query_lower in node["name"].lower() or query_lower in json.dumps(node).lower():
                results.append(node)
        return results

    def get_stats(self) -> Dict[str, Any]:
        types: Dict[str, int] = {}
        for node in self.nodes.values():
            t = node["type"]
            types[t] = types.get(t, 0) + 1
        rel_types: Dict[str, int] = {}
        for edge in self.edges:
            r = edge["relationship"]
            rel_types[r] = rel_types.get(r, 0) + 1
        return {
            "total_entities": len(self.nodes),
            "total_relationships": len(self.edges),
            "entity_types": types,
            "relationship_types": rel_types,
        }
