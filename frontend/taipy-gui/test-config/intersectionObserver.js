class IntersectionObserver {
    root = null;
    rootMargin = "";
    thresholds = [];

    disconnect() {
      return null;
    }

    observe() {
      return null;
    }

    takeRecords() {
      return [];
    }

    unobserve() {
      return null;
    }
  }
  window.IntersectionObserver = IntersectionObserver;
  global.IntersectionObserver = IntersectionObserver;
