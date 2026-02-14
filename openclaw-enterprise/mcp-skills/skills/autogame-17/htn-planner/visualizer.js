const fs = require('fs');

function visualize(domain, problem) {
  let mermaid = 'graph TD\n';
  const rootTasks = problem.goal || problem.tasks || [];

  if (!rootTasks || rootTasks.length === 0) {
    return 'graph TD\n  Error[No goal/tasks in problem]';
  }

  let nodeIdCounter = 0;
  function getNodeId(prefix) {
    nodeIdCounter++;
    return `${prefix}_${nodeIdCounter}`;
  }

  // To avoid infinite loops in recursive structures, track visited nodes?
  // HTN can be recursive. We need a depth limit or visited set.
  // For visualization, we can just expand to a certain depth.
  const MAX_DEPTH = 10;
  
  function traverse(taskName, parentId, depth = 0) {
    if (depth > MAX_DEPTH) {
      const limitId = getNodeId('limit');
      mermaid += `  ${parentId} -.-> ${limitId}[...]\n`;
      return;
    }

    // Check if it's an operator (primitive)
    const operator = domain.operators ? domain.operators[taskName] : null;
    if (operator) {
      const opId = getNodeId('op');
      mermaid += `  ${parentId} --> ${opId}[${taskName}]\n`;
      mermaid += `  style ${opId} fill:#f9f,stroke:#333,stroke-width:2px\n`;
      return;
    }

    // Check if it's a compound task (method)
    const methods = domain.methods ? domain.methods[taskName] : null;
    if (methods) {
      const taskId = getNodeId('task');
      mermaid += `  ${parentId} --> ${taskId}((${taskName}))\n`;
      
      methods.forEach((method, idx) => {
        const methodId = getNodeId(`method_${idx}`);
        // Add method label/preconditions if useful
        const label = method.name || `Method ${idx+1}`;
        mermaid += `  ${taskId} -.-> ${methodId}{${label}}\n`;
        
        if (method.subtasks) {
          method.subtasks.forEach(sub => traverse(sub, methodId, depth + 1));
        }
      });
      return;
    }

    // Unknown task
    const unknownId = getNodeId('unknown');
    mermaid += `  ${parentId} --> ${unknownId}[${taskName}?]\n`;
    mermaid += `  style ${unknownId} fill:#ccc,stroke-dasharray: 5 5\n`;
  }

  const startId = getNodeId('Root');
  mermaid += `  ${startId}[Start]\n`;

  rootTasks.forEach(t => traverse(t, startId));

  return mermaid;
}

module.exports = { visualize };
