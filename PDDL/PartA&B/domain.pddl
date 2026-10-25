(define (domain lunar)
    (:requirements :strips :typing)
    (:types rover lander waypoint)

    (:predicates
        ; Static facts: ownership, stationary landers, directed roads.
        (belongs-to ?r - rover ?l - lander)
        (lander-at ?l - lander ?w - waypoint)
        (connected ?from - waypoint ?to - waypoint)
        ; A rover is either aboard its own lander or at one waypoint.
        (aboard ?r - rover ?l - lander)
        (rover-at ?r - rover ?w - waypoint)
        ; One shared slot for an unsent image OR scan, separate from samples.
        (memory-free ?r - rover)
        (carrying-image ?r - rover ?source - waypoint)
        (carrying-scan ?r - rover ?source - waypoint)
        (image-saved ?source - waypoint ?l - lander)
        (scan-saved ?source - waypoint ?l - lander)
        ; One sample per rover; one stored sample per lander.
        (sample-free ?r - rover)
        (carrying-sample ?r - rover ?source - waypoint)
        (storage-free ?l - lander)
        (sample-stored ?source - waypoint ?l - lander)
    )

    ; Deployment creates the rover's first waypoint location.
    (:action deploy
        :parameters (?r - rover ?l - lander ?w - waypoint)
        :precondition (and
            (belongs-to ?r ?l) (aboard ?r ?l) (lander-at ?l ?w)
        )
        :effect (and (not (aboard ?r ?l)) (rover-at ?r ?w))
    )

    ; Only the explicitly supplied direction of a road is traversable.
    (:action move
        :parameters (?r - rover ?from - waypoint ?to - waypoint)
        :precondition (and (rover-at ?r ?from) (connected ?from ?to))
        :effect (and (not (rover-at ?r ?from)) (rover-at ?r ?to))
    )

    (:action capture-image
        :parameters (?r - rover ?source - waypoint)
        :precondition (and (rover-at ?r ?source) (memory-free ?r))
        :effect (and (not (memory-free ?r)) (carrying-image ?r ?source))
    )

    (:action perform-scan
        :parameters (?r - rover ?source - waypoint)
        :precondition (and (rover-at ?r ?source) (memory-free ?r))
        :effect (and (not (memory-free ?r)) (carrying-scan ?r ?source))
    )

    ; Wireless: current and source locations may differ. No proximity to a
    ; lander, or previous lander visit, is required. Held data is required.
    (:action transmit-image
        :parameters (?r - rover ?l - lander ?source - waypoint ?current - waypoint)
        :precondition (and
            (belongs-to ?r ?l) (rover-at ?r ?current)
            (carrying-image ?r ?source)
        )
        :effect (and
            (not (carrying-image ?r ?source))
            (memory-free ?r) (image-saved ?source ?l)
        )
    )

    (:action transmit-scan
        :parameters (?r - rover ?l - lander ?source - waypoint ?current - waypoint)
        :precondition (and
            (belongs-to ?r ?l) (rover-at ?r ?current)
            (carrying-scan ?r ?source)
        )
        :effect (and
            (not (carrying-scan ?r ?source))
            (memory-free ?r) (scan-saved ?source ?l)
        )
    )

    ; The waypoint records sample provenance. No finite source stock is
    ; specified; rover carrying and lander storage capacities are limited.
    (:action collect-sample
        :parameters (?r - rover ?source - waypoint)
        :precondition (and (rover-at ?r ?source) (sample-free ?r))
        :effect (and (not (sample-free ?r)) (carrying-sample ?r ?source))
    )

    ; Samples must physically return to the rover's own lander.
    ; storage-free is consumed permanently: no unload or discard action.
    (:action store-sample
        :parameters (?r - rover ?l - lander ?source - waypoint ?current - waypoint)
        :precondition (and
            (belongs-to ?r ?l) (rover-at ?r ?current) (lander-at ?l ?current)
            (carrying-sample ?r ?source) (storage-free ?l)
        )
        :effect (and
            (not (carrying-sample ?r ?source)) (sample-free ?r)
            (not (storage-free ?l)) (sample-stored ?source ?l)
        )
    )
)
