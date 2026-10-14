# 20261014-1750 — FOG, the first dropped state, taken off the list

One binary, one run, both arms alternating per frame (A7VK_AB=flip2). Every
capture is labelled with the arm it was DRAWN with, and both labels are present
(25 arm=0 / 26 arm=29 in each run).

Two runs, and they answer two DIFFERENT questions. Do not read one as the other.

## forced-fogC — "does the fog TERM work?"  (A7VK_FOGFORCE=30,900,ffffff)

Fog term forced on with a white colour and a 30..900 range, so the shader path
is exercised regardless of what the game asks for. 50 cross-arm pairs, one frame
apart.

    metric      fog ON     fog OFF      delta
    share      0.55709     0.51888    +0.03821
    far      119.86660   103.85158   +16.01502
    near      98.74094    91.29110    +7.44984
    mean     109.30377    97.57134   +11.73243
    edge       5.99038     7.09662    -1.10625
    far higher in 48/50 pairs

Row-mean luma, averaged over all 50 pairs: the difference is concentrated in
rows 200-350 (the horizon/background band) at +22 to +29 luma, falling to +3-6
in the extreme foreground. Vertical gradient (bottom-third minus top-third):
ON -29.23, OFF -21.01 -- **39 % steeper with fog on**. That is a distance cue,
in the ground band, which is what the state was supposed to provide.

## unforced-fogD — "does the GAME use fog here?"

Same binary, A7VK_FOGFORCE unset. 50 cross-arm pairs.

    share      0.51357     0.49775    +0.01582
    far      103.52706   104.63815    -1.11109
    mean      97.30710    98.36486    -1.05777
    (far lower in 27/50 pairs -- chance)

Cross-arm signed mean delta: forced +11.74 luma, unforced -1.07 luma. The game
does not fog: D3DRS_FOGENABLE is 0 in every one of 24369 calls, uniq=1, across a
full race stage.

rowmean-luma-profile_forced.png : the 800-row profile of the forced run,
red = fog ON, blue = fog OFF.
