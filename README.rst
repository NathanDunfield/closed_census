=======
Logbook
=======

Project started 2015/11/25.

Cusped manifolds
================

All 1-cusped hyperbolic 3-manifolds that can be triangulated with at
most 9 tetrahedra.  As enumerated by Burton and others, there are
59,107 such manifolds.

Finite fillings
===============

Two sources:

1. John Berge's list sent to Nathan in April/May 2015.

2. A fresh list generated using (as the *only* test) the coset
   enumeration feature of Magma (with a limit of 250k cosets).

After debugging my list (forgot to remove infinite cyclic groups
initially) the two lists were identical except that I was missing one
manifold that John included; rerunning that manifold with a different
initial presentation confirmed that John was correct it include it.
In total, there are 59,200 finite Dehn fillings on 46,176 cusped
manifolds (so 78.1% of the manifolds had at least one such filling).
Some 11,594 had two or more finite fillings, and so are Floer simple.
Final data is in "berge/berge_finite_checked_collated.csv.bz2".

Note: Above numbers updated 2018/1/6 from earlier incorrect values of
54,790, 42,325, and 11,035 respectively.  I was missing one of John's
files causing me to undercount, even though the final list exported to
"combined_conjecture" and elsewhere was correct (except for the above
mentioned inclusion of some S^2 x S^1 fillings as having "finite"
fundamental group; this was also corrected on 2018/1/6, see below).

Hyperbolic fillings
===================

I tried to enumerate all closed manifolds with injectivity radius at
least 0.2 that are Dehn fillings on these cusped manifolds.
Specifically, I looked at all slopes up to the size where
Hodgson-Kerckhoff guarantees that inj <= 0.17.  For each slope, I kept
those where the solution type is 'contains negatively oriented
tetrahedra' or better, the volume was positive, and all dual curves
had length >= 0.2.  This resulted in some 611,544 closed manifolds.

WARNING: By "injectivity radius" here, I really mean the length of the
systol. This is bad terminology, but I'm too lazy to fix it right
now. 

I then drilled these manifolds and identified the exteriors to produce
741,723 homeomorphism relations between various of these closed
manifolds; this partitioned them into 309,666 equivalence classes.

For one representative for each class, I used Goerner's verify code to
prove hyperbolicity (sometimes taking finite covers to find a
triangulation where all shapes are positive).  (I have great faith in
SnapPy, but even I was surprised that it worked in every case.)

Next, I refined the equivalence class structure by first computing two
hashes:

a. The volume at quad-double precision, rounded down to double (so all
   digits should be good).

b. A hash based solely on subgroups of index at most 6, computed via
   Magma.

There were 309,258 distinct hashes and hence at least that number of
manifolds (assuming volumes are correct).  When a hash was not unique
it was always shared by exactly two manifolds, and there were 408 pairs
which remained to be examined.

Some 342 these were due to a logic error earlier in "weed.py": the
initial homeomorphism relations omitted those between Dehn fillings on
the same cusped manifold induced by a symmetry of the same acting on
the space of slopes in a nontrivial way.  Another 12 pairs are
definitely isometric, not sure about the remaining 54.  In the
interests of time, I'll work on resolving these later.

Data for these two steps was saved in the original versions of
"cusped_fillings.csv.bz2" and "closed.csv.bz2" in the Mercurial repo.

Work resumed 2016/6/20.  By adding another group-based hash, this time
looking at non-abelian simple quotients, the remaining 54 pairs were
found to be all distinct.  So there are 309,312 distinct closed
manifolds in this sample.

Computing the injectivity radius (using quad-double precision), I found
three examples with injectivity radius < 0.195::

  m055(2, 1), m060(2, 3), m119(-1, 3)

deleting these resulted in a final count of 309,309 distinct closed
manifolds. The collected Dehn-filling descriptions for each closed
manifold were then copied into the cusped database.

Both the closed and cusped databases were saved in
"cusped_fillings.csv.bz2" and "closed.csv.bz2" on 2016/6/21 in
changeset aeeeb60c7cde.

On 2018/6/1, the file "cusped_fillings.csv.bz2" was updated to remove
200 S^2 x S^1 fillings that had been erroneously tagged as "finite
fillings".

On 2019/1/12, the file "closed.csv.bz2" was updated to reflect a bug
fix in the SnapPy code for computing the Chern-Simons invariant in
high-precision.  This changed the values for 1598 manifolds.





