"""Create and inspect a LineCode, a single Line, and a batch in AltDSS-Python."""

from altdss import altdss


def main():
    ctx = altdss.NewContext()
    ctx.Commands("New Circuit.workflow_lines Bus1=source BasekV=12.47 Phases=3")

    feeder_code = ctx.LineCode.new(
        "feeder_code",
        NPhases=3,
        Units="km",
        R1=0.20,
        X1=0.40,
        R0=0.50,
        X0=1.20,
        C1=3.4,
        C0=1.6,
        BaseFreq=60.0,
    )

    main_line = ctx.Line.new(
        "main",
        Bus1="source.1.2.3",
        Bus2="junction.1.2.3",
        LineCode=feeder_code,
        Length=1.0,
        Units="km",
    )

    # Arrays follow names order. The code and units are shared by both lines.
    laterals = ctx.Line.batch_new(
        names=["lateral_a", "lateral_b"],
        Bus1=["junction.1.2.3", "junction.1.2.3"],
        Bus2=["end_a.1.2.3", "end_b.1.2.3"],
        LineCode=feeder_code,
        Length=[0.25, 0.40],
        Units="km",
    )

    print("LineCode C1/C0 (nF/km):", feeder_code.C1, feeder_code.C0)
    print("Main line:", main_line.Bus1, main_line.Bus2, main_line.Length)
    print("Lateral receiving buses:", laterals.Bus2)
    print("Lateral lengths (km):", list(laterals.Length))


if __name__ == "__main__":
    main()
