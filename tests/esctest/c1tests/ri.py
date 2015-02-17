from esc import NUL
import escc1
import esccsi
import escio
from escutil import AssertEQ, AssertScreenCharsInRectEqual, GetCursorPosition, GetScreenSize, knownBug
from esctypes import Point, Rect

class RITests(object):
  def test_RI_Basic(self):
    """Reverse index moves the cursor up one line."""
    esccsi.CUP(Point(5, 3))
    escc1.RI()
    position = GetCursorPosition()
    AssertEQ(position.x(), 5)
    AssertEQ(position.y(), 2)

  def test_RI_Scrolls(self):
    """Reverse index scrolls when it hits the top."""
    # Put a and b on the last two lines.
    esccsi.CUP(Point(2, 1))
    escio.Write("a")
    esccsi.CUP(Point(2, 2))
    escio.Write("b")

    # Move to second line.
    esccsi.CUP(Point(2, 2))

    # Move up, ensure no scroll yet.
    escc1.RI()
    AssertEQ(GetCursorPosition().y(), 1)
    AssertScreenCharsInRectEqual(Rect(2, 1, 2, 3), [ "a", "b", NUL ])

    # Move up, ensure scroll.
    escc1.RI()
    AssertEQ(GetCursorPosition().y(), 1)
    AssertScreenCharsInRectEqual(Rect(2, 1, 2, 3), [ NUL, "a", "b" ])

  def test_RI_ScrollsInTopBottomRegionStartingBelow(self):
    """Reverse index scrolls when it hits the top region (starting below bottom)."""
    esccsi.DECSTBM(4, 5)
    esccsi.CUP(Point(2, 4))
    escio.Write("x")

    esccsi.CUP(Point(2, 6))
    escc1.RI()  # To 5
    escc1.RI()  # To 4
    escc1.RI()  # Stay at 4 and scroll x down one line
    AssertEQ(GetCursorPosition(), Point(2, 4))
    AssertScreenCharsInRectEqual(Rect(2, 4, 2, 5), [ NUL, "x" ])

  def test_RI_ScrollsInTopBottomRegionStartingWithin(self):
    """Reverse index scrolls when it hits the top (starting within region)."""
    esccsi.DECSTBM(4, 5)
    esccsi.CUP(Point(2, 4))
    escio.Write("x")

    esccsi.CUP(Point(2, 5))
    escc1.RI()  # To 4
    escc1.RI()  # Stay at 4 and scroll x down one line
    AssertEQ(GetCursorPosition(), Point(2, 4))
    AssertScreenCharsInRectEqual(Rect(2, 4, 2, 5), [ NUL, "x" ])

  @knownBug(terminal="iTerm2",
            reason="iTerm2 improperly scrolls when the cursor is outside the left-right region.")
  def test_RI_MovesDoesNotScrollOutsideLeftRight(self):
    """Cursor moves down but won't scroll when outside left-right region."""
    esccsi.DECSTBM(2, 5)
    esccsi.DECSET(esccsi.DECLRMM)
    esccsi.DECSLRM(2, 5)
    esccsi.CUP(Point(3, 5))
    escio.Write("x")

    # Move past bottom margin but to the right of the left-right region
    esccsi.CUP(Point(6, 2))
    escc1.RI()
    # Cursor won't pass bottom or scroll.
    AssertEQ(GetCursorPosition(), Point(6, 2))
    AssertScreenCharsInRectEqual(Rect(3, 5, 3, 5), [ "x" ])

    # Try to move past the top of the screen but to the right of the left-right region
    esccsi.CUP(Point(6, 1))
    escc1.RI()
    AssertEQ(GetCursorPosition(), Point(6, 1))
    AssertScreenCharsInRectEqual(Rect(3, 5, 3, 5), [ "x" ])

    # Move past top margin but to the left of the left-right region
    esccsi.CUP(Point(1, 2))
    escc1.RI()
    AssertEQ(GetCursorPosition(), Point(1, 2))
    AssertScreenCharsInRectEqual(Rect(3, 5, 3, 5), [ "x" ])

    # Try to move past the top of the screen but to the left of the left-right region
    esccsi.CUP(Point(1, 1))
    escc1.RI()
    AssertEQ(GetCursorPosition(), Point(1, 1))
    AssertScreenCharsInRectEqual(Rect(3, 5, 3, 5), [ "x" ])

  def test_RI_StopsAtTopLineWhenBegunAboveScrollRegion(self):
    """When the cursor starts above the scroll region, reverse index moves it
    up to the top of the screen but won't scroll."""
    # Set a scroll region. This must be done first because DECSTBM moves the
    # cursor to the origin.
    esccsi.DECSTBM(4, 5)

    # Position the cursor above the scroll region
    esccsi.CUP(Point(1, 3))
    escio.Write("x")

    # Move it up by a lot
    height = GetScreenSize().height()
    for i in xrange(height):
      escc1.RI()

    # Ensure it stopped at the top of the screen
    AssertEQ(GetCursorPosition().y(), 1)

    # Ensure no scroll
    AssertScreenCharsInRectEqual(Rect(1, 3, 1, 3), [ "x" ])
