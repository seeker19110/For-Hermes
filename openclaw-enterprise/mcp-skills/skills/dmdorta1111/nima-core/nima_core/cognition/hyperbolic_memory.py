#!/usr/bin/env python3
"""
Hyperbolic Memory — Frontier 8
==============================

Hierarchical knowledge representation in hyperbolic space.

Key insight: Hyperbolic space (Poincaré ball) has exponential growth
near the boundary, making it natural for tree-like hierarchies.

Based on: Nickel & Kiela "Poincaré Embeddings for Learning Hierarchical Representations"

Author: NIMA Project
Date: 2026
"""

import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
import json
from datetime import datetime
import math
import os

from ..config import NIMA_DATA_DIR

HYPERBOLIC_DIR = NIMA_DATA_DIR / "hyperbolic"
HYPERBOLIC_DIR.mkdir(parents=True, exist_ok=True)


def poincare_distance(u: torch.Tensor, v: torch.Tensor, eps: float = 1e-5) -> torch.Tensor:
    """
    Compute hyperbolic distance in Poincaré ball.
    
    d(u,v) = arcosh(1 + 2 * ||u-v||² / ((1-||u||²)(1-||v||²)))
    """
    u_norm_sq = torch.sum(u ** 2)
    v_norm_sq = torch.sum(v ** 2)
    diff_norm_sq = torch.sum((u - v) ** 2)
    
    u_norm_sq = torch.clamp(u_norm_sq, min=0.0, max=1 - eps)
    v_norm_sq = torch.clamp(v_norm_sq, min=0.0, max=1 - eps)
    
    numerator = 2 * diff_norm_sq
    denominator = (1 - u_norm_sq) * (1 - v_norm_sq)
    
    x = 1 + numerator / (denominator + eps)
    x = torch.clamp(x, min=1 + eps)
    
    return torch.log(x + torch.sqrt(x ** 2 - 1))


def mobius_add(u: torch.Tensor, v: torch.Tensor, eps: float = 1e-5) -> torch.Tensor:
    """
    Möbius addition in Poincaré ball.
    """
    u_norm_sq = torch.sum(u ** 2)
    v_norm_sq = torch.sum(v ** 2)
    uv_dot = torch.sum(u * v)
    
    u_norm_sq = torch.clamp(u_norm_sq, min=0.0, max=1 - eps)
    v_norm_sq = torch.clamp(v_norm_sq, min=0.0, max=1 - eps)
    
    numerator = (1 + 2 * uv_dot + v_norm_sq) * u + (1 - u_norm_sq) * v
    denominator = 1 + 2 * uv_dot + u_norm_sq * v_norm_sq
    
    result = numerator / (denominator + eps)
    
    result_norm = torch.norm(result)
    if result_norm.item() >= 1:
        result = result / (result_norm + eps) * (1 - eps)
    
    return result


def exp_map(v: torch.Tensor, p: torch.Tensor = None, eps: float = 1e-5) -> torch.Tensor:
    """
    Exponential map: tangent space → Poincaré ball.
    """
    if p is None:
        p = torch.zeros_like(v)
    
    v_norm = torch.norm(v)
    if v_norm < eps:
        return p
    
    p_norm_sq = torch.sum(p ** 2)
    lambda_p = 2 / (1 - p_norm_sq + eps)
    
    scaled = torch.tanh(lambda_p * v_norm / 2) * v / (v_norm + eps)
    
    return mobius_add(p, scaled)


def log_map(y: torch.Tensor, p: torch.Tensor = None, eps: float = 1e-5) -> torch.Tensor:
    """
    Logarithmic map: Poincaré ball → tangent space.
    """
    if p is None:
        p = torch.zeros_like(y)
    
    neg_p = -p
    diff = mobius_add(neg_p, y)
    
    diff_norm = torch.norm(diff)
    if diff_norm.item() < eps:
        return torch.zeros_like(y)
    
    p_norm_sq = torch.sum(p ** 2)
    lambda_p = 2 / (1 - p_norm_sq + eps)
    
    clamped_norm = torch.clamp(diff_norm, min=eps, max=1-eps)
    
    return 2 / lambda_p * torch.atanh(clamped_norm) * diff / (diff_norm + eps)


@dataclass
class HyperbolicConcept:
    """A concept represented in hyperbolic space."""
    name: str
    embedding: torch.Tensor  # Position in Poincaré ball
    level: int  # Hierarchy level (0 = root)
    parent: Optional[str] = None
    children: List[str] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
    
    @property
    def radius(self) -> float:
        """Distance from origin."""
        return float(torch.norm(self.embedding))


class HyperbolicTaxonomy:
    """
    Hierarchical concept taxonomy in hyperbolic space.
    
    Concepts near the center are abstract/general.
    Concepts near the boundary are specific/concrete.
    """
    
    def __init__(self, dimension: int = 50, data_dir: Path = None):
        self.dimension = dimension
        self.concepts: Dict[str, HyperbolicConcept] = {}
        
        if data_dir is None:
            data_dir = HYPERBOLIC_DIR
        
        self.add_concept("ROOT", torch.zeros(dimension), level=0)
        self.state_path = data_dir / "taxonomy.pt"
    
    def add_concept(
        self,
        name: str,
        embedding: torch.Tensor = None,
        level: int = 1,
        parent: str = None,
    ) -> HyperbolicConcept:
        """Add a concept to the taxonomy."""
        if embedding is None:
            radius = min(0.9, level * 0.15 + 0.1)
            direction = torch.randn(self.dimension)
            direction = direction / torch.norm(direction)
            embedding = direction * radius
        
        concept = HyperbolicConcept(
            name=name,
            embedding=embedding,
            level=level,
            parent=parent,
        )
        
        self.concepts[name] = concept
        
        if parent and parent in self.concepts:
            self.concepts[parent].children.append(name)
        
        return concept
    
    def distance(self, name1: str, name2: str) -> float:
        """Hyperbolic distance between two concepts."""
        if name1 not in self.concepts or name2 not in self.concepts:
            return float('inf')
        
        return float(poincare_distance(
            self.concepts[name1].embedding,
            self.concepts[name2].embedding,
        ))
    
    def nearest_neighbors(self, name: str, k: int = 5) -> List[Tuple[str, float]]:
        """Find k nearest concepts in hyperbolic space."""
        if name not in self.concepts:
            return []
        
        query = self.concepts[name].embedding
        distances = []
        
        for other_name, concept in self.concepts.items():
            if other_name != name:
                dist = poincare_distance(query, concept.embedding)
                distances.append((other_name, float(dist)))
        
        distances.sort(key=lambda x: x[1])
        return distances[:k]
    
    def find_common_ancestor(self, name1: str, name2: str) -> Optional[str]:
        """Find lowest common ancestor of two concepts."""
        if name1 not in self.concepts or name2 not in self.concepts:
            return None
        
        def get_ancestors(name):
            ancestors = [name]
            current = name
            while self.concepts[current].parent:
                current = self.concepts[current].parent
                ancestors.append(current)
            return ancestors
        
        ancestors1 = set(get_ancestors(name1))
        ancestors2 = get_ancestors(name2)
        
        for a in ancestors2:
            if a in ancestors1:
                return a
        
        return "ROOT"
    
    def get_subtree(self, name: str) -> List[str]:
        """Get all descendants of a concept."""
        if name not in self.concepts:
            return []
        
        result = [name]
        for child in self.concepts[name].children:
            result.extend(self.get_subtree(child))
        
        return result
    
    def embed_text_to_level(self, text: str, parent: str = "ROOT") -> HyperbolicConcept:
        """Embed text as a concept in the taxonomy."""
        parent_concept = self.concepts.get(parent)
        level = (parent_concept.level + 1) if parent_concept else 1
        
        import hashlib
        text_hash = hashlib.sha256(text.encode()).digest()
        direction = torch.tensor([float(b) / 128.0 - 1.0 for b in text_hash[:self.dimension]])
        direction = direction / torch.norm(direction)
        
        if parent_concept:
            radius_step = 0.15
            tangent = direction * radius_step
            embedding = exp_map(tangent, parent_concept.embedding)
        else:
            radius = min(0.9, level * 0.15 + 0.1)
            embedding = direction * radius
        
        return self.add_concept(text, embedding, level, parent)
    
    def get_hierarchy_stats(self) -> Dict:
        """Get statistics about the taxonomy."""
        levels = {}
        for concept in self.concepts.values():
            levels[concept.level] = levels.get(concept.level, 0) + 1
        
        radii = [c.radius for c in self.concepts.values()]
        
        return {
            "total_concepts": len(self.concepts),
            "levels": levels,
            "max_level": max(levels.keys()) if levels else 0,
            "avg_radius": sum(radii) / len(radii) if radii else 0,
            "max_radius": max(radii) if radii else 0,
        }
    
    def save(self):
        """Save taxonomy to disk."""
        data = {
            "dimension": self.dimension,
            "concepts": {
                name: {
                    "embedding": c.embedding,
                    "level": c.level,
                    "parent": c.parent,
                    "children": c.children,
                }
                for name, c in self.concepts.items()
            },
            "saved_at": datetime.now().isoformat(),
        }
        from ..utils import atomic_torch_save
        atomic_torch_save(data, self.state_path)
        print(f"💾 Saved {len(self.concepts)} concepts to hyperbolic taxonomy")
    
    def load(self) -> bool:
        """Load taxonomy from disk."""
        if not self.state_path.exists():
            return False
        
        try:
            from ..utils import safe_torch_load
            data = safe_torch_load(self.state_path)
            self.dimension = data.get("dimension", 50)
            
            for name, c in data.get("concepts", {}).items():
                self.concepts[name] = HyperbolicConcept(
                    name=name,
                    embedding=c["embedding"],
                    level=c["level"],
                    parent=c.get("parent"),
                    children=c.get("children", []),
                )
            
            print(f"📂 Loaded {len(self.concepts)} concepts from hyperbolic taxonomy")
            return True
        except Exception as e:
            print(f"⚠️ Failed to load taxonomy: {e}")
            return False


def build_domain_taxonomy():
    """Build initial domain taxonomy for NIMA."""
    print("=" * 60)
    print("HYPERBOLIC TAXONOMY — FRONTIER 8")
    print("=" * 60)
    
    taxonomy = HyperbolicTaxonomy(dimension=50)
    
    # Level 1: Main domains
    domains = [
        "technical",
        "personal", 
        "creative",
        "relational",
    ]
    
    for domain in domains:
        taxonomy.add_concept(domain, level=1, parent="ROOT")
    
    # Level 2: Sub-domains
    subdomains = {
        "technical": ["programming", "infrastructure", "algorithms", "architecture"],
        "personal": ["family", "health", "goals", "memories"],
        "creative": ["writing", "music", "visual", "ideas"],
        "relational": ["friends", "community"],
    }
    
    for parent, children in subdomains.items():
        for child in children:
            taxonomy.add_concept(child, level=2, parent=parent)
    
    # Level 3: Specific concepts
    specifics = {
        "programming": ["python", "typescript", "vsa", "embeddings"],
        "algorithms": ["sparse_retrieval", "binding", "convolution"],
    }
    
    for parent, children in specifics.items():
        for child in children:
            taxonomy.add_concept(child, level=3, parent=parent)
    
    print("\n📊 Taxonomy Statistics:")
    stats = taxonomy.get_hierarchy_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n📏 Distance Tests:")
    pairs = [
        ("python", "typescript"),
        ("python", "family"),
        ("ROOT", "vsa"),
    ]
    
    for a, b in pairs:
        dist = taxonomy.distance(a, b)
        print(f"   d({a}, {b}) = {dist:.4f}")
    
    taxonomy.save()
    
    print("\n" + "=" * 60)
    print("Hyperbolic Taxonomy READY")
    print("=" * 60)
    
    return taxonomy


if __name__ == "__main__":
    build_domain_taxonomy()
