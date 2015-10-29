
I first started coding this by implementing code to read in the field
file and represent it as a list of lists. I implemented movement and
"firing" instructions. At this point it was fairly monolithic so I
abstracted out classes for Ship, Field, Scorer.

I then implemented all function except for sizing the view so that it
would be no larger than necessary. I then abstracted out a View class
to print the grid as specified.

I count the number of initial mines and decrement for each volley
which destroys mines.

I check for hitting a mine (a mine is at the ship's X,Y coordinate and
has a Z 'depth' of 0).

I check for missing any mines (no mine is at the ship's X,Y coordinate
but there are mines with a Z 'depth' of 0).

I check for all mines cleared (field.nr_mines == 0) but remaining
script instructions as well as script completed but mines remain.

About moving the ship: The specifications note that moving "North"
increments the Y-coordinate and moving "South" decrements it.
Representing the field as a list of list this ordering is reversed.

About sizing the view: Shrinking the view to the smallest size is done
in two steps - shrink vertically and shrink horizontally.

The general idea is the same in each case - if the outer most rows or
columns are empty of mines, ignore them and recurively check the
remaining rows (columns).

Shrinking vertically is the simplest case given Python's row slicing
operations. Shrinking horizontally is more complex given no native
column slicing operations. This is the code only which his mother
would love.

As implemented this follows a Model-View-Controller paradigm with the
Ship, Field and Scorer classes forming the Model, the View class is
the View and process_script() acting as the Controller.
