import client from "./client";

export interface QueryResponse {
  answer: string;
  sources: { content: string }[];
}

export const ragApi = {
  query: (kbId: number, question: string, topK = 5) =>
    client.post<QueryResponse>(`/knowledge-bases/${kbId}/query`, {
      question,
      top_k: topK,
    }),

  /** 多知识库查询，kb_ids 为空表示全部知识库 */
  batchQuery: (question: string, kbIds: number[] = [], topK = 5) =>
    client.post<QueryResponse>("/knowledge-bases/query", {
      question,
      top_k: topK,
      kb_ids: kbIds,
    }),
};
