import { useEffect, useState } from "react";
import {
  Box,
  Button,
  Container,
  List,
  ListItem,
  ListItemText,
  Stack,
  Typography,
} from "@mui/material";
import { DateRangePicker } from "../components/DateRangePicker";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fetchReport, type ReportSummary } from "../api/client";

function toISO(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function startOfMonth(d = new Date()): Date {
  return new Date(d.getFullYear(), d.getMonth(), 1);
}

function startOfLastMonth(): Date {
  const d = new Date();
  return new Date(d.getFullYear(), d.getMonth() - 1, 1);
}

function endOfLastMonth(): Date {
  const d = new Date();
  return new Date(d.getFullYear(), d.getMonth(), 0);
}

function startOfWeek(d = new Date()): Date {
  const day = d.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  const result = new Date(d);
  result.setDate(d.getDate() + diff);
  return result;
}

function daysAgo(n: number): Date {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d;
}

type Preset = {
  label: string;
  range: () => [string, string];
};

const PRESETS: Preset[] = [
  {
    label: "今日",
    range: () => [toISO(new Date()), toISO(new Date())],
  },
  {
    label: "今週",
    range: () => [toISO(startOfWeek()), toISO(new Date())],
  },
  {
    label: "今月",
    range: () => [toISO(startOfMonth()), toISO(new Date())],
  },
  {
    label: "先月",
    range: () => [toISO(startOfLastMonth()), toISO(endOfLastMonth())],
  },
  {
    label: "直近30日",
    range: () => [toISO(daysAgo(29)), toISO(new Date())],
  },
];

function formatDuration(totalSec: number): string {
  const h = Math.floor(totalSec / 3600);
  const m = Math.floor((totalSec % 3600) / 60);
  if (h === 0) return `${m} 分`;
  return `${h} 時間 ${m} 分`;
}

function formatDurationWithSeconds(totalSec: number): string {
  const h = Math.floor(totalSec / 3600);
  const m = Math.floor((totalSec % 3600) / 60);
  const s = Math.floor(totalSec % 60);
  if (h > 0) return `${h} 時間 ${m} 分 ${s} 秒`;
  if (m > 0) return `${m} 分 ${s} 秒`;
  return `${s} 秒`;
}

export function Report() {
  const initial = PRESETS[2].range(); // 今月
  const [from, setFrom] = useState<string>(initial[0]);
  const [to, setTo] = useState<string>(initial[1]);
  const [data, setData] = useState<ReportSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!from || !to) return;
    let cancelled = false;
    fetchReport(from, to)
      .then((result) => {
        if (cancelled) return;
        setData(result);
        setError(null);
        setLoading(false);
      })
      .catch((e) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : "読み込みに失敗しました");
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [from, to]);

  function applyPreset(preset: Preset) {
    const [f, t] = preset.range();
    setFrom(f);
    setTo(t);
  }

  const dailyChartData = (data?.daily ?? []).map((d) => ({
    date: d.date.slice(5),
    minutes: Math.round(d.total_sec / 60),
  }));

  return (
    <Box sx={{ py: 3 }}>
      <Container maxWidth="sm">
        <Typography
          variant="h6"
          component="h1"
          gutterBottom
          sx={{ textAlign: "left", fontWeight: 700 }}
        >
          レポート
        </Typography>
      </Container>

      <Stack spacing={3} sx={{ mt: 2 }}>
        <Box component="section">
          <Container maxWidth="sm">
            <Typography
              variant="subtitle2"
              component="h2"
              color="text.secondary"
              sx={{ mb: 1, textAlign: "left", fontWeight: 600 }}
            >
              期間
            </Typography>
            <Stack
              direction="row"
              spacing={1}
              sx={{ mb: 1.5, flexWrap: "wrap" }}
            >
              {PRESETS.map((p) => (
                <Button
                  key={p.label}
                  size="small"
                  variant="outlined"
                  onClick={() => applyPreset(p)}
                >
                  {p.label}
                </Button>
              ))}
            </Stack>
            <DateRangePicker
              from={from}
              to={to}
              onChange={(f, t) => {
                setFrom(f);
                setTo(t);
              }}
            />
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
              合計
            </Typography>
            {loading ? (
              <Typography>Loading...</Typography>
            ) : error ? (
              <Typography color="error">エラー: {error}</Typography>
            ) : (
              <>
                <Typography
                  variant="h3"
                  sx={{ fontWeight: 700, mb: 2, textAlign: "left" }}
                >
                  {formatDurationWithSeconds(data?.total_sec ?? 0)}
                </Typography>
                {dailyChartData.length === 0 ? (
                  <Typography color="text.secondary">
                    記録がありません
                  </Typography>
                ) : (
                  <Box sx={{ width: "100%", height: 240 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={dailyChartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                        <YAxis tick={{ fontSize: 11 }} />
                        <Tooltip
                          formatter={(value) => [`${value} 分`, ""]}
                          labelStyle={{ color: "#555" }}
                        />
                        <Bar
                          dataKey="minutes"
                          fill="#007AFF"
                          radius={[3, 3, 0, 0]}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                )}
              </>
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
              プロジェクト別
            </Typography>
            {!data || data.by_project.length === 0 ? (
              <Typography color="text.secondary">データがありません</Typography>
            ) : (
              <List disablePadding>
                {data.by_project.map((p) => (
                  <ListItem key={p.project_id} divider disableGutters>
                    <Box
                      sx={{
                        width: 12,
                        height: 12,
                        borderRadius: "50%",
                        bgcolor: p.color,
                        mr: 1.5,
                        flexShrink: 0,
                      }}
                    />
                    <ListItemText
                      primary={p.name}
                      secondary={formatDuration(p.total_sec)}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Container>
        </Box>

      </Stack>
    </Box>
  );
}
