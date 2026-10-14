"""Native configuration storage: validated, atomic writes with backups."""
from __future__ import annotations
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from .colors import load_palette, normalize_team_colors, normalize_scoreboard_colors

def read_config(directory: str | Path):
    root=Path(directory)
    teams,scoreboard=load_palette(
        root/'teams.json' if (root/'teams.json').is_file() else None,
        root/'scoreboard.json' if (root/'scoreboard.json').is_file() else None)
    return {'teams':teams,'scoreboard':scoreboard}

def save_config(directory: str | Path, section: str, values: dict):
    if section not in ('teams','scoreboard'):
        raise ValueError('Unknown configuration section')
    normalized=(normalize_team_colors(values) if section=='teams'
                else normalize_scoreboard_colors(values))
    root=Path(directory)
    root.mkdir(parents=True,exist_ok=True)
    path=root/(section+'.json')
    # Only override values are persisted, never rewrite built-in defaults.
    backup_dir=root/'backups'
    backup_dir.mkdir(exist_ok=True)
    if path.exists():
        stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup=backup_dir/(section+'-'+stamp+'.json')
        backup.write_bytes(path.read_bytes())
    fd,tmp=tempfile.mkstemp(prefix='.'+section+'-',suffix='.tmp',dir=root)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            json.dump(normalized,stream,indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return normalized
