// Simple HTN Planner (DFS)
function plan(domain, problem) {
  const initialState = { ...problem.state };
  const rootTasks = problem.tasks || problem.goal;

  if (!rootTasks) {
    throw new Error('No tasks or goal defined in problem.');
  }

  // Ensure domain structure
  if (!domain.operators) domain.operators = {};
  if (!domain.methods) domain.methods = {};

  const result = decompose(initialState, rootTasks, domain, []);
  if (!result) {
    return { status: 'failed', plan: [] };
  }
  return { status: 'success', plan: result.plan, finalState: result.state };
}

function decompose(state, tasks, domain, planSoFar) {
  if (tasks.length === 0) {
    return { plan: planSoFar, state };
  }

  const taskName = tasks[0];
  const remainingTasks = tasks.slice(1);

  // If task is primitive (operator)
  if (domain.operators && domain.operators[taskName]) {
    const op = domain.operators[taskName];
    if (checkPreconditions(state, op.preconditions)) {
      const newState = applyEffects(state, op.effects);
      const newPlan = [...planSoFar, taskName];
      return decompose(newState, remainingTasks, domain, newPlan);
    }
    return null; // Precondition failed
  }

  // If task is compound (method)
  if (domain.methods && domain.methods[taskName]) {
    const methods = domain.methods[taskName]; // Array of method objects
    for (const method of methods) {
      if (checkPreconditions(state, method.preconditions)) {
        const subtasks = method.subtasks || [];
        const newTasks = [...subtasks, ...remainingTasks];
        const result = decompose(state, newTasks, domain, planSoFar);
        if (result) return result;
      }
    }
    return null; // No applicable method found
  }

  // Task not found
  console.warn(`Task or operator '${taskName}' not found in domain.`);
  return null;
}

function checkPreconditions(state, preconditions) {
  if (!preconditions) return true;
  for (const [key, value] of Object.entries(preconditions)) {
    if (state[key] !== value) return false;
  }
  return true;
}

function applyEffects(state, effects) {
  if (!effects) return state;
  const newState = { ...state };
  for (const [key, value] of Object.entries(effects)) {
    newState[key] = value;
  }
  return newState;
}

function simulate(domain, problem) {
    return plan(domain, problem);
}

module.exports = { plan, simulate };
