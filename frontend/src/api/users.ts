import client from "./client";

export interface User {
  id: number;
  username: string;
  email: string;
  created_at?: string;
}

export const usersApi = {
  search: (q: string) => client.get<User[]>("/users/search", { params: { q } }),
};
