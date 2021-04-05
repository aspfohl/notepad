from notepad import window, constants

def test_get_title():
    assert window.get_title("foo") == f"foo - {constants.APP_NAME}"
    assert window.get_title() == f"{constants.DEFAULT_UNNAMED_TITLE} - {constants.APP_NAME}"

def test_window_dimension():
    w = window.WindowDimension(height=50, width=100)
    assert w.left_alignment(screen_width=500) == 200.0
    assert w.top_alignment(screen_height=100) == 25.0
    assert w.get_geometry(screen_width=500, screen_height=100) == "100x50+200+25"