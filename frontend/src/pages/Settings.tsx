import { useEffect, useState, type FormEvent } from "react";
import {
  Box,
  Button,
  Container,
  FormControlLabel,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Stack,
  Switch,
  TextField,
  Typography,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
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
    setProjects((prev) => prev.map((p) => (p.id === id ? { ...p, color } : p)));
    await updateProjectColor(id, color);
  }

  async function handleShowSecondsChange(value: boolean) {
    setShowSeconds(value);
    await updateSetting("show_seconds", value ? "true" : "false");
  }

  if (loading) return <div style={{ padding: 24 }}>Loading...</div>;
  if (error)
    return <div style={{ padding: 24, color: "crimson" }}>エラー: {error}</div>;

  return (
    <Box sx={{ py: 3 }}>
      <Container maxWidth="sm">
        <Typography
          variant="h6"
          component="h1"
          gutterBottom
          sx={{ textAlign: "left", fontWeight: 700 }}
        >
          設定
        </Typography>
      </Container>

      <Stack spacing={4} sx={{ mt: 2 }}>
        <Box component="section">
          <Container maxWidth="sm">
            <Typography
              variant="subtitle2"
              component="h2"
              color="text.secondary"
              sx={{ mb: 1, textAlign: "left", fontWeight: 600 }}
            >
              プロジェクト管理
            </Typography>
            <Stack
              component="form"
              direction="row"
              spacing={1}
              onSubmit={handleAdd}
              sx={{ mb: 2 }}
            >
              <TextField
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="新しい PJ 名"
                size="small"
                fullWidth
              />
              <Button
                type="submit"
                variant="contained"
                disabled={!newName.trim()}
              >
                追加
              </Button>
            </Stack>
            {projects.length === 0 ? (
              <Typography color="text.secondary">
                プロジェクトがありません
              </Typography>
            ) : (
              <List disablePadding>
                {projects.map((p) => (
                  <ListItem
                    key={p.id}
                    divider
                    disableGutters
                    secondaryAction={
                      <IconButton
                        edge="end"
                        aria-label="削除"
                        onClick={() => handleDelete(p.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    }
                  >
                    <input
                      type="color"
                      value={p.color}
                      onChange={(e) =>
                        handleColorChange(p.id, e.target.value)
                      }
                      style={{
                        width: 28,
                        height: 24,
                        padding: 0,
                        border: "1px solid #ccc",
                        borderRadius: 4,
                        cursor: "pointer",
                        marginRight: 12,
                      }}
                      title="色を変更"
                    />
                    <ListItemText primary={p.name} />
                  </ListItem>
                ))}
              </List>
            )}
          </Container>
        </Box>

        <Box component="section">
          <Container maxWidth="sm">
            <Typography
              variant="subtitle2"
              component="h2"
              color="text.secondary"
              sx={{ mb: 1, textAlign: "left", fontWeight: 600 }}
            >
              タイマー表示
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={showSeconds}
                  onChange={(e) => handleShowSecondsChange(e.target.checked)}
                />
              }
              label="秒まで表示する (例: 00:42:30)"
              labelPlacement="start"
              sx={{
                ml: 0,
                width: "100%",
                justifyContent: "space-between",
              }}
            />
          </Container>
        </Box>
      </Stack>
    </Box>
  );
}
