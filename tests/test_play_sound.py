from huelloween import hued_wav_file


def test_play_sound_without_hue(mocker):
    """
    This will test the playing of sound without interfacing with the Hue bridge
    Mocked out the Hue bridge objects
    """
    bridge = mocker.Mock()
    light = mocker.Mock()
    hued_wav_file(sound_file='sounds/hammering.wav',
                  bridge=bridge,
                  light=light)
