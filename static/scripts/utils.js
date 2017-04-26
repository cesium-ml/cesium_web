export function objectType(obj) {
  return Object.prototype.toString.call(obj).slice(8, -1);
}

export function contains(array, x) {
  return (array.find(el => (el === x)) !== undefined);
}

export function $try(func) {
  try {
    return func();
  } catch (e) {
    return null;
  }
}

export function reformatDatetime(dtStr) {
  return new Date(dtStr).toString();
}

export function joinObjectValues(obj) {
  let vals = [];
  for (const prop in obj) {
    if (obj.hasOwnProperty(prop)) {
      vals = vals.concat(obj[prop]);
    }
  }
  return [...new Set(vals)];
}
