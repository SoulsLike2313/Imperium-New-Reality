function errorMessage(error) {
  if (error instanceof Error) return error.message;
  if (typeof error === "string") return error;
  try {
    return JSON.stringify(error);
  } catch {
    return "Unknown corridor bridge error";
  }
}

export function createCorridorState() {
  const listeners = new Set();
  let view = Object.freeze({
    snapshot: null,
    busy: false,
    pendingActionId: null,
    error: null,
    lastResult: null,
  });

  function publish(patch) {
    view = Object.freeze({ ...view, ...patch });
    for (const listener of listeners) listener(view);
  }

  return Object.freeze({
    subscribe(listener) {
      listeners.add(listener);
      listener(view);
      return () => listeners.delete(listener);
    },
    startRequest(actionId = null) {
      publish({ busy: true, pendingActionId: actionId, error: null });
    },
    receiveSnapshot(snapshot, lastResult = null) {
      publish({ snapshot, busy: false, pendingActionId: null, error: null, lastResult });
    },
    failRequest(error) {
      publish({ busy: false, pendingActionId: null, error: errorMessage(error) });
    },
  });
}
