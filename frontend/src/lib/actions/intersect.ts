export function intersect(node: HTMLElement, { threshold = 0.1, rootMargin = '0px', onEnter }: { threshold?: number, rootMargin?: string, onEnter?: () => void } = {}) {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    if (onEnter) onEnter();
                    observer.unobserve(node); // Only trigger once
                }
            });
        },
        { threshold, rootMargin }
    );

    observer.observe(node);

    return {
        destroy() {
            observer.unobserve(node);
        }
    };
}
