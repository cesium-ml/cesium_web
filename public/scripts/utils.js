export function objectType(obj) {
  return Object.prototype.toString.call(obj).slice(8, -1)
}

export function contains(array, x) {
  return (array.find(el => (el == x)) !== undefined);
}
