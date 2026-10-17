"""Deterministic non-priority display rotation.

A live favorite-team game bypasses this scheduler entirely.
"""
def choose_screen(position, *, has_game, clock, weather, news, interval=5, countdown=False, live_games=False):
    if live_games:
        return 'game'
    options=[]
    if clock: options.append('clock')
    if weather: options.append('weather')
    if news: options.append('news')
    if countdown: options.append('countdown')
    if has_game: options.append('game')
    if not options: return 'splash'
    # Rotate all available content equally; no source can starve another.
    return options[int(position)%len(options)]
