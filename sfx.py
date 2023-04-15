from utils import MUSIC_DEFAULT_VOLUME, SFX_DEFAULT_VOLUME, SFX_DIR
from pygame import mixer
import os
import random

mixer.init()

sfx_files = os.listdir(SFX_DIR)
sfx = {file[:-4]: mixer.Sound(os.path.join(SFX_DIR, file))
    for file in sfx_files if not file.startswith('bg_music')}

bg_music_tracks = [os.path.join(SFX_DIR, file) for file in sfx_files if file.startswith('bg_music')]
print(bg_music_tracks)

def set_sfx_volume(vol):
    global sfx
    for s_effect in sfx.values():
        s_effect.set_volume(vol)


set_sfx_volume(SFX_DEFAULT_VOLUME)


def play_sfx(name):
    sfx[name].play()


def play_bg_music():
    bg_track = random.choice(bg_music_tracks)
    mixer.music.load(bg_track)
    bg_music_set_vol(MUSIC_DEFAULT_VOLUME)
    mixer.music.play(-1)


def bg_music_set_vol(vol):
    mixer.music.set_volume(vol)


def bg_music_play(play: bool):
    if play:
        mixer.music.unpause()
    else:
        mixer.music.pause()
