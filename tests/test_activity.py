from datetime import timedelta

from nose.tools import assert_raises, eq_

from datasets import ActivityData, make_data
from tic.model import Activity

data = make_data()
act = Activity.all().filter("name =", ActivityData.working_on_tic.name)[0]

def teardown():
    data.teardown()

def test_hour_duration():
    durations = [(timedelta(hours=1), ['   1 hour', '1 hours', '0 hours 60 minute ', '60 minutes',
        '  1  h   ', '1h    0m   ', '1h 0 minute', '60m', '0h     60m'])]
    for result, entries in durations:
        stop = act.start + result
        for entry in entries:
            act.duration = entry
            eq_(stop, act.stop, '%s should result in %s, not %s' % (entry, stop, act.stop))

def test_bad_durations():
    for entry in ['1 ours', '12', '1q2 hour']:
        assert_raises(ValueError, setattr, act, 'duration', entry)
