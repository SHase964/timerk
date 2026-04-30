import { useEffect, useState, type FormEvent } from "react";
import {
  createProject,
  deleteProject,
  listProjects,
  listSettings,
  updateSetting,
  type Project,
} from "../api/client";

export function Settings() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [newName, setNewName] = useState("");
  const [timerUnit, setTimerUnit] = useState("min");
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
      const unit =
        settingList.find((s) => s.key === "timer_unit")?.value ?? "min";
      setTimerUnit(unit);
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

  async function handleUnitChange(value: string) {
    setTimerUnit(value);
    await updateSetting("timer_unit", value);
  }

  if (loading) return <div style={{ padding: 24 }}>Loading...</div>;
  if (error)
    return (
      <div style={{ padding: 24, color: "crimson" }}>
        エラー: {error}
      </div>
    );

  return (
    <div style={{ padding: 24, maxWidth: 560, margin: "0 auto" }}>
      <h1>⚙️ 設定</h1>

      <section style={{ marginBottom: 32 }}>
        <h2>プロジェクト管理</h2>
        <form onSubmit={handleAdd} style={{ display: "flex", gap: 8, marginBottom: 16 }}>
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
                <span>{p.name}</span>
                <button onClick={() => handleDelete(p.id)}>削除</button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2>タイマー表示単位</h2>
        <label style={{ display: "block", marginBottom: 8 }}>
          <input
            type="radio"
            name="unit"
            value="min"
            checked={timerUnit === "min"}
            onChange={() => handleUnitChange("min")}
          />{" "}
          分 (例: 00:42)
        </label>
        <label style={{ display: "block" }}>
          <input
            type="radio"
            name="unit"
            value="sec"
            checked={timerUnit === "sec"}
            onChange={() => handleUnitChange("sec")}
          />{" "}
          秒 (例: 00:42:30)
        </label>
      </section>
    </div>
  );
}
