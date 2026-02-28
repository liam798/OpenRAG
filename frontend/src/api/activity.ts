import client from "./client";

export interface Activity {
  id: number;
  user_id: number;
  username: string;
  action: string;
  action_label: string;
  knowledge_base_id: number | null;
  knowledge_base_name: string | null;
  knowledge_base_owner?: string | null;
  extra: Record<string, unknown> | null;
  created_at: string;
}

export const activityApi = {
  list: (scope: "all" | "mine" = "all", limit = 50) =>
    client.get<Activity[]>("/activities", { params: { scope, limit } }),
};
