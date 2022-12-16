from coffee_roulette import utils


def test_get_meeting_times():
    import datetime as dt

    assert utils.get_meeting_times([[9, 10]], spacing=30) == [
        dt.timedelta(seconds=32400),
        dt.timedelta(seconds=34200),
    ]
    assert utils.get_meeting_times(
        [[900, 1000], [1430, 1630]], spacing=50
    ) == [
        dt.timedelta(seconds=32400),
        dt.timedelta(seconds=35400),
        dt.timedelta(seconds=52200),
        dt.timedelta(seconds=55200),
        dt.timedelta(seconds=58200),
    ]
