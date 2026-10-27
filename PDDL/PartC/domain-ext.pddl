; Extended lunar domain for Part 2C. Everything from the base domain
; (PDDL/PartA&B/domain.pddl) keeps its meaning; the extra astronaut and
; room types only gate the four receiving actions. deploy, transmit-image,
; transmit-scan and store-sample gain an astronaut + room pair and require
; the right astronaut to be standing in the right room of the receiving
; lander. move-astronaut is the one new action.
(define (domain lunar-extended)
    (:requirements :strips :typing)
    (:types rover lander waypoint astronaut room)

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
        ; Astronaut ownership and room layout are static.
        (astronaut-belongs-to ?a - astronaut ?l - lander)
        (room-of ?area - room ?l - lander)
        (docking-bay ?area - room)
        (control-room ?area - room)
        (room-connected ?from - room ?to - room)
        ; One current room per astronaut; moving swaps it.
        (astronaut-at ?a - astronaut ?area - room)
    )

    ; Places the rover at its lander's waypoint. The astronaut gate requires
    ; someone assigned to that lander to be standing in its docking bay.
    (:action deploy
        :parameters (?r - rover ?l - lander ?w - waypoint
                     ?a - astronaut ?area - room)
        :precondition (and
            ; The astronaut and room must belong to this lander.
            (astronaut-belongs-to ?a ?l) (room-of ?area ?l)
            (docking-bay ?area) (astronaut-at ?a ?area)
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

    ; Wireless as in the base domain: the rover may be anywhere and need not
    ; have visited the lander. The astronaut gate requires someone assigned
    ; to the receiving lander to be standing in its control room.
    (:action transmit-image
        :parameters (?r - rover ?l - lander ?source - waypoint
                     ?current - waypoint ?a - astronaut ?area - room)
        :precondition (and
            ; The astronaut and room must belong to this lander.
            (astronaut-belongs-to ?a ?l) (room-of ?area ?l)
            (control-room ?area) (astronaut-at ?a ?area)
            (belongs-to ?r ?l) (rover-at ?r ?current)
            (carrying-image ?r ?source)
        )
        :effect (and
            (not (carrying-image ?r ?source))
            (memory-free ?r) (image-saved ?source ?l)
        )
    )

    (:action transmit-scan
        :parameters (?r - rover ?l - lander ?source - waypoint
                     ?current - waypoint ?a - astronaut ?area - room)
        :precondition (and
            ; The astronaut and room must belong to this lander.
            (astronaut-belongs-to ?a ?l) (room-of ?area ?l)
            (control-room ?area) (astronaut-at ?a ?area)
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

    ; As in the base domain the rover must be at its own lander, and
    ; storage-free is consumed permanently: no unload or discard action.
    ; The astronaut gate requires someone assigned to the receiving lander
    ; to be standing in its docking bay.
    (:action store-sample
        :parameters (?r - rover ?l - lander ?source - waypoint
                     ?current - waypoint ?a - astronaut ?area - room)
        :precondition (and
            ; The astronaut and room must belong to this lander.
            (astronaut-belongs-to ?a ?l) (room-of ?area ?l)
            (docking-bay ?area) (astronaut-at ?a ?area)
            (belongs-to ?r ?l) (rover-at ?r ?current) (lander-at ?l ?current)
            (carrying-sample ?r ?source) (storage-free ?l)
        )
        :effect (and
            (not (carrying-sample ?r ?source)) (sample-free ?r)
            (not (storage-free ?l)) (sample-stored ?source ?l)
        )
    )

    ; Both rooms must belong to the astronaut's own lander. The old room
    ; fact is deleted, so the astronaut is never in two rooms at once.
    (:action move-astronaut
        :parameters (?a - astronaut ?l - lander ?from - room ?to - room)
        :precondition (and
            (astronaut-belongs-to ?a ?l)
            (room-of ?from ?l) (room-of ?to ?l)
            (room-connected ?from ?to) (astronaut-at ?a ?from)
        )
        :effect (and
            (not (astronaut-at ?a ?from)) (astronaut-at ?a ?to)
        )
    )

)
