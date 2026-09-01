export const range = (startOrLength: number, end?: number): number[] => {
  if (end === undefined) {
    return Array.from({ length: startOrLength }, (_, i) => i)
  } else {
    return Array.from({ length: end - startOrLength }, (_, i) => i + startOrLength)
  }
}