from hypothesis import given, settings, strategies as st
from processor import parse_walk_schedule, compute_pace_per_pet, lookup_temperament_surcharge


# Inputs that look roughly like real ones, so Hypothesis also reaches the deeper bugs
schedule_like = st.builds(
    lambda a, b, c: f"{a}-{b}-{c}",
    st.text(max_size=5), st.text(max_size=5), st.text(max_size=5),
)
metrics_like = st.builds(
    lambda a, b: f"{a}/{b}",
    st.one_of(st.integers(), st.floats(), st.text(max_size=5)).map(str),
    st.one_of(st.integers(), st.floats(), st.text(max_size=5)).map(str),
)


@settings(max_examples=300)
@given(st.text() | st.none() | schedule_like)
def test_parse_walk_schedule_no_crash(s):
    try:
        parse_walk_schedule(s)
    except Exception as e:
        assert False, f"parse_walk_schedule crashed on {s!r} with: {type(e).__name__}: {e}"


@settings(max_examples=300)
@given(st.text() | st.none() | metrics_like)
def test_compute_pace_per_pet_safe(s):
    try:
        compute_pace_per_pet(s)
    except Exception as e:
        assert False, f"compute_pace_per_pet crashed on {s!r} with: {type(e).__name__}: {e}"


@settings(max_examples=300)
@given(st.text() | st.none())
def test_lookup_temperament_surcharge_safe(s):
    try:
        lookup_temperament_surcharge(s)
    except Exception as e:
        assert False, f"lookup_temperament_surcharge crashed on {s!r} with: {type(e).__name__}: {e}"
