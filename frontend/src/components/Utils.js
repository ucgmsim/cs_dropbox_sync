export const APIQueryBuilder = (params) => {
  let queryString = "?";

  for (const [param, value] of Object.entries(params)) {
    queryString += `${param}=${value}&`;
  }

  // Remove last character which is an extra & symbol.
  return queryString.slice(0, -1);
};
