(define (problem lunar-mission-3)
    (:domain lunar-extended)
    (:objects
        rover1 rover2 - rover
        lander1 lander2 - lander
        wp1 wp2 wp3 wp4 wp5 wp6 - waypoint
        alice bob - astronaut
        l1-docking-bay l1-control-room l2-docking-bay l2-control-room - room
    )
    (:init
        ; Astronauts remain within their assigned stationary landers.
        (astronaut-belongs-to alice lander1)
        (astronaut-belongs-to bob lander2)
        (room-of l1-docking-bay lander1)
        (room-of l1-control-room lander1)
        (room-of l2-docking-bay lander2)
        (room-of l2-control-room lander2)
        (docking-bay l1-docking-bay)
        (docking-bay l2-docking-bay)
        (control-room l1-control-room)
        (control-room l2-control-room)
        (room-connected l1-docking-bay l1-control-room)
        (room-connected l1-control-room l1-docking-bay)
        (room-connected l2-docking-bay l2-control-room)
        (room-connected l2-control-room l2-docking-bay)
        (astronaut-at alice l1-docking-bay)
        (astronaut-at bob l2-control-room)
        (belongs-to rover1 lander1)
        (belongs-to rover2 lander2)
        ; Required setup: rover1 is deployed at its lander at WP2.
        (lander-at lander1 wp2)
        (rover-at rover1 wp2)
        ; Chosen lander2 site: WP1. Mission 3 must retain this choice.
        (lander-at lander2 wp1)
        (aboard rover2 lander2)
        (memory-free rover1)
        (memory-free rover2)
        (sample-free rover1)
        (sample-free rover2)
        (storage-free lander1)
        (storage-free lander2)
        ; Figure 3: three two-way pairs and three one-way edges (nine total).
        (connected wp1 wp2)
        (connected wp2 wp1)
        (connected wp2 wp4)
        (connected wp4 wp2)
        (connected wp3 wp5)
        (connected wp5 wp3)
        (connected wp2 wp3)
        (connected wp5 wp6)
        (connected wp6 wp4)
    )
    (:goal (and
        (image-saved wp3 lander1)
        (scan-saved wp4 lander2)
        (image-saved wp2 lander2)
        (scan-saved wp6 lander1)
        (sample-stored wp5 lander1)
        (sample-stored wp1 lander2)
    ))
)
