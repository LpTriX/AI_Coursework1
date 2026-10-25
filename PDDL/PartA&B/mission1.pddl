(define (problem lunar-mission-1)
    (:domain lunar)
    (:objects
        rover1 - rover
        lander1 - lander
        wp1 wp2 wp3 wp4 wp5 - waypoint
    )
    (:init
        ; Landing is fixed at WP1 as permitted; the rover is undeployed.
        (belongs-to rover1 lander1)
        (lander-at lander1 wp1)
        (aboard rover1 lander1)
        (memory-free rover1)
        (sample-free rover1)
        (storage-free lander1)
        ; Figure 2: six directed edges, no implicit reverse roads.
        (connected wp1 wp2)
        (connected wp2 wp3)
        (connected wp3 wp5)
        (connected wp5 wp1)
        (connected wp1 wp4)
        (connected wp4 wp3)
    )
    (:goal (and
        (image-saved wp5 lander1)
        (scan-saved wp3 lander1)
        (sample-stored wp1 lander1)
    ))
)
