FULL_FEATURES = {
    "general_playing_time": [
        "MP", "Starts", "Min", "90s"
    ],

    "shooting": [
        "Gls", "Ast", "G+A", "PK", "xG", "xAG",
        "Sh", "SoT", "SoT%", "SoT/90", "G/SoT",
        "Dist", "FK"
    ],

    "passing": [
        "Cmp", "Att", "Cmp%", "TotDist", "PrgDist", "PrgP",
        "xA", "KP", "1/3", "PPA", "Live", "Dead", "TB",
        "Sw", "Crs", "TI", "CK", "In", "Out", "Str",
        "Off", "Blocks"
    ],

    "chance_creation": [
        "SCA", "SCA90", "PassLive", "PassDead", "TO",
        "Fld", "Def", "GCA", "GCA90"
    ],

    "defense": [
        "Tkl", "TklW", "Def 3rd", "Mid 3rd", "Tkl%",
        "Lost", "Pass", "Int", "Clr", "Err"
    ],

    "possession_carrying": [
        "Touches", "Def Pen", "Def 3rd", "Mid 3rd", "Live",
        "Succ", "Succ%", "Tkld", "Tkld%", "Carries",
        "CPA", "Mis", "Dis", "Rec", "PrgC", "PrgR"
    ],

    "substitution_context": [
        "Mn/Start", "Compl", "Subs", "Mn/Sub", "unSub",
        "PPM", "onG", "onGA", "+/-", "+/-90"
    ],

    "fouls_recovery_aerials": [
        "Fls", "OG", "Recov", "Won", "Won%"
    ],

    "team_results": [
        "W", "D", "L"
    ],

    "goalkeeping": [
        "GA", "GA90", "SoTA", "Saves", "Save%",
        "CS", "CS%"
    ],

    "goalkeeping_advanced": [
        "GA_stats_keeper_adv", "FK_stats_keeper_adv",
        "CK_stats_keeper_adv", "OG_stats_keeper_adv",
        "/90", "Cmp_stats_keeper_adv", "Cmp%_stats_keeper_adv",
        "Thr", "Launch%", "AvgLen", "Opp",
        "Stp", "Stp%", "#OPA", "#OPA/90","AvgDist"
    ]
}

FEATURE_TAGS = {
    # Shooting ratios / conditional stats
    "SoT%": ["efficiency", "percentage", "conditional", "denominator:Sh"],
    "SoT/90": ["rate", "per90"],
    "G/SoT": ["efficiency", "ratio", "conditional", "denominator:SoT"],
    "Dist": ["conditional", "denominator:Sh"],

    # Passing efficiency
    "Cmp%": ["efficiency", "percentage", "denominator:Att"],

    # Chance creation rates
    "SCA90": ["rate", "per90"],
    "GCA90": ["rate", "per90"],

    # Defensive efficiency
    "Tkl%": ["efficiency", "percentage", "conditional"],

    # Possession / take-on efficiency
    "Succ%": ["efficiency", "percentage", "conditional"],
    "Tkld%": ["efficiency", "percentage", "conditional"],

    # Substitution / playing-time context rates
    "Mn/Start": ["rate", "context"],
    "Mn/Sub": ["rate", "context"],
    "PPM": ["rate", "team_context"],
    "+/-90": ["rate", "per90", "team_context"],

    # Aerial efficiency
    "Won%": ["efficiency", "percentage", "conditional"],

    # Goalkeeping efficiency / rates
    "GA90": ["rate", "per90", "goalkeeping"],
    "Save%": ["efficiency", "percentage", "conditional", "denominator:SoTA"],
    "CS%": ["efficiency", "percentage", "conditional", "denominator:Starts"],

    # Advanced GK
    "/90": ["rate", "per90", "goalkeeping"],
    "Cmp%_stats_keeper_adv": ["efficiency", "percentage", "goalkeeping"],
    "Launch%": ["percentage", "goalkeeping"],
    "Stp%": ["efficiency", "percentage", "conditional", "goalkeeping"],
    "#OPA/90": ["rate", "per90", "goalkeeping"],
}

EXCLUDED_GROUPS = {"substitution_context"}
EXCLUDED_TAGS ={"efficiency", "percentage", "ratio", "conditional"}

def get_feature_groups() -> dict:
    return {
        group: [
            col for col in cols
            if not any(tag in EXCLUDED_TAGS for tag in FEATURE_TAGS.get(col, []))
        ]
        for group, cols in FULL_FEATURES.items()
        if group not in EXCLUDED_GROUPS
    }