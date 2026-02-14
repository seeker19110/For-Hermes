const fs = require('fs');

/**
 * Analyzes the HTN domain and problem structure for potential issues.
 * @param {Object} domain The HTN domain definition
 * @param {Object} problem The HTN problem definition
 * @returns {string} Markdown report
 */
function analyze(domain, problem) {
  const stats = {
    operators: Object.keys(domain.operators || {}).length,
    methods: 0,
    tasks_with_methods: Object.keys(domain.methods || {}).length,
    cycles: [],
    missing: new Set(),
    unreachable: [],
    roots: problem.tasks || problem.goal || []
  };

  // Build Adjacency Graph: Task -> Set(Subtasks)
  const graph = {};
  const allDefined = new Set([
    ...Object.keys(domain.operators || {}),
    ...Object.keys(domain.methods || {})
  ]);

  if (domain.methods) {
    for (const [taskName, methodList] of Object.entries(domain.methods)) {
      stats.methods += methodList.length;
      if (!graph[taskName]) graph[taskName] = new Set();
      
      for (const method of methodList) {
        if (method.subtasks) {
          for (const subtask of method.subtasks) {
            graph[taskName].add(subtask);
            if (!allDefined.has(subtask)) {
              stats.missing.add(subtask);
            }
          }
        }
      }
    }
  }

  // Cycle Detection (DFS)
  const visited = new Set();
  const recursionStack = new Set();

  function detectCycle(node, path) {
    visited.add(node);
    recursionStack.add(node);

    if (graph[node]) {
      for (const neighbor of graph[node]) {
        if (!visited.has(neighbor)) {
          detectCycle(neighbor, [...path, neighbor]);
        } else if (recursionStack.has(neighbor)) {
          // Cycle found!
          const cycle = [...path, neighbor];
          // Simple dedup: check if equivalent cycle exists
          const cycleStr = cycle.join('->');
          if (!stats.cycles.some(c => c.join('->') === cycleStr)) {
             stats.cycles.push(cycle);
          }
        }
      }
    }

    recursionStack.delete(node);
  }

  // Check from roots first
  for (const root of stats.roots) {
    if (!visited.has(root)) {
      detectCycle(root, [root]);
    }
  }
  // Check remaining disconnected components
  for (const node of allDefined) {
    if (!visited.has(node)) {
      detectCycle(node, [node]);
    }
  }

  // Unreachable Code Detection
  const reachable = new Set();
  function markReachable(node) {
    if (reachable.has(node)) return;
    reachable.add(node);
    if (graph[node]) {
      for (const neighbor of graph[node]) {
        markReachable(neighbor);
      }
    }
  }

  for (const root of stats.roots) {
    if (allDefined.has(root)) {
        markReachable(root);
    } else {
        stats.missing.add(root);
    }
  }

  for (const task of allDefined) {
    if (!reachable.has(task)) {
      stats.unreachable.push(task);
    }
  }

  // Generate Report
  let report = `# HTN Domain Analysis Report\n\n`;
  report += `## Summary\n`;
  report += `- **Operators**: ${stats.operators}\n`;
  report += `- **Compound Tasks**: ${stats.tasks_with_methods} (Total Methods: ${stats.methods})\n`;
  report += `- **Problem Roots**: ${stats.roots.join(', ')}\n`;
  
  if (stats.cycles.length > 0) {
    report += `\n## ⚠️ Recursion Cycles Detected (Potential Loops)\n`;
    report += `> Recursion is allowed in HTN but infinite loops without base cases will crash the planner.\n\n`;
    stats.cycles.forEach(c => {
      report += `- \`${c.join(' -> ')}\`\n`;
    });
  } else {
    report += `\n## ✅ Recursion Check\n- No cycles detected (DAG structure).\n`;
  }

  if (stats.missing.size > 0) {
    report += `\n## ❌ Missing Definitions\n`;
    report += `> Tasks referenced in subtasks/goals but not defined in domain.\n\n`;
    stats.missing.forEach(t => report += `- \`${t}\`\n`);
  }

  if (stats.unreachable.length > 0) {
    report += `\n## 👻 Unreachable Tasks (Dead Code)\n`;
    report += `> Tasks defined but never used from problem roots.\n\n`;
    stats.unreachable.forEach(t => report += `- \`${t}\`\n`);
  } else {
    report += `\n## ✅ Reachability\n- All defined tasks are reachable.\n`;
  }

  return report;
}

module.exports = { analyze };
