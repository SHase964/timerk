import axios from "axios";

import type { components } from "./schema";

export const api = axios.create({
  baseURL: "/api",
});

export type Project = components["schemas"]["ProjectRead"];
export type Setting = components["schemas"]["SettingRead"];
export type DailyProjectPoint = components["schemas"]["DailyProjectPoint"];
export type DailyPoint = components["schemas"]["DailyPoint"];
export type ProjectBreakdown = components["schemas"]["ProjectBreakdown"];
export type ReportSummary = components["schemas"]["ReportSummary"];

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

export async function fetchReport(
  from: string,
  to: string,
): Promise<ReportSummary> {
  const res = await api.get<ReportSummary>("/reports", {
    params: { from, to },
  });
  return res.data;
}
