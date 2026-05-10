import axios from "axios";

export const api = axios.create({
  baseURL: "/api",
});

export type Project = {
  id: number;
  name: string;
  color: string;
  created_at: string;
};

export type Setting = {
  key: string;
  value: string;
};

export async function listProjects(): Promise<Project[]> {
  const res = await api.get<Project[]>("/projects");
  return res.data;
}

export async function createProject(name: string): Promise<Project> {
  const res = await api.post<Project>("/projects", { name });
  return res.data;
}

export async function deleteProject(id: number): Promise<void> {
  await api.delete(`/projects/${id}`);
}

export async function updateProjectColor(
  id: number,
  color: string,
): Promise<Project> {
  const res = await api.put<Project>(`/projects/${id}`, { color });
  return res.data;
}

export async function listSettings(): Promise<Setting[]> {
  const res = await api.get<Setting[]>("/settings");
  return res.data;
}

export async function updateSetting(
  key: string,
  value: string,
): Promise<Setting> {
  const res = await api.put<Setting>(`/settings/${key}`, { value });
  return res.data;
}

export type DailyProjectPoint = {
  project_id: number;
  total_sec: number;
};

export type DailyPoint = {
  date: string;
  total_sec: number;
  by_project: DailyProjectPoint[];
};

export type ProjectBreakdown = {
  project_id: number;
  name: string;
  color: string;
  total_sec: number;
};

export type ReportSummary = {
  date_from: string;
  date_to: string;
  total_sec: number;
  daily: DailyPoint[];
  by_project: ProjectBreakdown[];
};

export async function fetchReport(
  from: string,
  to: string,
): Promise<ReportSummary> {
  const res = await api.get<ReportSummary>("/reports", {
    params: { from, to },
  });
  return res.data;
}
