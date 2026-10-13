
## 2024-10-13 - Number Formatting Performance Bottleneck
**Learning:** Calling `Number.prototype.toLocaleString()` with configuration options creates a new `Intl.NumberFormat` instance under the hood every single time it's called. When used in Vue template rendering paths for lists (e.g. `PositionsTable` rendering multiple currency cells per row), this inline instantiation causes significant main thread blocking and slows down component rendering by ~60x compared to a cached formatter.
**Action:** When a specific formatting option is used repeatedly (especially in loops, lists, or reactive templates), extract it to a static `Intl.NumberFormat` instance outside the loop/render function and call `.format(value)` on that cached instance instead of using `.toLocaleString()`.
