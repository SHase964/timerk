import { useState } from "react";
import {
  Box,
  ClickAwayListener,
  Paper,
  Popper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { DayPicker, type DateRange } from "react-day-picker";
import { ja } from "date-fns/locale";
import "react-day-picker/style.css";
import "./DateRangePicker.css";

type Props = {
  from: string;
  to: string;
  onChange: (from: string, to: string) => void;
};

function toISO(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function fromISO(iso: string): Date | undefined {
  if (!iso) return undefined;
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}

function formatJa(iso: string): string {
  return iso.replaceAll("-", "/");
}

export function DateRangePicker({ from, to, onChange }: Props) {
  const [anchorEl, setAnchorEl] = useState<HTMLDivElement | null>(null);
  const [open, setOpen] = useState(false);
  const [tempRange, setTempRange] = useState<DateRange | undefined>(undefined);

  function openPicker() {
    setTempRange({ from: fromISO(from), to: fromISO(to) });
    setOpen(true);
  }

  function handleSelect(selected: DateRange | undefined) {
    setTempRange(selected);
    if (selected?.from && selected?.to) {
      onChange(toISO(selected.from), toISO(selected.to));
    }
  }

  return (
    <ClickAwayListener onClickAway={() => setOpen(false)}>
      <Box ref={setAnchorEl} sx={{ width: "100%" }}>
        <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
          <TextField
            label="開始日"
            value={from ? formatJa(from) : ""}
            onClick={openPicker}
            size="small"
            fullWidth
            slotProps={{
              input: { readOnly: true, sx: { cursor: "pointer" } },
              inputLabel: { shrink: true },
            }}
            placeholder="YYYY/MM/DD"
          />
          <Typography color="text.secondary">~</Typography>
          <TextField
            label="終了日"
            value={to ? formatJa(to) : ""}
            onClick={openPicker}
            size="small"
            fullWidth
            slotProps={{
              input: { readOnly: true, sx: { cursor: "pointer" } },
              inputLabel: { shrink: true },
            }}
            placeholder="YYYY/MM/DD"
          />
        </Stack>
        <Popper
          open={open}
          anchorEl={anchorEl}
          placement="bottom-start"
          sx={{ zIndex: 1300 }}
        >
          <Paper elevation={4} sx={{ mt: 1, p: 1 }}>
            <DayPicker
              mode="range"
              selected={tempRange}
              onSelect={handleSelect}
              locale={ja}
              weekStartsOn={0}
              showOutsideDays
            />
          </Paper>
        </Popper>
      </Box>
    </ClickAwayListener>
  );
}
