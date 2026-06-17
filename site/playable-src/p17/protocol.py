"""Shared wire-protocol names for the multiplayer game.

The visible game language is Defender/Attacker. These constants keep the
network payload values stable so existing clients and servers keep talking.
"""

ROLE_DEFENDER = "crewmate"
ROLE_ATTACKER = "impostor"

RESULT_DEFENDERS_WIN = "crewmate_win"
RESULT_ATTACKERS_WIN = "impostor_win"

ACTIVE_SOCIAL_ROLES = (ROLE_DEFENDER, ROLE_ATTACKER)

ROLE_DISPLAY_LABELS = {
    ROLE_DEFENDER: "DEFENDER",
    ROLE_ATTACKER: "ATTACKER",
}


def display_social_role(role):
    return ROLE_DISPLAY_LABELS.get(role, role.upper() if role else "?")
