"""Deterministic non-priority display rotation.

When live_games is true, any eligible live sport takes precedence over
clock, weather, news, countdown and plugin screens. The caller handles
individual game selection and rotation.
"""
def choose_screen(position, *, has_game, clock, weather, news, interval=5, countdown=False, live_games=False, plugins=()):
    """Select a screen type, not an individual game.

    interval remains accepted for backward compatibility; screen types
    currently receive equal rotation slots rather than interval weighting.
    """
    if live_games:
        return 'game'
    options=[]
    if clock: options.append('clock')
    if weather: options.append('weather')
    if news: options.append('news')
    if countdown: options.append('countdown')
    if has_game: options.append('game')
    # Plugin screens are global ULS rotation participants, not MLB pages.
    # Callers supply only eligible, enabled plugin IDs.
    options.extend('plugin:' + plugin_id for plugin_id in plugins)
    if not options: return 'splash'
    # Rotate all available content equally; no source can starve another.
    return options[int(position)%len(options)]
