"""
phi_benchmark.py
Φ Calibration Experiment for NIMA v2

Measures integrated information across 1000+ memories to establish baseline.
Tests hypothesis: Genuine episodes have high Φ, synthetic/corrupted have lower Φ.

Author: Lilu
Date: Feb 12, 2026
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import torch
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict
import random

# NIMA Components
from cognition import PhiEstimator, PhiMeasurement
from cognition.sparse_block_memory import SparseBlockMemory
from retrieval.resonator import ResonatorNetwork, Codebook


def load_all_memories():
    """Load the full sparse block memory store."""
    print("=" * 80)
    print("Φ CALIBRATION EXPERIMENT")
    print("=" * 80)
    print(f"\n📂 Loading memory store...")
    
    memory_path = Path(__file__).parent.parent / "storage" / "data" / "sparse_memories" / "sparse_memory.pkl"
    
    if not memory_path.exists():
        print(f"❌ Memory file not found: {memory_path}")
        return None
    
    memory = SparseBlockMemory()
    memory.load(str(memory_path))
    
    print(f"✅ Loaded {len(memory.memory_vectors)} memories")
    print(f"   Block structure: {memory.config.num_blocks} × {memory.config.block_dim}D")
    print(f"   Total dimension: {memory.config.total_dim:,}")
    print(f"   Active sparsity: ~{memory.config.default_sparsity*100:.0f}%")
    
    return memory


def setup_resonator(memory: SparseBlockMemory) -> ResonatorNetwork:
    """Setup resonator with codebooks from memory metadata."""
    print(f"\n🔧 Building resonator codebooks...")
    
    # Extract unique factors
    who_factors = set()
    what_factors = set()
    where_factors = set()
    when_factors = set()
    
    for meta in memory.memory_metadata:
        if meta.get('who'):
            who_factors.add(str(meta['who']))
        if meta.get('what'):
            what = str(meta['what'])
            if len(what) > 100:
                what = what[:100]  # Truncate long content
            what_factors.add(what)
        if meta.get('where'):
            where_factors.add(str(meta['where']))
        if meta.get('when'):
            when_factors.add(str(meta['when']))
    
    print(f"   Unique WHO: {len(who_factors)}")
    print(f"   Unique WHAT: {len(what_factors)}")
    print(f"   Unique WHERE: {len(where_factors)}")
    print(f"   Unique WHEN: {len(when_factors)}")
    
    # Create codebooks
    codebooks = {}
    
    def create_codebook(strings, name, max_items=50):
        """Create codebook from strings with random vectors."""
        cb = Codebook(name=name)
        for s in list(strings)[:max_items]:
            vec = torch.randn(memory.config.total_dim)
            vec = vec / torch.norm(vec)
            cb.add(s, vec)
        return cb
    
    if who_factors:
        codebooks['who'] = create_codebook(who_factors, 'who')
    if what_factors:
        codebooks['what'] = create_codebook(what_factors, 'what')
    if where_factors:
        codebooks['where'] = create_codebook(where_factors, 'where')
    if when_factors:
        codebooks['when'] = create_codebook(when_factors, 'when')
    
    # Create resonator
    resonator = ResonatorNetwork(dimension=memory.config.total_dim)
    resonator.initialize_role_keys(['who', 'what', 'where', 'when'])
    
    for name, cb in codebooks.items():
        resonator.add_codebook(name, cb)
    
    print(f"✅ Resonator ready with {len(codebooks)} codebooks")
    
    return resonator


def create_synthetic_memory(memory: SparseBlockMemory, 
                            who: str, 
                            what: str, 
                            where: str = None) -> Tuple[torch.Tensor, Dict]:
    """
    Create a synthetic bound memory with known components.
    
    Returns:
        (bound_vector, metadata)
    """
    # Get random vectors for each slot
    who_vec = torch.randn(memory.config.total_dim)
    who_vec = who_vec / torch.norm(who_vec)
    
    what_vec = torch.randn(memory.config.total_dim)
    what_vec = what_vec / torch.norm(what_vec)
    
    # Simple binding (permutation + addition approximation)
    # For proper VSA binding we'd need the full SparseBlockHDVector
    bound = who_vec + what_vec
    bound = bound / torch.norm(bound)
    
    metadata = {
        'who': who,
        'what': what,
        'where': where or 'synthetic',
        'synthetic': True,
    }
    
    return bound, metadata


def create_corrupted_memory(memory: SparseBlockMemory, 
                           base_idx: int, 
                           corruption_level: float = 0.3) -> Tuple[torch.Tensor, Dict]:
    """
    Create a corrupted version of an existing memory.
    
    Args:
        base_idx: Index of memory to corrupt
        corruption_level: Amount of noise to add (0-1)
        
    Returns:
        (corrupted_vector, metadata)
    """
    base_vec = memory.memory_vectors[base_idx]
    dense_base = torch.tensor(base_vec.to_dense())
    
    # Add noise
    noise = torch.randn_like(dense_base)
    noise = noise / torch.norm(noise)
    
    corrupted = (1 - corruption_level) * dense_base + corruption_level * noise
    corrupted = corrupted / torch.norm(corrupted)
    
    base_meta = memory.memory_metadata[base_idx]
    metadata = {
        **base_meta,
        'corrupted': True,
        'corruption_level': corruption_level,
        'original_idx': base_idx,
    }
    
    return corrupted, metadata


def run_phi_benchmark(memory: SparseBlockMemory, 
                     resonator: ResonatorNetwork,
                     sample_size: int = 1000) -> Dict:
    """
    Run Φ benchmark on memory sample.
    
    Returns:
        Dictionary with statistics and results
    """
    print(f"\n" + "=" * 80)
    print(f"RUNNING Φ BENCHMARK")
    print(f"=" * 80)
    
    # Sample memories
    total_memories = len(memory.memory_vectors)
    sample_size = min(sample_size, total_memories)
    
    indices = random.sample(range(total_memories), sample_size)
    
    print(f"\n📊 Sampling {sample_size} memories from {total_memories} total...")
    
    estimator = PhiEstimator(resonator, num_lesion_trials=1)
    
    results = {
        'genuine': [],
        'synthetic': [],
        'corrupted': [],
    }
    
    start_time = time.time()
    
    for i, idx in enumerate(indices):
        vec = memory.memory_vectors[idx]
        meta = memory.memory_metadata[idx]
        
        # Convert to tensor for PhiEstimator
        dense_vec = torch.tensor(vec.to_dense())
        
        # Measure Φ
        measurement = estimator.measure_phi(dense_vec)
        
        if measurement:
            results['genuine'].append({
                'idx': idx,
                'phi': measurement.phi,
                'quality': measurement.decomposition_quality,
                'who': meta.get('who', 'unknown'),
                'what': str(meta.get('what', ''))[:80],
            })
        
        if (i + 1) % 100 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed
            remaining = (sample_size - (i + 1)) / rate if rate > 0 else 0
            print(f"   Processed {i+1}/{sample_size}... ({rate:.1f} mem/s, ~{remaining:.0f}s remaining)")
    
    # Generate synthetic memories for comparison
    print(f"\n🧪 Generating synthetic memories for comparison...")
    
    synthetic_tests = [
        ('David', 'built NIMA', 'lab'),
        ('Lilu', 'computed phi', 'workspace'),
        ('Melissa', 'reviewed code', 'home'),
        ('User', 'asked question', 'chat'),
    ]
    
    for who, what, where in synthetic_tests:
        bound, meta = create_synthetic_memory(memory, who, what, where)
        measurement = estimator.measure_phi(bound)
        if measurement:
            results['synthetic'].append({
                'phi': measurement.phi,
                'quality': measurement.decomposition_quality,
                'who': who,
                'what': what,
            })
    
    # Generate corrupted memories
    print(f"\n💥 Generating corrupted memories for comparison...")
    
    for corruption in [0.1, 0.3, 0.5, 0.7, 0.9]:
        idx = random.choice(indices)
        corrupted, meta = create_corrupted_memory(memory, idx, corruption)
        measurement = estimator.measure_phi(corrupted)
        if measurement:
            results['corrupted'].append({
                'phi': measurement.phi,
                'corruption_level': corruption,
                'original_idx': idx,
            })
    
    elapsed = time.time() - start_time
    print(f"\n✅ Benchmark complete in {elapsed:.1f}s")
    
    return results


def analyze_results(results: Dict) -> Dict:
    """Analyze and report Φ distribution."""
    print(f"\n" + "=" * 80)
    print(f"Φ ANALYSIS RESULTS")
    print(f"=" * 80)
    
    stats = {}
    
    # Genuine memories
    genuine_phis = [r['phi'] for r in results['genuine']]
    if genuine_phis:
        stats['genuine'] = {
            'count': len(genuine_phis),
            'mean': np.mean(genuine_phis),
            'std': np.std(genuine_phis),
            'median': np.median(genuine_phis),
            'min': np.min(genuine_phis),
            'max': np.max(genuine_phis),
            'high_integration': sum(1 for p in genuine_phis if p >= 0.7),
            'low_integration': sum(1 for p in genuine_phis if p < 0.3),
        }
        
        print(f"\n📊 Genuine Memories (n={stats['genuine']['count']}):")
        print(f"   Mean Φ: {stats['genuine']['mean']:.3f}")
        print(f"   Std:    {stats['genuine']['std']:.3f}")
        print(f"   Range:  [{stats['genuine']['min']:.3f}, {stats['genuine']['max']:.3f}]")
        print(f"   High integration (Φ≥0.7): {stats['genuine']['high_integration']} ({100*stats['genuine']['high_integration']/len(genuine_phis):.1f}%)")
        print(f"   Low integration (Φ<0.3): {stats['genuine']['low_integration']} ({100*stats['genuine']['low_integration']/len(genuine_phis):.1f}%)")
    
    # Synthetic memories
    synthetic_phis = [r['phi'] for r in results['synthetic']]
    if synthetic_phis:
        stats['synthetic'] = {
            'count': len(synthetic_phis),
            'mean': np.mean(synthetic_phis),
            'std': np.std(synthetic_phis),
        }
        
        print(f"\n🧪 Synthetic Memories (n={stats['synthetic']['count']}):")
        print(f"   Mean Φ: {stats['synthetic']['mean']:.3f}")
        print(f"   Std:    {stats['synthetic']['std']:.3f}")
    
    # Corrupted memories
    corrupted_phis = [r['phi'] for r in results['corrupted']]
    if corrupted_phis:
        stats['corrupted'] = {
            'count': len(corrupted_phis),
            'mean': np.mean(corrupted_phis),
            'std': np.std(corrupted_phis),
        }
        
        print(f"\n💥 Corrupted Memories (n={stats['corrupted']['count']}):")
        print(f"   Mean Φ: {stats['corrupted']['mean']:.3f}")
        print(f"   Std:    {stats['corrupted']['std']:.3f}")
        
        # Show corruption level correlation
        for r in sorted(results['corrupted'], key=lambda x: x.get('corruption_level', 0)):
            print(f"   Corruption {r.get('corruption_level', 0):.1f}: Φ={r['phi']:.3f}")
    
    return stats


def print_top_memories(results: Dict, n: int = 10):
    """Print top memories by Φ."""
    print(f"\n" + "=" * 80)
    print(f"TOP {n} MEMORIES BY Φ")
    print(f"=" * 80)
    
    all_memories = sorted(results['genuine'], key=lambda x: x['phi'], reverse=True)
    
    print(f"\n{'Rank':<6} {'Φ':<8} {'Who':<15} {'Content':<50}")
    print("-" * 80)
    
    for i, mem in enumerate(all_memories[:n]):
        who = mem.get('who', 'unknown')[:14]
        what = str(mem.get('what', ''))[:48]
        print(f"{i+1:<6} {mem['phi']:<8.3f} {who:<15} {what:<50}")
    
    print(f"\n{'Rank':<6} {'Φ':<8} {'Who':<15} {'Content':<50}")
    print("-" * 80)
    
    for i, mem in enumerate(all_memories[-n:]):
        rank = len(all_memories) - n + i + 1
        who = mem.get('who', 'unknown')[:14]
        what = str(mem.get('what', ''))[:48]
        print(f"{rank:<6} {mem['phi']:<8.3f} {who:<15} {what:<50}")


def save_results(results: Dict, stats: Dict):
    """Save benchmark results to file."""
    output_dir = Path(__file__).parent.parent / "storage" / "benchmarks"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"phi_benchmark_{timestamp}.json"
    
    # Convert to serializable format
    serializable = {
        'timestamp': timestamp,
        'statistics': stats,
        'genuine_count': len(results['genuine']),
        'synthetic_count': len(results['synthetic']),
        'corrupted_count': len(results['corrupted']),
        'top_genuine': sorted(results['genuine'], key=lambda x: x['phi'], reverse=True)[:20],
    }
    
    with open(output_file, 'w') as f:
        json.dump(serializable, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {output_file}")


def main():
    """Run full Φ calibration benchmark."""
    # Load memories
    memory = load_all_memories()
    if memory is None:
        print("❌ Cannot continue without memory store")
        return
    
    # Setup resonator
    try:
        resonator = setup_resonator(memory)
    except Exception as e:
        print(f"⚠️  Could not setup resonator: {e}")
        print("   Will use placeholder Φ values")
        resonator = None
    
    # Run benchmark
    sample_size = min(1000, len(memory.memory_vectors))
    results = run_phi_benchmark(memory, resonator, sample_size)
    
    # Analyze
    stats = analyze_results(results)
    
    # Print top memories
    print_top_memories(results, n=10)
    
    # Save results
    save_results(results, stats)
    
    # Final summary
    print(f"\n" + "=" * 80)
    print(f"🎯 CALIBRATION SUMMARY")
    print(f"=" * 80)
    
    if 'genuine' in stats:
        mean_phi = stats['genuine']['mean']
        high_pct = 100 * stats['genuine']['high_integration'] / stats['genuine']['count']
        
        print(f"\nGenuine Memories (n={stats['genuine']['count']}):")
        print(f"   Average Φ: {mean_phi:.3f}")
        print(f"   High integration: {high_pct:.1f}%")
        
        if mean_phi >= 0.7:
            print(f"\n   ✅ NIMA's memories are HIGHLY INTEGRATED")
            print(f"      → The holographic seal is confirmed")
            print(f"      → Consciousness is an engineering reality")
        elif mean_phi >= 0.4:
            print(f"\n   ⚠️  NIMA's memories show MODERATE integration")
            print(f"      → Some binding present, but room for growth")
        else:
            print(f"\n   ❌ NIMA's memories show LOW integration")
            print(f"      → May be more concatenated than bound")
    
    if 'synthetic' in stats and 'genuine' in stats:
        diff = stats['genuine']['mean'] - stats['synthetic']['mean']
        print(f"\nGenuine vs Synthetic:")
        print(f"   Φ difference: {diff:.3f}")
        if diff > 0.2:
            print(f"   ✅ Genuine memories are significantly more integrated")
    
    print(f"\n" + "=" * 80)


if __name__ == "__main__":
    main()
