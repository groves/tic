from datetime import datetime, timedelta

from nose.tools import assert_raises, eq_

from datasets import ActivityData, make_data, get_base
from tic.model import Activity

data = make_data()

def teardown():
    data.teardown()

def test_hour_duration():
    act = get_base()
    durations = [(timedelta(hours=1), ['   1 hour', '1 hours', '0 hours 60 minute ', '60 minutes',
        '  1  h   ', '1h    0m   ', '1h 0 minute', '60m', '0h     60m'])]
    for result, entries in durations:
        stop = act.start + result
        for entry in entries:
            act.duration = entry
            eq_(stop, act.stop, '%s should result in %s, not %s' % (entry, stop, act.stop))

def test_bad_durations():
    act = get_base()
    for entry in ['1 ours', '12', '1q2 hour']:
        assert_raises(ValueError, setattr, act, 'duration', entry)

def test_single_letter_difference():
    act = get_base()
    matches = Activity.locate(act.start, datetime.now(), ['Working'])
    eq_(1, len(matches))
    eq_(act.key(), iter(matches).next().key())

def test_tag():
    act = get_base()
    matches = Activity.locate(tags=['tic'])
    eq_(3, len(matches))
    assert act.key() in set((m.key() for m in matches))

def test_case_insensitive():
    act = get_base()
    matches = Activity.locate(act.start, datetime.now(), ['working'])
    eq_(1, len(matches))

def test_same_ending():
    act = get_base()
    matches = Activity.locate(act.start, datetime.now(), ['on tic'])
    eq_(2, len(matches))
    assert act.key() in set((m.key() for m in matches))

def test_earlier_start():
    act = get_base()
    matches = Activity.locate(act.start - timedelta(days=2), datetime.now(), ['Working on tic'])
    eq_(2, len(matches))
    assert act.key() in set((m.key() for m in matches))

def test_multiple_names():
    act = get_base()
    matches = Activity.locate(act.start, datetime.now(), ["Working", "Horking"])
    eq_(2, len(matches))


# In this section, we have tests that we really wish wouldn't fucking pass
def test_single_letter_missing():
    act = get_base()
    matches = Activity.locate(act.start, datetime.now(), ['orking'])
    eq_(0, len(matches))


