export const getToken = () =>
  typeof window !== "undefined" ? localStorage.getItem("access") : null;

export const setTokens = (access: string, refresh: string) => {
  localStorage.setItem("access", access);
  localStorage.setItem("refresh", refresh);
};

export const logout = () => {
  localStorage.clear();
  window.location.href = "/login";
};
