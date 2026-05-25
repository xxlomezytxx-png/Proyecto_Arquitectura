import { authAxios } from "./authClient";

const BFF = import.meta.env.VITE_BFF_URL || "http://localhost:8009";

export interface InsertedPreviewItem {
  row: number;
  isbn: string;
  title: string;
  author?: string;
  source?: string;
  confidence?: string;
}

export interface DuplicatedPreviewItem {
  row: number;
  isbn: string;
  title: string;
  reason?: string;
}

export interface ErrorPreviewItem {
  row: number;
  isbn?: string;
  title?: string;
  error: string | Record<string, unknown>;
}

export interface UploadResult {
  total_rows_processed: number;
  inserted: number;
  duplicated: number;
  errors: number;
  inserted_preview: InsertedPreviewItem[];
  duplicated_preview: DuplicatedPreviewItem[];
  error_preview: ErrorPreviewItem[];
}

export const uploadExcel = async (file: File): Promise<UploadResult> => {
  const form = new FormData();
  form.append("file", file);
  const res = await authAxios.post(`${BFF}/api/admin/enrichment/upload-excel`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

export const getEnrichmentStatus = async () => {
  const res = await authAxios.get(`${BFF}/api/admin/enrichment/status`);
  return res.data;
};
