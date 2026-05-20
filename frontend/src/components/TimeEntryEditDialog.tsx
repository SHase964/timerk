import { useState } from "react";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  Typography,
} from "@mui/material";
import { DateTimePicker } from "@mui/x-date-pickers/DateTimePicker";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { ja } from "date-fns/locale";
import {
  deleteTimeEntry,
  updateTimeEntry,
  type TimeEntry,
} from "../api/client";

// Date を「タイムゾーン無しのローカルISO文字列」に変換する。
// toISOString() は UTC に変換してしまい時刻がズレるため使わない。
function toLocalISOString(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` +
    `T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
  );
}

export function TimeEntryEditDialog({
  entry,
  onClose,
  onSaved,
}: {
  entry: TimeEntry | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  if (!entry) return null;
  // entry が変わるたびに key で再マウントし、stateを初期化し直す。
  return (
    <EditDialogContent
      key={entry.id}
      entry={entry}
      onClose={onClose}
      onSaved={onSaved}
    />
  );
}

function EditDialogContent({
  entry,
  onClose,
  onSaved,
}: {
  entry: TimeEntry;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [started, setStarted] = useState<Date | null>(
    () => new Date(entry.started_at),
  );
  const [stopped, setStopped] = useState<Date | null>(() =>
    entry.stopped_at ? new Date(entry.stopped_at) : null,
  );
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSave() {
    if (!started) {
      setError("開始時刻を入力してください");
      return;
    }
    if (stopped && started >= stopped) {
      setError("開始時刻は終了時刻より前にしてください");
      return;
    }
    setBusy(true);
    try {
      await updateTimeEntry(entry.id, {
        started_at: toLocalISOString(started),
        stopped_at: stopped ? toLocalISOString(stopped) : null,
      });
      onSaved();
      onClose();
    } catch {
      setError("保存に失敗しました");
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete() {
    setBusy(true);
    try {
      await deleteTimeEntry(entry.id);
      onSaved();
      onClose();
    } catch {
      setError("削除に失敗しました");
    } finally {
      setBusy(false);
    }
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ja}>
      <Dialog open onClose={onClose} fullWidth maxWidth="xs">
        <DialogTitle>記録を編集</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            <DateTimePicker
              label="開始"
              value={started}
              onChange={setStarted}
              ampm={false}
              minutesStep={1}
              format="yyyy/MM/dd HH:mm"
            />
            <DateTimePicker
              label="終了"
              value={stopped}
              onChange={setStopped}
              ampm={false}
              minutesStep={1}
              format="yyyy/MM/dd HH:mm"
            />
            {error && (
              <Typography color="error" variant="body2">
                {error}
              </Typography>
            )}
          </Stack>
        </DialogContent>
        <DialogActions sx={{ justifyContent: "space-between", px: 3, pb: 2 }}>
          <Button color="error" onClick={handleDelete} disabled={busy}>
            削除
          </Button>
          <Box>
            <Button onClick={onClose} disabled={busy}>
              キャンセル
            </Button>
            <Button variant="contained" onClick={handleSave} disabled={busy}>
              保存
            </Button>
          </Box>
        </DialogActions>
      </Dialog>
    </LocalizationProvider>
  );
}
