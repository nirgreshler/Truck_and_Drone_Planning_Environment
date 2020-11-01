(define (domain drive_with_drone)

(:requirements :adl :typing :fluents :durative-actions)
(:types location)
(:predicates (truck-in ?x - location)
            (drone-in ?x - location)
            (drone-on-truck)
            (package-delivered-at ?x - location)
            (can_drive ?from ?to - location)
            (can_fly ?from ?to - location)
            )
(:functions (drive-time ?from ?to - location)
            (fly-time ?from ?to - location)
            (battery-time)
            (full-battery-time)
)

(:durative-action truck-drive
:parameters (?from - location ?to - location)
:duration (= ?duration (drive-time ?from ?to))
:condition (and 
    (at start (and 
    (truck-in ?from)
    (can_drive ?from ?to)
    ))
    (over all (drone-on-truck))
)
:effect (and
    (at start (not (truck-in ?from)))
    (at end (and 
    (truck-in ?to)
    (drone-in ?to)))
)
)

(:durative-action drone-deliver
	:parameters (?from ?to - location)
	:duration ( = ?duration (fly-time ?from ?to))
	:condition (and
		(at start (and (drone-in ?from) (drone-on-truck) (can_fly ?from ?to)))
		; (at start (not (package-delivered-at ?to)))
		(over all (truck-in ?from)))
	:effect (and
        (at start (not (drone-on-truck)))
		(at end (drone-in ?to))
		(at end (package-delivered-at ?to))
        )
)

(:durative-action drone-return
	:parameters (?from ?to - location)
	:duration ( = ?duration (fly-time ?from ?to))
	:condition (and
		(at start (and (drone-in ?from) (can_fly ?from ?to)))
        (over all (truck-in ?to)))
	:effect (and
        (at start (not (drone-in ?from)))
		(at end (drone-on-truck))
        )
)

)