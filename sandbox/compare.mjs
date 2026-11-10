const INVALID = Symbol('invalid JSON')
function tokens(value) {
  return String(value).trim().split(/\s+/).filter(Boolean)
}
function parse(value) {
  let s = String(value)
    .trim()
    .replace(/^tensor\(/, '')
    .replace(/,\s*dtype=torch\.\w+\)$/, '')
    .replace(/\)$/, '')
  try {
    return JSON.parse(s)
  } catch {}
  // Legacy tensor repr may use Python literals. Preserve all quoted text.
  const replacements = { None: 'null', True: 'true', False: 'false' }
  let converted = '',
    quote = null,
    escaped = false
  for (let i = 0; i < s.length;) {
    const c = s[i]
    if (quote) {
      converted += c
      i++
      if (escaped) escaped = false
      else if (c === '\\') escaped = true
      else if (c === quote) quote = null
    } else if (c === '"' || c === "'") {
      quote = c
      converted += c
      i++
    } else if (/[A-Za-z_]/.test(c)) {
      const word = s.slice(i).match(/^[A-Za-z_]+/)[0]
      converted += replacements[word] ?? word
      i += word.length
    } else {
      converted += c
      i++
    }
  }
  try {
    return JSON.parse(converted)
  } catch {
    return INVALID
  }
}
function equal(a, b, abs, rel) {
  if (Array.isArray(a) || Array.isArray(b))
    return (
      Array.isArray(a) &&
      Array.isArray(b) &&
      a.length === b.length &&
      a.every((x, i) => equal(x, b[i], abs, rel))
    )
  if (typeof a === 'number' && typeof b === 'number')
    return Number.isFinite(a) && Number.isFinite(b) && Math.abs(a - b) <= abs + rel * Math.abs(b)
  if (a && b && typeof a === 'object' && typeof b === 'object') {
    const keys = Object.keys(a)
    return (
      keys.length === Object.keys(b).length &&
      keys.every((k) => Object.hasOwn(b, k) && equal(a[k], b[k], abs, rel))
    )
  }
  return a === b
}
function balancedBst(value) {
  if (!Array.isArray(value) || value.length > 10000) return null
  if (!value.length || value[0] === null) return value.every((v) => v === null) ? [] : null
  const root = { value: value[0], left: null, right: null },
    nodes = [root]
  let cursor = 1
  for (let q = 0; q < nodes.length; q++) {
    const node = nodes[q]
    if (typeof node.value !== 'number' || !Number.isFinite(node.value)) return null
    for (const side of ['left', 'right']) {
      if (cursor >= value.length) break
      const next = value[cursor++]
      if (next !== null) {
        const child = { value: next, left: null, right: null }
        node[side] = child
        nodes.push(child)
      }
    }
  }
  if (value.slice(cursor).some((v) => v !== null)) return null
  for (let i = nodes.length - 1; i >= 0; i--) {
    const n = nodes[i],
      l = n.left,
      r = n.right
    if (
      (l && l.max >= n.value) ||
      (r && r.min <= n.value) ||
      Math.abs((l?.height || 0) - (r?.height || 0)) > 1
    )
      return null
    n.min = l?.min ?? n.value
    n.max = r?.max ?? n.value
    n.height = 1 + Math.max(l?.height || 0, r?.height || 0)
  }
  return nodes.map((n) => n.value).sort((a, b) => a - b)
}
export function compare(actual, expected, mode = 'tokens', abs = 1e-5, rel = 1e-5) {
  if (mode === 'exact') return String(actual).trimEnd() === String(expected).trimEnd()
  if (mode === 'unordered_tokens')
    return JSON.stringify(tokens(actual).sort()) === JSON.stringify(tokens(expected).sort())
  if (
    mode === 'json' ||
    mode === 'unordered_json' ||
    mode === 'unordered_nested' ||
    mode === 'balanced_bst' ||
    mode === 'float_tokens'
  ) {
    const a = parse(actual),
      b = parse(expected)
    if (a !== INVALID && b !== INVALID) {
      if (mode === 'balanced_bst') {
        const aa = balancedBst(a),
          bb = balancedBst(b)
        return aa !== null && bb !== null && equal(aa, bb, 0, 0)
      }
      if (mode === 'unordered_nested') {
        const norm = (x) =>
          Array.isArray(x)
            ? x
                .map((v) => (Array.isArray(v) ? [...v].sort() : v))
                .sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b)))
            : x
        return JSON.stringify(norm(a)) === JSON.stringify(norm(b))
      }
      if (mode === 'unordered_json')
        return (
          Array.isArray(a) &&
          Array.isArray(b) &&
          a.length === b.length &&
          a.every((x) => {
            const i = b.findIndex((y) => equal(x, y, abs, rel))
            if (i < 0) return false
            b.splice(i, 1)
            return true
          })
        )
      return equal(a, b, mode === 'float_tokens' ? abs : 0, mode === 'float_tokens' ? rel : 0)
    }
    if (mode !== 'float_tokens') return false
    const at = tokens(actual),
      bt = tokens(expected)
    return (
      at.length === bt.length &&
      at.every(
        (x, i) =>
          Number.isFinite(Number(x)) &&
          Number.isFinite(Number(bt[i])) &&
          equal(Number(x), Number(bt[i]), abs, rel),
      )
    )
  }
  return JSON.stringify(tokens(actual)) === JSON.stringify(tokens(expected))
}
