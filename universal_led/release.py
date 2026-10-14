"""Single source of truth for the current development preview label."""
PREVIEW = "21.6"
STAGE = 15

def display_version():
    return f"Preview {PREVIEW} · Stage {STAGE}"
