/**
 * Независимая минимальная шина событий для собственного Bedrock Add-On.
 * Чистый JavaScript без Minecraft API — удобно тестировать отдельно.
 */
export class EventBus {
  #listeners = new Map();
  #nextId = 1;

  on(eventName, handler, { priority = 0, once = false } = {}) {
    if (typeof eventName !== "string" || !eventName) {
      throw new TypeError("eventName must be a non-empty string");
    }
    if (typeof handler !== "function") {
      throw new TypeError("handler must be a function");
    }

    const listener = {
      id: this.#nextId++,
      handler,
      priority: Number.isFinite(priority) ? priority : 0,
      once: Boolean(once),
      active: true,
    };

    const bucket = this.#listeners.get(eventName) ?? [];
    bucket.push(listener);
    bucket.sort((a, b) => b.priority - a.priority || a.id - b.id);
    this.#listeners.set(eventName, bucket);

    return () => this.off(eventName, listener.id);
  }

  off(eventName, listenerId) {
    const bucket = this.#listeners.get(eventName);
    if (!bucket) return false;
    const listener = bucket.find((item) => item.id === listenerId);
    if (!listener) return false;

    listener.active = false;
    const remaining = bucket.filter((item) => item.active);
    if (remaining.length) this.#listeners.set(eventName, remaining);
    else this.#listeners.delete(eventName);
    return true;
  }

  emit(eventName, payload) {
    const snapshot = [...(this.#listeners.get(eventName) ?? [])];
    const errors = [];

    for (const listener of snapshot) {
      if (!listener.active) continue;
      if (listener.once) this.off(eventName, listener.id);
      try {
        listener.handler(payload);
      } catch (error) {
        errors.push({ eventName, listenerId: listener.id, error });
      }
    }
    return errors;
  }

  clear(eventName) {
    if (eventName === undefined) this.#listeners.clear();
    else this.#listeners.delete(eventName);
  }

  listenerCount(eventName) {
    return (this.#listeners.get(eventName) ?? []).filter((item) => item.active).length;
  }
}
