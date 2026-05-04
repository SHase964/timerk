import { useEffect, useState, type FormEvent } from "react";
import {
  createProject,
  deleteProject,
  listProjects,
  listSettings,
  updateProjectColor,
  updateSetting,
  type Project,
} from "../api/client";

export function Settings() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [newName, setNewName] = useState("");
  const [showSeconds, setShowSeconds] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const [projectList, settingList] = await Promise.all([
        listProjects(),
        listSettings(),
      ]);
      setProjects(projectList);
      const value =
        settingList.find((s) => s.key === "show_seconds")?.value ?? "false";
      setShowSeconds(value === "true");
    } catch (e) {
      setError(e instanceof Error ? e.message : "読み込みに失敗しました");
    } finally {
      setLoading(false);
    }
  }

  async function handleAdd(e: FormEvent) {
    e.preventDefault();
    const name = newName.trim();
    if (!name) return;
    await createProject(name);
    setNewName("");
    await loadData();
  }

  async function handleDelete(id: number) {
    if (!confirm("本当に削除しますか？")) return;
    await deleteProject(id);
    await loadData();
  }

  async function handleColorChange(id: number, color: string) {
    setProjects((prev) =>
      prev.map((p) => (p.id === id ? { ...p, color } : p)),
    );
    await updateProjectColor(id, color);
  }

  async function handleShowSecondsChange(value: boolean) {
    setShowSeconds(value);
    await updateSetting("show_seconds", value ? "true" : "false");
  }

  if (loading) return <div style={{ padding: 24 }}>Loading...</div>;
  if (error)
    return (
      <div style={{ padding: 24, color: "crimson" }}>エラー: {error}</div>
    );

  return (
    <div style={{ padding: 24, maxWidth: 560, margin: "0 auto" }}>
      <h1>⚙️ 設定</h1>

      <section style={{ marginBottom: 32 }}>
        <h2>プロジェクト管理</h2>
        <form
          onSubmit={handleAdd}
          style={{ display: "flex", gap: 8, marginBottom: 16 }}
        >
          <input
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="新しい PJ 名"
            style={{ flex: 1, padding: "6px 10px" }}
          />
          <button type="submit" disabled={!newName.trim()}>
            追加
          </button>
        </form>
        {projects.length === 0 ? (
          <p style={{ color: "#888" }}>プロジェクトがありません</p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0 }}>
            {projects.map((p) => (
              <li
                key={p.id}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "8px 12px",
                  borderBottom: "1px solid #eee",
                }}
              >
                <span style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <input
                    type="color"
                    value={p.color}
                    onChange={(e) => handleColorChange(p.id, e.target.value)}
                    style={{
                      width: 28,
                      height: 24,
                      padding: 0,
                      border: "1px solid #ccc",
                      borderRadius: 4,
                      cursor: "pointer",
                    }}
                    title="色を変更"
                  />
                  {p.name}
                </span>
                <button onClick={() => handleDelete(p.id)}>削除</button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2>タイマー表示</h2>
        <label style={{ display: "block" }}>
          <input
            type="checkbox"
            checked={showSeconds}
            onChange={(e) => handleShowSecondsChange(e.target.checked)}
          />{" "}
          秒まで表示する (例: 00:42:30)
        </label>
      </section>
    </div>
  );
}
