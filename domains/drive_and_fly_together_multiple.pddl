(define (domain drive_and_fly_together_multiple)

(:requirements :typing :fluents :durative-actions :conditional-effects)
(:types location)
(:predicates (truck-in ?x - location)
            (drone-in ?x - location)
            (drone-on-truck)
            (package-delivered-at ?x - location)
            (can_drive ?from ?to - location)
            (can_fly ?from ?to - location)
            (drone-out)
            )
(:functions (drive-time ?from ?to - location)
            (fly-time ?from ?to - location)
            (battery-time)
            (full-battery-time)
)

(:durative-action truck-drive-alone
:parameters (?from - location ?to - location)
:duration (= ?duration (drive-time ?from ?to))
:condition (and
    (at start (and
        (truck-in ?from)
        (can_drive ?from ?to)
    ))
    (over all (drone-out))
)
:effect (and
    (at start (not (truck-in ?from)))
    (at end (truck-in ?to))
)
)

(:durative-action truck-drive-with-drone
:parameters (?from - location ?to - location)
:duration (= ?duration (drive-time ?from ?to))
:condition (and
    (at start (and
        (truck-in ?from)
        (drone-in ?from)
        (can_drive ?from ?to)
    ))
    (over all (drone-on-truck))
)
:effect (and
    (at start (and
        (not (truck-in ?from))
        (not (drone-in ?from))
    ))
    (at end (and
        (truck-in ?to)
        (drone-in ?to)
    )
    )
)
)

(:durative-action drone-deliver
	:parameters (?from ?to - location)
	:duration ( = ?duration (fly-time ?from ?to))
	:condition (and
		(at start (and
            (drone-in ?from)
            (drone-on-truck)
            (can_fly ?from ?to)
            (truck-in ?from)
            (> (battery-time) (fly-time ?from ?to))
            )))
	:effect (and
        (at start (and
            (not (drone-on-truck))
            (not (drone-in ?from))
            (drone-out)
            ))
		(at end (and
		    (package-delivered-at ?to)
		    (decrease (battery-time) (fly-time ?from ?to))
		    (drone-in ?to)
		    ))
        )
)

(:durative-action drone-deliver-out
	:parameters (?from ?to - location)
	:duration ( = ?duration (fly-time ?from ?to))
	:condition (and
		(at start (and
            		(drone-in ?from)
            		(drone-out)
            		(can_fly ?from ?to)
            		(> (battery-time) (fly-time ?from ?to))
            )))
	:effect (and
        (at start (not (drone-in ?from)))
		(at end (and
		    (drone-in ?to)
		    (package-delivered-at ?to)
		    (decrease (battery-time) (fly-time ?from ?to))
		    ))
        )
)

(:durative-action drone-return
	:parameters (?from ?to - location)
	:duration ( = ?duration (fly-time ?from ?to))
	:condition (and
		(at start (and
            (drone-in ?from)
            (drone-out)
            (can_fly ?from ?to)
            (> (battery-time) (fly-time ?from ?to))
            ))
        (at end (truck-in ?to)))
	:effect (and
        (at start (not (drone-in ?from)))
		(at end (and
            (drone-on-truck)
            (assign (battery-time) (full-battery-time))
            (not (drone-out))
            (drone-in ?to)
            ))
        )
)
)