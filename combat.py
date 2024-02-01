import math
import random
from enum import Enum
from hero import *

# CONSTANTS
HP = 0
ATK = 1
SPD = 2
DEF = 3
RES = 4

def move_letters(s, letter):
    if letter not in ['A', 'D']:
        return "Invalid letter"

    first_occurrence = s.find(letter)
    if first_occurrence == -1:
        return s

    remaining_part = s[first_occurrence + 1:]
    moved_letters = s[first_occurrence] * remaining_part.count(letter)
    new_string = s[:first_occurrence + 1] + moved_letters + remaining_part.replace(letter, '')

    return new_string


def simulate_combat(attacker, defender, isInSim, turn, spacesMovedByAtkr, combatEffects):

    # Invalid Combat if one unit is dead
    # or if attacker does not have weapon
    if attacker.HPcur <= 0 or defender.HPcur <= 0 or attacker.weapon is None: return (-1,-1)

    # OK I gotta do some research on all cases of this
    # actually wait shouldn't this only get incremented upon the ACTUAL combat?
    # Known cases: Kvasir/NY!Kvasir, Fell Star, Resonance: Shields
    attacker.unitCombatInitiates += 1
    defender.enemyCombatInitiates += 1

    # Output arrays
    atkAttackDamages = []
    defAttackDamages = []

    atkSpCharges = []
    defSpCharges = []

    # Estimate given in-game
    # Determined by atk - def/res + true damage ADDED IN ALL HITS
    atkFEHDamage = 0
    defFEHDamage = 0

    # who possesses the weapon triangle advantage
    # 0 - attacker
    # 1 - defender
    # -1 - neither
    wpnAdvHero = -1

    # lists of attacker/defender's skills & stats
    atkSkills = attacker.getSkills()
    atkStats = attacker.getStats()
    atkPhantomStats = [0] * 5

    defSkills = defender.getSkills()
    defStats = defender.getStats()
    defPhantomStats = [0] * 5

    atkHPCur = attacker.HPcur
    defHPCur = defender.HPcur

    atkSpCountCur = attacker.specialCount
    defSpCountCur = defender.specialCount

    if "phantomSpd" in atkSkills: atkPhantomStats[SPD] += max(atkSkills["phantomSpd"] * 3 + 2, 10)
    if "phantomRes" in atkSkills: atkPhantomStats[RES] += max(atkSkills["phantomRes"] * 3 + 2, 10)
    if "phantomSpd" in defSkills: defPhantomStats[SPD] += max(defSkills["phantomSpd"] * 3 + 2, 10)
    if "phantomRes" in defSkills: defPhantomStats[RES] += max(defSkills["phantomRes"] * 3 + 2, 10)

    # Now wouldn't that be amayzing -Matthew Vandham (2023)
    unit = [attacker, defender]
    stats = [atkStats, defStats]
    skills = [atkSkills, defSkills]
    phantomStats = [atkPhantomStats, defPhantomStats]

    # stored combat buffs (essentially everything)
    atkCombatBuffs = [0] * 5
    defCombatBuffs = [0] * 5
    combatBuffs = [atkCombatBuffs, defCombatBuffs]

    # add effects of CombatFields
    if isInSim:
        skills[0].update(e.effect for e in combatEffects if e.affectedSide == 0 and e.range(unit[0].tile) and e.condition(unit[0]) and (e.affectSelf or not e.owner == unit[0]))
        skills[1].update(e.effect for e in combatEffects if e.affectedSide == 1 and e.range(unit[1].tile) and e.condition(unit[1]) and (e.affectSelf or not e.owner == unit[1]))

    # common position-based conditions
    if isInSim:
        atkAdjacentToAlly = attacker.tile.unitsWithinNSpaces(1, True)
        atkAllyWithin2Spaces = attacker.tile.unitsWithinNSpaces(2, True)
        atkAllyWithin3Spaces = attacker.tile.unitsWithinNSpaces(3, True)
        atkAllyWithin4Spaces = attacker.tile.unitsWithinNSpaces(4, True)
        defAdjacentToAlly = defender.tile.unitsWithinNSpaces(1, True)
        defAllyWithin2Spaces = defender.tile.unitsWithinNSpaces(2, True)
        defAllyWithin3Spaces = defender.tile.unitsWithinNSpaces(3, True)
        defAllyWithin4Spaces = defender.tile.unitsWithinNSpaces(4, True)
    else:
        atkAdjacentToAlly = 0
        atkAllyWithin2Spaces = 0
        atkAllyWithin3Spaces = 0
        atkAllyWithin4Spaces = 0
        defAdjacentToAlly = 0
        defAllyWithin2Spaces = 0
        defAllyWithin3Spaces = 0
        defAllyWithin4Spaces = 0

    if isInSim: atkFoeWithin2Spaces = attacker.tile.unitsWithinNSpaces(1, False)
    else: atkFoeWithin2Spaces = 0

    atkInfAlliesWithin2Spaces = 0
    atkCavAlliesWithin2Spaces = 0
    atkArmAlliesWithin2Spaces = 0
    atkFlyAlliesWithin2Spaces = 0
    atkPhysMeleeCavWithin2Spaces = 0

    defAdjacentToAlly = 0
    defAllyWithin2Spaces = 0
    defAllyWithin3Spaces = 0
    defAllyWithin4Spaces = 0
    defNumAlliesWithin2Spaces = 0
    defNumFoesWithin2Spaces = 0
    defInfAlliesWithin2Spaces = 0
    defCavAlliesWithin2Spaces = 0
    defArmAlliesWithin2Spaces = 0
    defFlyAlliesWithin2Spaces = 0

    #common HP-based conditions
    atkHPGreaterEqual25Percent = atkHPCur / atkStats[0] >= 0.25
    atkHPGreaterEqual50Percent = atkHPCur / atkStats[0] >= 0.50
    atkHPGreaterEqual75Percent = atkHPCur / atkStats[0] >= 0.75
    atkHPEqual100Percent = atkHPCur == atkStats[0]

    defHPGreaterEqual25Percent = defHPCur / defStats[0] >= 0.25
    defHPGreaterEqual50Percent = defHPCur / defStats[0] >= 0.50
    defHPGreaterEqual75Percent = defHPCur / defStats[0] >= 0.75
    defHPEqual100Percent = defHPCur == defStats[0]

    # Genesis Falchion
    atkTop3AllyBuffTotal = 0
    defTop3AllyBuffTotal = 0

    # Dark Creator Sword
    atkNumAlliesHPGE90Percent = 0
    defNumAlliesHPGE90Percent = 0

    if isInSim:
        atkDefensiveTerrain = attacker.tile.is_def_terrain
        defDefensiveTerrain = defender.tile.is_def_terrain
    else:
        atkDefensiveTerrain = False
        defDefensiveTerrain = False

    #  Panic Status Effect
    AtkPanicFactor = 1
    DefPanicFactor = 1

    # buffs + debuffs calculation
    # throughout combat, PanicFactor * buff produces the current buff value
    if Status.Panic in attacker.statusNeg: AtkPanicFactor *= -1
    if Status.Panic in defender.statusNeg: DefPanicFactor *= -1

    if Status.NullPanic in attacker.statusPos: AtkPanicFactor = 1
    if Status.NullPanic in defender.statusPos: DefPanicFactor = 1

    # apply buffs/debuffs

    atkStats[ATK] += attacker.buffs[ATK] * AtkPanicFactor + attacker.debuffs[ATK]
    atkStats[SPD] += attacker.buffs[SPD] * AtkPanicFactor + attacker.debuffs[SPD]
    atkStats[DEF] += attacker.buffs[DEF] * AtkPanicFactor + attacker.debuffs[DEF]
    atkStats[RES] += attacker.buffs[RES] * AtkPanicFactor + attacker.debuffs[RES]

    defStats[ATK] += defender.buffs[ATK] * DefPanicFactor + defender.debuffs[ATK]
    defStats[SPD] += defender.buffs[SPD] * DefPanicFactor + defender.debuffs[SPD]
    defStats[DEF] += defender.buffs[DEF] * DefPanicFactor + defender.debuffs[DEF]
    defStats[RES] += defender.buffs[RES] * DefPanicFactor + defender.debuffs[RES]

    # [Bonus] and [Penalty] conditions
    atkHasBonus = attacker.hasBonus()
    defHasBonus = defender.hasBonus()
    atkHasPenalty = attacker.hasPenalty()
    defHasPenalty = defender.hasPenalty()

    # triangle adept during combat, default of -1
    triAdept = -1

    # cancel affinity, differs between ally and foe for
    # levels 2/3 because my life can't be easy
    atkCA = 0
    defCA = 0

    # ignore range (distant/close counter)
    ignoreRng = False

    # prevent counterattacks from defender (sweep, flash)
    cannotCounter = False

    # grants brave effect
    braveATKR = False
    braveDEFR = False

    # vantage
    vantageEnabled = False

    # desperation
    desperateA = False
    desperateD = False

    # hardy bearing
    hardyBearingAtk = False
    hardyBearingDef = False

    # special disabled (special cannot proc)
    atkSpecialDisabled = False
    defSpecialDisabled = False

    # number of follow-ups permitted
    atkSkillFollowUps = 0  # guaranteed follow-ups granted by skills (brash assault)
    atkSkillFollowUpDenials = 0  # follow-ups denied by skills (windsweep)
    defSkillFollowUps = 0
    defSkillFollowUpDenials = 0
    atkSpdFollowUps = 0
    defSpdFollowUps = 0

    # null follow-up
    atkNullDefFU = False # prevent foe's guaranteed follow-ups
    defNullAtkFU = False # prevent atkr's guaranteed follow-ups
    atkDoSkillFU = False # disables foe's skills that disable follow-ups
    defDoSkillFU = False # disables atkr's sskills that disable follow-ups

    # special cooldown charge boost (affected by heavy blade, guard, etc.)
    attackerGainWhenAttacking = 0
    attackerGainWhenAttacked = 0
    attackerLossWhenAttacking = 0
    attackerLossWhenAttacked = 0

    defenderGainWhenAttacking = 0
    defenderGainWhenAttacked = 0
    defenderLossWhenAttacking = 0
    defenderLossWhenAttacked = 0

    # mid-combat special charge
    atkSpChargeBeforeFirstStrike = 0
    defSpChargeBeforeFirstStrike = 0

    # GET RID
    atkHit1Reduction = 1 # how much the attacker's first hit is reduced by
    atkHit2Reduction = 1
    atkHit3Reduction = 1
    atkHit4Reduction = 1

    defHit1Reduction = 1 # how much the defender's first hit is reduced by
    defHit2Reduction = 1
    defHit3Reduction = 1
    defHit4Reduction = 1

    # how much damage is reduced by (skills like Phys. Null Follow or Impenetrable Void)
    atkDmgReduFactor = 1 # atk causes def's hits to be reduced
    defDmgReduFactor = 1 #c

    atkAllHitsRedu = []
    atkFirstAttackRedu = []
    atkFirstStrikesRedu = []
    atkSecondStrikesRedu = []
    atkConsecutiveRedu = []
    atkSpReadyRedu = []
    atkSpTriggeredNextRedu = []

    defAllHitsRedu = []
    defFirstAttackRedu = []
    defFirstStrikesRedu = []
    defSecondStrikesRedu = []
    defConsecutiveRedu = []
    defSpReadyRedu = []
    defSpTriggeredNextRedu = []

    # pseudo-Miracle effects (refined Tyrfing)
    atkPseudoMiracleEnabled = False
    defPseudoMiracleEnabled = False

    # true damage when attacking
    atkTrueDamage = 0
    defTrueDamage = 0
    # needs to be per hit yaaaaaaaaaaaaay
    atkTrueDamageArr = [0] * 4
    defTrueDamageArr = [0] * 4

    # finish skills
    atkFinishTrueDamage = 0
    defFinishTrueDamage = 0

    atkTrueDamageFunc = lambda α: atkFinishTrueDamage * α
    defTrueDamageFunc = lambda δ: defFinishTrueDamage * δ

    # true damage when attacking (special only)
    atkFixedSpDmgBoost = 0
    defFixedSpDmgBoost = 0

    # damage done to self after combat
    atkSelfDmg = 0
    defSelfDmg = 0

    # damage done to other after combat iff self attacks other (should be added to atk/defSelfDmg)
    atkOtherDmg = 0
    defOtherDmg = 0

    # damage done to self iff self attacks other (should be added to atk/defSelfDmg)
    atkRecoilDmg = 0
    defRecoilDmg = 0

    # i dunno how to explain but i need them and to remove them i need to use a bit of brainpower
    NEWatkOtherDmg = 0
    NEWdefOtherDmg = 0

    # healing after combat, negated by deep wounds, cannot be reduced by special fighter 4
    atkPostCombatHealing = 0
    defPostCombatHealing = 0

    # mid-combat healing per hit, fully negated by deep wounds
    atkMidCombatHeal = 0
    defMidCombatHeal = 0
    atkFinishMidCombatHeal = 0
    defFinishMidCombatHeal = 0

    atkMidCombatHealFunc = lambda u:atkMidCombatHeal + atkFinishMidCombatHeal * u
    defMidCombatHealFunc = lambda v:defMidCombatHeal + defFinishMidCombatHeal * v

    # highest % of healing allowed while deep wounds active during combat, special fighter 4
    atkDeepWoundsHealAllowance = 0
    defDeepWoundsHealAllowance = 0

    # special charge granted after combat (special spiral, dark mystletainn, etc.)
    atkPostCombatSpCharge = 0
    defPostCombatSpCharge = 0

    # status effects given after combat
    # 0 - given regardless
    # 1 - given if attacked by foe
    # 2 - given if attacked foe
    # ex: attacker has panic, defender is hit
    # elements of 2 with be appended to 0
    # at end of combat, all of 0 will be given to defender
    atkPostCombatStatusesApplied = [[],[],[]]
    defPostCombatStatusesApplied = [[],[],[]]

    atkBonusesNeutralized = [False] * 5
    defBonusesNeutralized = [False] * 5
    atkPenaltiesNeutralized = [False] * 5
    defPenaltiesNeutralized = [False] * 5

    # Ignore % damage reduction on only special or always
    atkSpPierceDR = False
    atkAlwaysPierceDR = False
    defSpPierceDR = False
    defAlwaysPierceDR = False

    # SOME STATUSES

    if Status.Discord in attacker.statusNeg:
        atkCombatBuffs[1] -= min(2 + atkAllyWithin2Spaces, 5)
        atkCombatBuffs[2] -= min(2 + atkAllyWithin2Spaces, 5)
        atkCombatBuffs[3] -= min(2 + atkAllyWithin2Spaces, 5)
        atkCombatBuffs[4] -= min(2 + atkAllyWithin2Spaces, 5)

    if Status.Discord in defender.statusNeg:
        defCombatBuffs[1] -= min(2 + defNumAlliesWithin2Spaces, 5)
        defCombatBuffs[2] -= min(2 + defNumAlliesWithin2Spaces, 5)
        defCombatBuffs[3] -= min(2 + defNumAlliesWithin2Spaces, 5)
        defCombatBuffs[4] -= min(2 + defNumAlliesWithin2Spaces, 5)

    # ATTACKER SKILLS -----------------------------------------------------------------------------------------------------------------------

    if "atkBlow" in atkSkills: atkCombatBuffs[1] += atkSkills["atkBlow"] * 2
    if "spdBlow" in atkSkills: atkCombatBuffs[2] += atkSkills["spdBlow"] * 2
    if "defBlow" in atkSkills: atkCombatBuffs[3] += atkSkills["defBlow"] * 2
    if "resBlow" in atkSkills: atkCombatBuffs[4] += atkSkills["resBlow"] * 2

    if "fireBoost" in atkSkills and atkHPCur >= defHPCur + 3: atkCombatBuffs[1] += atkSkills["fireBoost"] * 2
    if "windBoost" in atkSkills and atkHPCur >= defHPCur + 3: atkCombatBuffs[2] += atkSkills["windBoost"] * 2
    if "earthBoost" in atkSkills and atkHPCur >= defHPCur + 3: atkCombatBuffs[3] += atkSkills["earthBoost"] * 2
    if "waterBoost" in atkSkills and atkHPCur >= defHPCur + 3: atkCombatBuffs[4] += atkSkills["waterBoost"] * 2

    if "brazenAtk" in atkSkills and atkHPCur / atkStats[HP] <= 0.8: atkCombatBuffs[1] += atkSkills["brazenAtk"]
    if "brazenSpd" in atkSkills and atkHPCur / atkStats[HP] <= 0.8: atkCombatBuffs[2] += atkSkills["brazenSpd"]
    if "brazenDef" in atkSkills and atkHPCur / atkStats[HP] <= 0.8: atkCombatBuffs[3] += atkSkills["brazenDef"]
    if "brazenRes" in atkSkills and atkHPCur / atkStats[HP] <= 0.8: atkCombatBuffs[4] += atkSkills["brazenRes"]

    if "atkBond" in atkSkills and atkAdjacentToAlly: atkCombatBuffs[1] += atkSkills["atkBond"]
    if "spdBond" in atkSkills and atkAdjacentToAlly: atkCombatBuffs[2] += atkSkills["spdBond"]
    if "defBond" in atkSkills and atkAdjacentToAlly: atkCombatBuffs[3] += atkSkills["defBond"]
    if "resBond" in atkSkills and atkAdjacentToAlly: atkCombatBuffs[4] += atkSkills["resBond"]

    if "atkRein" in atkSkills: defCombatBuffs -= atkSkills["atkRein"]
    if "spdRein" in atkSkills: defCombatBuffs -= atkSkills["atkRein"]
    if "defRein" in atkSkills: defCombatBuffs -= atkSkills["atkRein"]
    if "resRein" in atkSkills: defCombatBuffs -= atkSkills["atkRein"]


    if "ILOVEBONUSES" in atkSkills and atkHPGreaterEqual50Percent or atkHasBonus:
        map(lambda x: x + 4, atkCombatBuffs)

    if "SEGAAAA" in atkSkills or "nintenesis" in atkSkills:
        map(lambda x: x + 5, atkCombatBuffs)
        if atkTop3AllyBuffTotal >= 25:
            atkCombatBuffs[1] += 5
            atkMidCombatHeal += 5

    if ("SEGAAAA" in defSkills or "nintenesis" in defSkills) and defAllyWithin2Spaces:
        map(lambda x: x + 5, defCombatBuffs)
        if defTop3AllyBuffTotal >= 25:
            defCombatBuffs[1] += 5
            defMidCombatHeal += 5 + 2 * ("nintenesis" in defSkills)
        if defTop3AllyBuffTotal >= 60:
            vantageEnabled = True

    if "denesis" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[1] += 5 # + highest atk bonus on self/allies within 2 spaces
        # and the rest of them

    if "denesis" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[1] += 5 # + highest atk bonus on self/allies within 2 spaces
        # and the rest of them

    if "caedaVantage" in defSkills and (attacker.wpnType in ["Sword", "Lance", "Axe", "CBow"] or attacker.move == 3 or defHPCur/defStats[0] <= 0.75):
        vantageEnabled = True

    if "guardraug" in atkSkills and atkAllyWithin2Spaces:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[3] += 5
        atkPenaltiesNeutralized[ATK] = True
        atkPenaltiesNeutralized[DEF] = True

    if "guardraug" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[1] += 5
        defCombatBuffs[3] += 5
        defPenaltiesNeutralized[ATK] = True
        defPenaltiesNeutralized[DEF] = True

    if "triangleAtk" in atkSkills and atkFlyAlliesWithin2Spaces >= 2:
        map(lambda x: x + 3, atkCombatBuffs)
        braveATKR = True

    if "triangleAtk" in defSkills and defFlyAlliesWithin2Spaces >= 2:
        map(lambda x: x + 3, defCombatBuffs)

    if "banana" in atkSkills and (atkInfAlliesWithin2Spaces > 0 or atkFlyAlliesWithin2Spaces > 0):
        atkCombatBuffs[1] += 4
        atkCombatBuffs[2] += 4

    if "banana" in defSkills and (defInfAlliesWithin2Spaces > 0 or defFlyAlliesWithin2Spaces > 0):
        defCombatBuffs[1] += 4
        defCombatBuffs[2] += 4

    if "bibleBros" in atkSkills:
        atkCombatBuffs[1] += max(atkAllyWithin2Spaces * 2, 6)
        atkCombatBuffs[3] += max(atkAllyWithin2Spaces * 2, 6)

    if "bibleBrosBrave" in atkSkills and atkPhysMeleeCavWithin2Spaces:
        braveATKR = True

    if "bibleBros" in defSkills:
        defCombatBuffs[1] += max(defNumAlliesWithin2Spaces * 2, 6)
        defCombatBuffs[3] += max(defNumAlliesWithin2Spaces * 2, 6)

    if "BEAST MODE BABY" in atkSkills and sum(defender.debuffs) == 0:
        atkCombatBuffs[1] += 6
        atkCombatBuffs[3] += 6

    if "BEAST MODE BABY" in defSkills and sum(attacker.debuffs) == 0:
        defCombatBuffs[1] += 6
        defCombatBuffs[3] += 6

    if "mercuriusMegabuff" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)

    if "mercuriusMegabuff" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)

    if "yahoo" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs[1] += 4 # plus highest atk buff among self & allies within 3 spaces
        atkCombatBuffs[2] += 4 # and so on
        atkCombatBuffs[3] += 4 # and so forth
        atkCombatBuffs[4] += 4 # for all 4 stats

    if "yahoo" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[1] += 4 # if you have panic
        defCombatBuffs[2] += 4 # and not null panic
        defCombatBuffs[3] += 4 # your buff don't count
        defCombatBuffs[4] += 4 # bottom text

    if "extraAstra" in atkSkills:
        map(lambda x: x + 4, atkCombatBuffs)

    if "extraAstra" in defSkills and defAllyWithin2Spaces:
        map(lambda x: x + 4, defCombatBuffs)

    if "superExtraAstra" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        atkCombatBuffs[1] += min(spacesMovedByAtkr * 2, 8)
        defCombatBuffs[3] -= min(spacesMovedByAtkr * 2, 8)

    if "superExtraAstra" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)
        defCombatBuffs[1] += min(spacesMovedByAtkr * 2, 8)
        atkCombatBuffs[3] -= min(spacesMovedByAtkr * 2, 8)

    if "shadowBlade" in atkSkills and defHPEqual100Percent:
        defCombatBuffs[1] -= 4
        defCombatBuffs[2] -= 4
        defCombatBuffs[3] -= 4
        atkPenaltiesNeutralized = [True] * 5

    if "shadowBlade" in defSkills and atkHPEqual100Percent:
        atkCombatBuffs[1] -= 4
        atkCombatBuffs[2] -= 4
        atkCombatBuffs[3] -= 4
        defPenaltiesNeutralized = [True] * 5

    if "Hello, I like money" in atkSkills:
        map(lambda x: x + 4 + (2 * attacker.dragonflowers > 0), atkCombatBuffs)

    if "Hello, I like money" in defSkills and defAllyWithin2Spaces:
        map(lambda x: x + 4 + (2 * defender.dragonflowers > 0), defCombatBuffs)

    if "doubleLion" in atkSkills and atkHPEqual100Percent: #refined eff alm
        braveATKR = True
        atkSelfDmg += 5

    if "dracofalchion" in atkSkills and atkFoeWithin2Spaces >= atkAllyWithin2Spaces: map(lambda x: x + 5, atkCombatBuffs)
    if "dracofalchion" in defSkills and defNumFoesWithin2Spaces >= defNumAlliesWithin2Spaces: map(lambda x: x + 5, defCombatBuffs)
    if "dracofalchionDos" in atkSkills: map(lambda x: x + 5, atkCombatBuffs)
    if "dracofalchionDos" in defSkills and defAllyWithin2Spaces: map(lambda x: x + 5, defCombatBuffs)
    if "sweeeeeeep" in atkSkills and atkHPGreaterEqual25Percent: map(lambda x: x + 5, atkCombatBuffs)
    if "sweeeeeeep" in defSkills and defHPGreaterEqual25Percent: map(lambda x: x + 5, defCombatBuffs)

    if "grayBoost" in atkSkills and atkHPGreaterEqual50Percent: map(lambda x: x + 3, atkCombatBuffs)
    if "grayBoost" in defSkills and defHPGreaterEqual50Percent: map(lambda x: x + 3, defCombatBuffs)
    if "challenger" in atkSkills and atkAllyWithin2Spaces <= atkFoeWithin2Spaces: map(lambda x: x + 5, atkCombatBuffs)
    if "challenger" in defSkills and defNumAlliesWithin2Spaces <= defNumFoesWithin2Spaces: map(lambda x: x + 5, defCombatBuffs)

    if "HPWarrior" in atkSkills and atkStats[0] >= defHPCur + 1: map(lambda x: x + 4, atkCombatBuffs)
    if "HPWarrior" in defSkills and defStats[0] >= atkHPCur + 1: map(lambda x: x + 4, defCombatBuffs)

    if ("belovedZofia" in atkSkills and atkHPEqual100Percent) or "belovedZofia2" in atkSkills:
        map(lambda x: x + 4, atkCombatBuffs)
        atkRecoilDmg += 4

    if "A man has fallen into the river in LEGO City!" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        atkPostCombatHealing += 7

    if "ALMMM" in atkSkills and (not atkHPEqual100Percent or not defHPEqual100Percent):
        map(lambda x: x + 4, atkCombatBuffs)
        atkMidCombatHeal += 7

    if "SUPER MARIO!!!" in atkSkills and atkSpCountCur == 0:
        map(lambda x: x + 3, atkCombatBuffs)

    if "SUPER MARIO!!!" in defSkills and defSpCountCur == 0:
        map(lambda x: x + 3, atkCombatBuffs)
        ignoreRng = True

    if "berkutBoost" in atkSkills and defHPEqual100Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        atkCombatBuffs[2] -= 5

    if "baseTyrfing" in atkSkills and atkHPCur / atkStats[0] <= 0.5:
        atkCombatBuffs[3] += 4

    if "refDivTyrfing" in atkSkills and atkHPGreaterEqual50Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[3] += 5

    if "WE MOVE" in atkSkills and atkHPGreaterEqual50Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[3] += 5
        atkSkillFollowUps += 1

    if "vTyrfing" in atkSkills and not atkHPEqual100Percent:
        defCombatBuffs[1] -= 6
        defCombatBuffs[3] -= 6
        atkMidCombatHeal += 7

    if "vTyrfing" in defSkills:
        atkCombatBuffs[1] -= 6
        atkCombatBuffs[3] -= 6
        defMidCombatHeal += 7

    if "newVTyrfing" in atkSkills and (not atkHPEqual100Percent or defHPGreaterEqual75Percent):
        defCombatBuffs[1] -= 6
        defCombatBuffs[3] -= 6
        atkMidCombatHeal += 8

    if "newVTyrfing" in defSkills:
        atkCombatBuffs[1] -= 6
        atkCombatBuffs[3] -= 6
        defMidCombatHeal += 8

    if "NO MORE LOSSES" in atkSkills:
        defCombatBuffs[1] -= 5
        defCombatBuffs[3] -= 5

    if "NO MORE LOSSES" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[1] -= 5
        defCombatBuffs[3] -= 5

    if "I HATE FIRE JOKES >:(" in atkSkills and spacesMovedByAtkr:
        map(lambda x: x + 5, atkCombatBuffs)
        if atkHPGreaterEqual25Percent: atkPseudoMiracleEnabled

    if "I HATE FIRE JOKES >:(" in defSkills and spacesMovedByAtkr:
        map(lambda x: x + 5, defCombatBuffs)
        if defHPGreaterEqual25Percent: defPseudoMiracleEnabled

    if "WaitIsHeAGhost" in atkSkills and defHPGreaterEqual75Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        atkSkillFollowUps += 1

    if "WaitIsHeAGhost" in defSkills and atkHPGreaterEqual75Percent:
        map(lambda x: x + 5, defCombatBuffs)
        defSkillFollowUps += 1

    if "I'M STRONG AND YOU'RE TOAST" in atkSkills and atkHPGreaterEqual50Percent:
        atkCombatBuffs[1] += 4
        atkCombatBuffs[3] += 6
        defenderLossWhenAttacked -= 1
        defenderLossWhenAttacking -= 1

    if "I'M STRONG AND YOU'RE TOAST" in defSkills and defHPGreaterEqual50Percent:
        defCombatBuffs[1] += 4
        defCombatBuffs[3] += 6
        attackerLossWhenAttacked -= 1
        attackerLossWhenAttacking -= 1

    if "Ayragate" in atkSkills and defHPGreaterEqual75Percent:
        map(lambda x: x + 4, atkCombatBuffs)

    if "balmungBoost" in atkSkills and defHPEqual100Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        atkPenaltiesNeutralized = [True] * 5

    if "larceiEdge" in atkSkills and (atkStats[SPD] + atkPhantomStats[2] > defStats[SPD] + defPhantomStats[2] or defHPEqual100Percent):
        map(lambda x: x + 4, atkCombatBuffs)
        defBonusesNeutralized = [True] * 5

    if "larceiEdge" in defSkills and (atkStats[2] + atkPhantomStats[2] < defStats[2] + defPhantomStats[2] or atkHPEqual100Percent):
        map(lambda x: x + 4, defCombatBuffs)
        atkBonusesNeutralized = [True] * 5

    if "larceiEdge2" in atkSkills and atkStats[2] + atkPhantomStats[2] > defStats[2] + defPhantomStats[2] or defHPGreaterEqual75Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        defBonusesNeutralized = [True] * 5

    if "larceiEdge2" in defSkills and defStats[2] + defPhantomStats[2] > atkStats[2] + atkPhantomStats[2] or atkHPGreaterEqual75Percent:
        map(lambda x: x + 4, defCombatBuffs)
        atkBonusesNeutralized = [True] * 5

    if "infiniteSpecial" in atkSkills and atkHPGreaterEqual25Percent: map(lambda x: x + 4, atkCombatBuffs)
    if "infiniteSpecial" in defSkills and defHPGreaterEqual25Percent: map(lambda x: x + 4, defCombatBuffs)

    if "DRINK" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[3] += 5
        atkFixedSpDmgBoost += 7

    if "AMERICA" in atkSkills:
        NEWatkOtherDmg += 10
        defPostCombatStatusesApplied[2].append(Status.Flash)

    if "AMERICA" in defSkills:
        NEWdefOtherDmg += 10
        atkPostCombatStatusesApplied[2].append(Status.Flash)

    if "FREEDOM" in atkSkills and atkHPGreaterEqual25Percent: map(lambda x: x + 4, atkCombatBuffs)
    if "FREEDOM" in defSkills and defHPGreaterEqual25Percent: map(lambda x: x + 4, defCombatBuffs)

    if "MY TRAP! 🇺🇸" in atkSkills and atkAdjacentToAlly <= 1:
        map(lambda x: x + 4, atkCombatBuffs)
        defPostCombatStatusesApplied[2].append(Status.Discord)

    if "MY TRAP! 🇺🇸" in defSkills and defAdjacentToAlly <= 1:
        map(lambda x: x + 4, defCombatBuffs)
        defPostCombatStatusesApplied[2].append(Status.Discord)

    if "leafSword" in atkSkills and defHPEqual100Percent:
        atkCombatBuffs[2] += 4
        atkCombatBuffs[3] += 4

    if "theLand" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[1] += 6
        atkCombatBuffs[2] += 6
        atkAlwaysPierceDR = True
        atkPostCombatHealing += 7
        if defender.getSpecialType() == "Defense": defSpecialDisabled = True

    if "theLand" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[1] += 6
        defCombatBuffs[2] += 6
        defAlwaysPierceDR = True
        defPostCombatHealing += 7
        if attacker.getSpecialType() == "Defense": atkSpecialDisabled = True

    if "bigHands" in atkSkills and defHPGreaterEqual50Percent:
        atkCombatBuffs[1] += 5
        defCombatBuffs[1] -= 5
        atkSkillFollowUpDenials -= 1

    if "swagDesp" in atkSkills and atkHPGreaterEqual50Percent:
        desperateA = True

    if "swagDespPlus" in atkSkills and atkHPGreaterEqual25Percent:
        desperateA = True
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5
        if defStats[SPD] + defPhantomStats[SPD] > defStats[DEF] + defPhantomStats[DEF]: defCombatBuffs[2] -= 8
        else: defCombatBuffs[3] -= 8

    if "swagDespPlus" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[2] += 5
        if atkStats[SPD] + defPhantomStats[SPD] > atkStats[DEF] + defPhantomStats[DEF]: atkCombatBuffs[2] -= 8
        else: atkCombatBuffs[3] -= 8

    if "swagDespPlusPlus" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5

    if "swagDespPlusPlus" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[2] += 5

    if "spectrumSolo" in atkSkills and not atkAdjacentToAlly:
        map(lambda x: x + 4, atkCombatBuffs)

    if "spectrumSolo" in defSkills and not defAdjacentToAlly:
        map(lambda x: x + 4, defCombatBuffs)

    if "mareeeeta" in atkSkills and atkAdjacentToAlly <= 1:
        map(lambda x: x + 4, atkCombatBuffs)
        defBonusesNeutralized[SPD], defBonusesNeutralized[DEF] = True

    if "mareeeeta" in defSkills and defAdjacentToAlly <= 1:
        map(lambda x: x + 4, defCombatBuffs)
        atkBonusesNeutralized[SPD], atkBonusesNeutralized[DEF] = True

    if "moreeeeta" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        atkSpPierceDR = True

    if "moreeeeta" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)
        defSpPierceDR = True

    if "ascendingBlade" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        atkPostCombatSpCharge += 1

    if "ascendingBlade" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 5, defCombatBuffs)
        defPostCombatSpCharge += 1

    if "ROY'S OUR BOY" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        attackerGainWhenAttacking += 1
        attackerGainWhenAttacked += 1

    if "ROY'S OUR BOY" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)
        defenderGainWhenAttacking += 1
        defenderGainWhenAttacked += 1

    if "wanderer" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "like the university" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "wanderer" in defSkills and atkHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "like the university" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    if "elistats" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)

    if "elistats" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)

    if "hamburger" in atkSkills:
        map(lambda x: x + 4, atkCombatBuffs)
        defBonusesNeutralized = [True] * 5

    if "hamburger" in defSkills and defAllyWithin2Spaces:
        map(lambda x: x + 4, defCombatBuffs)
        atkBonusesNeutralized = [True] * 5

    if ("curiosBoost" in atkSkills or "reduFU" in atkSkills) and turn % 2 == 1 or not defHPEqual100Percent:
        map(lambda x: x + 4, atkCombatBuffs)

    if ("curiosBoost" in defSkills or "reduFU" in defSkills) and turn % 2 == 1 or not atkHPEqual100Percent:
        map(lambda x: x + 4, defCombatBuffs)

    if "oho dad" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)

        defCombatBuffs[1] -= math.trunc(atkStats[ATK] * 0.1)
        defCombatBuffs[3] -= math.trunc(atkStats[ATK] * 0.1)

        atkPostCombatHealing += 7

    if "oho dad" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)

        atkCombatBuffs[1] -= math.trunc(defStats[ATK] * 0.1)
        atkCombatBuffs[3] -= math.trunc(defStats[ATK] * 0.1)

        atkPostCombatHealing += 7


    if "garbageSword" in atkSkills and defHPEqual100Percent:
        atkCombatBuffs[1] += atkSkills["garbageSword"]
        atkCombatBuffs[2] += atkSkills["garbageSword"]

    if "Hi Nino" in atkSkills:
        allyMagic2Spaces = 0
        if allyMagic2Spaces: map(lambda x: x + 3, atkCombatBuffs)

    if "vassalBlade" in atkSkills:
        atkCombatBuffs[SPD] += 5

    if "Barry B. Benson" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5

    if "bonusInheritor" in atkSkills: #eirika, should be highest bonus for each given stat on allies within 2 spaces
        atkCombatBuffs[1] += 0
        atkCombatBuffs[2] += 0
        atkCombatBuffs[3] += 0
        atkCombatBuffs[4] += 0

    if "stormSieglinde" in atkSkills and atkFoeWithin2Spaces >= atkAllyWithin2Spaces:
        atkCombatBuffs[3] += 3
        atkCombatBuffs[4] += 3
        attackerGainWhenAttacking += 1

    if "stormSieglinde2" in atkSkills:
        map(lambda x: x + 4, atkCombatBuffs)
        attackerGainWhenAttacking += 1
        attackerGainWhenAttacked += 1

    if "stormSieglinde2" in defSkills and not defAdjacentToAlly:
        map(lambda x: x + 4, defCombatBuffs)
        defenderGainWhenAttacking += 1
        defenderGainWhenAttacked += 1

    if "Just Lean" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)

    if "Just Lean" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)

    if "renaisTwins" in atkSkills:
        map(lambda x: x + 4, atkCombatBuffs)

    if "renaisTwins" in defSkills and defAllyWithin2Spaces:
        map(lambda x: x + 4, defCombatBuffs)

    if "audBoost" in atkSkills and defHPEqual100Percent:
        map(lambda x: x + 4, atkCombatBuffs)

    if "hey all scott here" in atkSkills:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5

    if "hey all scott here" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[1] += 5
        defCombatBuffs[2] += 5

    if ("I fight for my friends" in atkSkills or "WILLYOUSURVIVE?" in atkSkills) and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)

    if "sturdyWarrr" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        if attacker.getSpecialType() == "Offense":
            if atkAllyWithin4Spaces >= 1:
                atkSpChargeBeforeFirstStrike += math.trunc(attacker.getMaxSpecialCooldown()/2)
            if atkAllyWithin4Spaces >= 3:
                atkNullDefFU, atkDoSkillFU = True

    if "sturdyWarrr" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 5, defCombatBuffs)
        if defender.getSpecialType() == "Offense":
            if defAllyWithin4Spaces >= 1:
                defSpChargeBeforeFirstStrike += math.trunc(defender.getMaxSpecialCooldown()/2)
            if defAllyWithin4Spaces >= 3:
                defNullAtkFU, defDoSkillFU = True

    if "pointySword" in atkSkills: map(lambda x: x + 5, atkCombatBuffs)
    if "pointySword" in defSkills and defAllyWithin2Spaces: map(lambda x: x + 5, atkCombatBuffs)

    if "TWO?" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[4] += 5
        attackerGainWhenAttacked += 1
        attackerGainWhenAttacking += 1
        defBonusesNeutralized[ATK] = True
        defBonusesNeutralized[DEF] = True

    if "TWO?" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[4] += 5
        defenderGainWhenAttacked += 1
        defenderGainWhenAttacking += 1
        atkBonusesNeutralized[ATK] = True
        atkBonusesNeutralized[DEF] = True

    # yeah we'll be here for a while
    if "You get NOTHING" in atkSkills:
        atkDoSkillFU = 0
        atkNullDefFU = 0
        defDoSkillFU = 0
        defNullAtkFU = 0
        atkSpecialDisabled = True
        defSpecialDisabled = True
        atkDefensiveTerrain = False
        defDefensiveTerrain = False
        hardyBearingAtk = True
        hardyBearingDef = True
        if atkHPGreaterEqual25Percent: map(lambda x: x + 5, atkCombatBuffs)

    if "You get NOTHING" in defSkills:
        atkDoSkillFU = 0
        atkNullDefFU = 0
        defDoSkillFU = 0
        defNullAtkFU = 0
        atkSpecialDisabled = True
        defSpecialDisabled = True
        atkDefensiveTerrain = False
        defDefensiveTerrain = False
        hardyBearingAtk = True
        hardyBearingDef = True
        if defHPGreaterEqual25Percent: map(lambda x: x + 5, defCombatBuffs)

    if "spectrumBond" in atkSkills and atkAdjacentToAlly: # awakening falchion
        map(lambda x: x + atkSkills["spectrumBond"], atkCombatBuffs)

    if "sealedFalchion" in atkSkills and not atkHPEqual100Percent:
        map(lambda x: x + 5, atkCombatBuffs)

    if "newSealedFalchion" in atkSkills and (not atkHPEqual100Percent or atkHasBonus):
        map(lambda x: x + 5, atkCombatBuffs)

    if "I CANT STOP THIS THING" in atkSkills and defHPGreaterEqual75Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        defSkillFollowUpDenials -= 1

    if "refineExtra" in atkSkills and defHPGreaterEqual50Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5

    if "Sacred Stones Strike!" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5

    if "ancientRagnell" in atkSkills and (atkHPGreaterEqual50Percent or atkHasBonus):
        defCombatBuffs[1] -= 6
        defCombatBuffs[3] -= 6

    if "ancientRagnell" in defSkills and (defHPGreaterEqual50Percent or defHasBonus):
        atkCombatBuffs[1] -= 6
        atkCombatBuffs[3] -= 6

    if "lioness" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[1] += 6
        atkCombatBuffs[2] += 6
        atkSpPierceDR = True
        if defHPGreaterEqual75Percent:
            attackerGainWhenAttacked += 1
            attackerGainWhenAttacked += 1

    if "lioness" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[1] += 6
        defCombatBuffs[2] += 6
        defSpPierceDR = True
        if atkHPGreaterEqual75Percent:
            defenderGainWhenAttacked += 1
            defenderGainWhenAttacked += 1

    if "waitTurns" in atkSkills: #ryoma
        map(lambda x:x+4, atkCombatBuffs)

    if "xanderific" in atkSkills and defHPGreaterEqual75Percent:
        defCombatBuffs[1] -= 5
        defCombatBuffs[3] -= 5
        defSkillFollowUpDenials -= 1

    if "Toaster" in atkSkills and not atkAdjacentToAlly:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5
        atkPenaltiesNeutralized = [True] * 5

    if "lowAtkBoost" in atkSkills and defStats[ATK] + defPhantomStats[ATK] >= atkStats[ATK] + atkPhantomStats[ATK] + 3:
        map(lambda x:x+3, atkCombatBuffs)

    if "lowAtkBoost" in defSkills and atkStats[ATK] + atkPhantomStats[ATK] >= defStats[ATK] + defPhantomStats[ATK] + 3:
        map(lambda x:x+3, defCombatBuffs)

    # If Laslow is within 3 spaces of at least 2 allies who each have total stat buffs >= 10
    if "laslowBrave" in atkSkills:
        theLaslowCondition = False
        if theLaslowCondition:
            atkCombatBuffs[1] += 3
            atkCombatBuffs[3] += 3
            braveATKR = True

    if "laslowBrave" in defSkills:
        theLaslowCondition = False
        if theLaslowCondition:
            defCombatBuffs[1] += 3
            defCombatBuffs[3] += 3
            braveDEFR = True

    if "ladies, whats good" in atkSkills:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5
        attackerGainWhenAttacking += 1

    if "up b bair" in atkSkills: map(lambda x:x+4, atkCombatBuffs)
    if "up b bair" in defSkills and defAllyWithin2Spaces: map(lambda x:x+4, defCombatBuffs)

    if "HERE'S SOMETHING TO BELIEVE IN" in atkSkills:
        atkSpPierceDR = True
        if atkHPGreaterEqual25Percent: map(lambda x:x+4, atkCombatBuffs)

    if "HERE'S SOMETHING TO BELIEVE IN" in defSkills:
        defSpPierceDR = True
        if defHPGreaterEqual25Percent: map(lambda x:x+4, defCombatBuffs)

    if "regalSunshade" in atkSkills and atkHPGreaterEqual25Percent:
        numFoesLeft = 0
        numFoesWithin3Columns3Rows = 0
        atkCombatBuffs[1] += 6
        atkCombatBuffs[3] += 6
        X = 1 if numFoesLeft <= 2 else (2 if 3 <= numFoesLeft <= 5 else 3)
        if X <= numFoesWithin3Columns3Rows: braveATKR = True

    if "regalSunshade" in defSkills and defHPGreaterEqual25Percent:
        numFoesLeft = 0
        numFoesWithin3Columns3Rows = 0
        defCombatBuffs[1] += 6
        defCombatBuffs[3] += 6
        X = 1 if numFoesLeft <= 2 else (2 if 3 <= numFoesLeft <= 5 else 3)
        if X <= numFoesWithin3Columns3Rows: braveDEFR = True

    # Catherine: Thunderbrand

    if "thundabrand" in atkSkills and defHPGreaterEqual50Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5
        desperateA = True

    if "thundabrand" in defSkills and atkHPGreaterEqual50Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[1] += 5

    # Nemesis: Dark Creator S
    if "DCSIYKYK" in atkSkills:
        atkCombatBuffs[1] += 2 * atkNumAlliesHPGE90Percent
        atkCombatBuffs[3] += 2 * defNumAlliesHPGE90Percent

    if "TMSFalchion" in atkSkills:
        atkCombatBuffs[1] += min(3 + 2 * 00000, 7) # 00000 - number of allies who have acted
        atkCombatBuffs[3] += min(3 + 2 * 00000, 7)

    if "TMSFalchion" in defSkills:
        atkCombatBuffs[1] += max(3, 7 - 000000 * 2) # 000000 - number of foes who have acted
        atkCombatBuffs[3] += max(3, 7 - 000000 * 2)

    # 00000 and 000000 should be equal

    if "Garfield You Fat Cat" in atkSkills:
        atkCombatBuffs[1] += min(4 + 3 * 00000, 10)  # 00000 - number of allies who have acted
        atkCombatBuffs[2] += min(4 + 3 * 00000, 10)
        atkCombatBuffs[3] += min(4 + 3 * 00000, 10)
        atkCombatBuffs[4] += min(4 + 3 * 00000, 10)
        atkPostCombatHealing += 7

    if "Garfield You Fat Cat" in defSkills:
        defCombatBuffs[1] += max(4, 10 - 000000 * 3)  # 000000 - number of foes who have acted
        defCombatBuffs[2] += max(4, 10 - 000000 * 3)
        defCombatBuffs[3] += max(4, 10 - 000000 * 3)
        defCombatBuffs[4] += max(4, 10 - 000000 * 3)
        defPostCombatHealing += 7

    if "Nintendo has forgotten about Mario…" in atkSkills:
        map(lambda x:x+4, atkCombatBuffs)
        atkSkillFollowUps += 1

    if "Nintendo has forgotten about Mario…" in defSkills or defAllyWithin2Spaces:
        map(lambda x:x+4, defCombatBuffs)
        defSkillFollowUps += 1

    if "BONDS OF FIIIIRE, CONNECT US" in atkSkills and atkHPGreaterEqual25Percent:
        titlesAmongAllies = 0
        atkCombatBuffs = list(map(lambda x: x + 5, atkCombatBuffs))
        defCombatBuffs[SPD] -= min(4 + titlesAmongAllies * 2, 12)
        defCombatBuffs[DEF] -= min(4 + titlesAmongAllies * 2, 12)

    if "BONDS OF FIIIIRE, CONNECT US" in defSkills and defHPGreaterEqual25Percent:
        titlesAmongAllies = 0
        map(lambda x: x + 5, defCombatBuffs)
        atkCombatBuffs[SPD] -= min(4 + titlesAmongAllies * 2, 12)
        atkCombatBuffs[DEF] -= min(4 + titlesAmongAllies * 2, 12)

    if "LOVE PROVIIIIDES, PROTECTS US" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        defenderLossWhenAttacking -= 1
        defenderLossWhenAttacked -= 1

    if "LOVE PROVIIIIDES, PROTECTS US" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 5, defCombatBuffs)
        attackerLossWhenAttacking -= 1
        attackerLossWhenAttacked -= 1

    if "laevBoost" in atkSkills and (atkHasBonus or atkHPGreaterEqual50Percent):
        atkCombatBuffs[1] += 5
        atkCombatBuffs[3] += 5

    if "laevPartner" in atkSkills and defHPGreaterEqual75Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[3] += 5

    if "niuBoost" in atkSkills and atkHPGreaterEqual25Percent: map(lambda x: x + 4, atkCombatBuffs)

    if "ICE UPON YOU" in atkSkills and defHasPenalty:
        atkSkillFollowUps += 1
        defSkillFollowUps -= 1

    if "ICE UPON YOU" in defSkills and atkHasPenalty:
        defSkillFollowUps += 1
        atkSkillFollowUps -= 1

    if "FREEZE NOW" in atkSkills and (atkHPGreaterEqual25Percent or defHasPenalty):
        defCombatBuffs[1] -= 5
        defCombatBuffs[3] -= 5

    if "FREEZE NOW" in defSkills and (defHPGreaterEqual25Percent or atkHasPenalty):
        atkCombatBuffs[1] -= 5
        atkCombatBuffs[3] -= 5

    if "hikamiThreaten2" in atkSkills and atkHPGreaterEqual25Percent:
        defCombatBuffs[1] -= 4
        defCombatBuffs[2] -= 4
        defCombatBuffs[3] -= 4

    if "hikamiThreaten2" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[1] -= 4
        atkCombatBuffs[2] -= 4
        atkCombatBuffs[3] -= 4

    if "https://youtu.be/eVTXPUF4Oz4?si=RkBGT1Gf1bGBxOPK" in atkSkills and atkAllyWithin3Spaces:
        map(lambda x: x + 4, atkCombatBuffs)
        atkSkillFollowUps += 1

    if "https://youtu.be/eVTXPUF4Oz4?si=RkBGT1Gf1bGBxOPK" in defSkills and defAllyWithin3Spaces:
        map(lambda x: x + 4, defCombatBuffs)
        defSkillFollowUps += 1

    if "https://www.youtube.com/watch?v=Gd9OhYroLN0&pp=ygUUY3Jhd2xpbmcgbGlua2luIHBhcms%3D" in atkSkills and atkAllyWithin4Spaces:
        map(lambda x: x + 6, atkCombatBuffs)
        atkSkillFollowUps += 1
        atkFinishTrueDamage += 5
        atkFinishMidCombatHeal += 7

    if "https://www.youtube.com/watch?v=Gd9OhYroLN0&pp=ygUUY3Jhd2xpbmcgbGlua2luIHBhcms%3D" in defSkills and defAllyWithin4Spaces:
        map(lambda x: x + 6, defCombatBuffs)
        defSkillFollowUps += 1
        defFinishTrueDamage += 5
        defFinishMidCombatHeal += 7

    if "ow" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)

    if "ow" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)

    if "zzzzzzzzzzzzzzzz" in atkSkills and (defender.hasPenalty() or defHPGreaterEqual75Percent):
        defCombatBuffs[1] -= 5
        defCombatBuffs[3] -= 5

    if "zzzzzzzzzzzzzzzz" in defSkills and (attacker.hasPenalty() or atkHPGreaterEqual75Percent):
        atkCombatBuffs[1] -= 5
        atkCombatBuffs[3] -= 5

    if "sleepy head" in atkSkills and atkHPGreaterEqual25Percent:
        defCombatBuffs[1] -= 5
        defCombatBuffs[3] -= 5
        atkSkillFollowUps += 1
        defPostCombatStatusesApplied[2].append(Status.Flash)

    if "sleepy head" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[1] -= 5
        atkCombatBuffs[3] -= 5
        defSkillFollowUps += 1
        atkPostCombatStatusesApplied[2].append(Status.Flash)

    if "Mario":
        "only Bros!"

    if "selfDmg" in atkSkills:  # damage to self after combat always
        atkSelfDmg += atkSkills["selfDmg"]

    if "atkOnlySelfDmg" in atkSkills:  # damage to attacker after combat iff attacker had attacked
        atkRecoilDmg += atkSkills["atkOnlySelfDmg"]

    if "atkOnlyOtherDmg" in atkSkills: # damage to other unit after combat iff attacker had attacked
        NEWatkOtherDmg += atkSkills["atkOnlyOtherDmg"]


    if "triAdeptS" in atkSkills and atkSkills["triAdeptS"] > triAdept: triAdept = atkSkills["triAdeptS"]
    if "triAdeptW" in atkSkills and atkSkills["triAdeptW"] > triAdept: triAdept = atkSkills["triAdeptW"]

    if "owlBoost" in atkSkills:
        map(lambda x: x + 2 * atkAdjacentToAlly, atkCombatBuffs)

    if "FollowUpEph" in atkSkills and atkHPCur / atkStats[0] > 0.90: atkSkillFollowUps += 1

    if "BraveAW" in atkSkills or "BraveAS" in atkSkills or "BraveBW" in atkSkills: braveATKR = True

    if "swordBreak" in atkSkills and defender.wpnType == "Sword" and atkHPCur / atkStats[0] > 1.1 - (atkSkills["swordBreak"] * 0.2): atkSkillFollowUps += 1; defSkillFollowUpDenials -= 1
    if "lanceBreak" in atkSkills and defender.wpnType == "Lance" and atkHPCur / atkStats[0] > 1.1 - (atkSkills["lanceBreak"] * 0.2): atkSkillFollowUps += 1; defSkillFollowUpDenials -= 1
    if "axeBreak" in atkSkills and defender.wpnType == "Axe" and atkHPCur / atkStats[0] > 1.1 - (atkSkills["axeBreak"] * 0.2): atkSkillFollowUps += 1; defSkillFollowUpDenials -= 1
    if "rtomeBreak" in atkSkills and defender.wpnType == "RTome" and atkHPCur / atkStats[0] > 1.1 - (atkSkills["rtomeBreak"] * 0.2): atkSkillFollowUps += 1; defSkillFollowUpDenials -= 1
    if "btomeBreak" in atkSkills and defender.wpnType == "BTome" and atkHPCur / atkStats[0] > 1.1 - (atkSkills["btomeBreak"] * 0.2): atkSkillFollowUps += 1; defSkillFollowUpDenials -= 1
    if "gtomeBreak" in atkSkills and defender.wpnType == "GTome" and atkHPCur / atkStats[0] > 1.1 - (atkSkills["gtomeBreak"] * 0.2): atkSkillFollowUps += 1; defSkillFollowUpDenials -= 1
    if "cBowBreak" in atkSkills and defender.wpnType == "CBow" and atkHPCur / atkStats[0] > 1.1 - (atkSkills["cBowBreak"] * 0.2): atkSkillFollowUps += 1; defSkillFollowUpDenials -= 1
    if "cDaggerBreak" in atkSkills and defender.wpnType == "CDagger" and atkHPCur / atkStats[0] > 1.1 - (atkSkills["cDaggerBreak"] * 0.2): atkSkillFollowUps += 1; defSkillFollowUpDenials -= 1

    if "spDamageAdd" in atkSkills: atkFixedSpDmgBoost += atkSkills["spDamageAdd"]

    if "firesweep" in atkSkills or "firesweep" in defSkills:
        cannotCounter = True

    if "hardyBearing" in atkSkills:
        hardyBearingAtk = True
        hardyBearingDef = atkHPCur/atkStats[0] >= 1.5 - (atkSkills["hardyBearing"] * .5)

    if "cancelTA" in atkSkills: atkCA = atkSkills["cancelTA"]

    # pseudo-miracle (the seliph zone)

    if "pseudoMiracle" in atkSkills and atkHPGreaterEqual50Percent:
        atkPseudoMiracleEnabled = True

    if "NO MORE LOSSES" in defSkills and defAllyWithin3Spaces and defHPGreaterEqual50Percent:
        defPseudoMiracleEnabled = True

    atkSpEffects = {}

    for key in atkSkills:
        # special tags
        if key == "healSelf": atkSpEffects.update({"healSelf": atkSkills[key]})
        if key == "defReduce": atkSpEffects.update({"defReduce": atkSkills[key]})
        if key == "dmgBoost": atkSpEffects.update({"dmgBoost": atkSkills[key]})
        if key == "atkBoostSp": atkSpEffects.update({"atkBoost": atkSkills[key]})
        if key == "defBoostSp": atkSpEffects.update({"defBoost": atkSkills[key]})
        if key == "resBoostSp": atkSpEffects.update({"resBoost": atkSkills[key]})
        if key == "closeShield": atkSpEffects.update({"closeShield": atkSkills[key]})
        if key == "distantShield": atkSpEffects.update({"distantShield": atkSkills[key]})
        if key == "miracleSP": atkSpEffects.update({"distantShield": atkSkills[key]})

    if "atkStance" in defSkills: defCombatBuffs[1] += defSkills["atkStance"] * 2
    if "spdStance" in defSkills: defCombatBuffs[2] += defSkills["spdStance"] * 2
    if "defStance" in defSkills: defCombatBuffs[3] += defSkills["defStance"] * 2
    if "resStance" in defSkills: defCombatBuffs[4] += defSkills["resStance"] * 2
    if "draugBlade" in defSkills: atkCombatBuffs[ATK] -= 6

    if "fireBoost" in defSkills and defHPCur >= atkHPCur + 3: defCombatBuffs[1] += defSkills["fireBoost"] * 2
    if "windBoost" in defSkills and defHPCur >= atkHPCur + 3: defCombatBuffs[2] += defSkills["windBoost"] * 2
    if "earthBoost" in defSkills and defHPCur >= atkHPCur + 3: defCombatBuffs[3] += defSkills["earthBoost"] * 2
    if "waterBoost" in defSkills and defHPCur >= atkHPCur + 3: defCombatBuffs[4] += defSkills["waterBoost"] * 2

    if "closeDef" in defSkills and attacker.weapon.range == 1:
        defCombatBuffs[3] += defSkills["distDef"] * 2
        defCombatBuffs[4] += defSkills["distDef"] * 2

    if "distDef" in defSkills and attacker.weapon.range == 2:
        defCombatBuffs[3] += defSkills["distDef"] * 2
        defCombatBuffs[4] += defSkills["distDef"] * 2

    if "brazenAtk" in defSkills and defHPCur / defStats[HP] <= 0.8: defCombatBuffs[1] += defSkills["brazenAtk"]
    if "brazenSpd" in defSkills and defHPCur / defStats[HP] <= 0.8: defCombatBuffs[2] += defSkills["brazenSpd"]
    if "brazenDef" in defSkills and defHPCur / defStats[HP] <= 0.8: defCombatBuffs[3] += defSkills["brazenDef"]
    if "brazenRes" in defSkills and defHPCur / defStats[HP] <= 0.8: defCombatBuffs[4] += defSkills["brazenRes"]

    if "ILOVEBONUSES" in defSkills and defHPGreaterEqual50Percent or atkHasBonus: #UPDATE WITH DEF SKILLS
        map(lambda x: x + 4, defCombatBuffs)

    if "spectrumBond" in defSkills and defAdjacentToAlly:
        map(lambda x: x + defSkills["spectrumBond"], defCombatBuffs)

    if ("belovedZofia" in defSkills and defHPEqual100Percent) or "belovedZofia2" in defSkills:
        map(lambda x: x + 4, defCombatBuffs)
        defRecoilDmg += 4

    if "ALMMM" in defSkills and (not atkHPEqual100Percent or not defHPEqual100Percent):
        map(lambda x: x + 4, defCombatBuffs)
        defMidCombatHeal += 7

    if "A man has fallen into the river in LEGO City!" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)
        defPostCombatHealing += 7

    if "berkutBoost" in defSkills:
        defCombatBuffs[1] += 5
        defCombatBuffs[3] += 5
        defCombatBuffs[4] += 5

    if "baseTyrfing" in defSkills and defHPCur / defStats[0] <= 0.5:
        defCombatBuffs[3] += 4

    if "refDivTyrfing" in defSkills and atkHPGreaterEqual50Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[3] += 5

    if "WE MOVE" in defSkills and defHPGreaterEqual50Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[3] += 5
        defSkillFollowUps += 1

    if "Ayragate" in defSkills and atkHPGreaterEqual75Percent:
        map(lambda x: x + 4, defCombatBuffs)

    if "DRINK" in defSkills:
        defCombatBuffs[1] += 5
        defCombatBuffs[3] += 5
        defFixedSpDmgBoost += 7

    if "leafSword" in defSkills and atkHPEqual100Percent:
        defCombatBuffs[2] += 4
        defCombatBuffs[3] += 4

    if "bigHands" in defSkills and atkHPGreaterEqual50Percent:
        defCombatBuffs[1] += 5
        atkCombatBuffs[1] -= 5

    if "garbageSword" in defSkills and atkHPEqual100Percent:
        defCombatBuffs[1] += defSkills["garbageSword"]
        defCombatBuffs[2] += defSkills["garbageSword"]

    if "Hi Nino" in defSkills:
        allyMagic2Spaces = 0
        if allyMagic2Spaces: map(lambda x: x + 3, defCombatBuffs)

    if "vassalBlade" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[2] += 5

    if "Barry B. Benson" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[2] += 5

    if "bonusInheritor" in defSkills: #eirika, should be highest bonus for each given stat on allies within 2 spaces
        defCombatBuffs[1] += 0
        defCombatBuffs[2] += 0
        defCombatBuffs[3] += 0
        defCombatBuffs[4] += 0

    if "stormSieglinde" in defSkills and defNumFoesWithin2Spaces >= defNumAlliesWithin2Spaces:
        defCombatBuffs[3] += 3
        defCombatBuffs[4] += 3
        defenderGainWhenAttacking += 1

    if "audBoost" in defSkills:
        map(lambda x: x + 4, defCombatBuffs)

    if ("I fight for my friends" in defSkills or "WILLYOUSURVIVE?" in defSkills) and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)

    if "sealedFalchion" in defSkills and not atkHPEqual100Percent:
        map(lambda x: x + 5, defCombatBuffs)

    if "newSealedFalchion" in defSkills and (not defHPEqual100Percent or defHasBonus):
        map(lambda x: x + 5, defCombatBuffs)

    if "I CANT STOP THIS THING" in defSkills and atkHPGreaterEqual75Percent:
        map(lambda x: x + 5, defCombatBuffs)
        atkSkillFollowUpDenials -= 1

    if "refineExtra" in defSkills and atkHPGreaterEqual50Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[2] += 5

    if "Sacred Stones Strike!" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[1] += 5
        defCombatBuffs[2] += 5

    if "amatsuDC" in defSkills and defHPGreaterEqual50Percent:
        ignoreRng = True

    if "waitTurns" in defSkills and defAllyWithin2Spaces:
        map(lambda x: x + 4, defCombatBuffs)

    if "xanderific" in defSkills and atkHPGreaterEqual75Percent:
        atkCombatBuffs[1] -= 5
        atkCombatBuffs[3] -= 5
        atkSkillFollowUpDenials -= 1

    if "Toaster" in defSkills and not defAdjacentToAlly:
        defCombatBuffs[1] += 5
        defCombatBuffs[2] += 5
        defPenaltiesNeutralized = [True] * 5

    if "laevBoost" in defSkills and (defHasBonus or atkHPGreaterEqual50Percent):
        defCombatBuffs[1] += 5
        defCombatBuffs[3] += 5

    if "laevPartner" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[3] += 5

    if "niuBoost" in defSkills and defHPGreaterEqual25Percent: map(lambda x: x + 4, defCombatBuffs)

    if "triAdeptS" in defSkills and defSkills["triAdeptS"] > triAdept: triAdept = defSkills["triAdeptS"]
    if "triAdeptW" in defSkills and defSkills["triAdeptW"] > triAdept: triAdept = defSkills["triAdeptW"]

    if "cCounter" in defSkills or "dCounter" in defSkills: ignoreRng = True
    if "BraveDW" in defSkills or "BraveBW" in defSkills: braveDEFR = True

    if "selfDmg" in defSkills: defSelfDmg += defSkills["selfDmg"]

    if "atkOnlySelfDmg" in defSkills: defRecoilDmg += defSkills["atkOnlySelfDmg"]
    if "atkOnlyOtherDmg" in defSkills: NEWdefOtherDmg += defSkills["atkOnlyOtherDmg"]

    if "QRW" in defSkills and defHPCur / defStats[0] >= 1.0 - (defSkills["QRW"] * 0.1): defSkillFollowUps += 1
    if "QRS" in defSkills and defHPCur / defStats[0] >= 1.0 - (defSkills["QRS"] * 0.1): defSkillFollowUps += 1

    if "desperation" in defSkills and defHPCur / defStats[0] <= 0.25 * defSkills["desperation"]: desperateA = True

    if "swordBreak" in defSkills and attacker.wpnType == "Sword": defSkillFollowUps += 1; atkSkillFollowUpDenials -= 1
    if "lanceBreak" in defSkills and attacker.wpnType == "Lance": defSkillFollowUps += 1; atkSkillFollowUpDenials -= 1
    if "axeBreak" in defSkills and attacker.wpnType == "Axe": defSkillFollowUps += 1; atkSkillFollowUpDenials -= 1
    if "rtomeBreak" in defSkills and attacker.wpnType == "RTome": defSkillFollowUps += 1; atkSkillFollowUpDenials -= 1
    if "btomeBreak" in defSkills and attacker.wpnType == "BTome": defSkillFollowUps += 1; atkSkillFollowUpDenials -= 1
    if "gtomeBreak" in defSkills and attacker.wpnType == "GTome": defSkillFollowUps += 1; atkSkillFollowUpDenials -= 1
    if "cBowBreak" in defSkills and attacker.wpnType == "CBow": defSkillFollowUps += 1; atkSkillFollowUpDenials -= 1
    if "cDaggerBreak" in defSkills and attacker.wpnType == "CDagger": defSkillFollowUps += 1; atkSkillFollowUpDenials -= 1

    if "spDamageAdd" in defSkills: defFixedSpDmgBoost += defSkills["spDamageAdd"]

    if "vantage" in defSkills and defHPCur / defStats[0] <= 0.75 - (0.25 * (3 - defSkills["vantage"])):
        vantageEnabled = True

    if Status.Vantage in defender.statusNeg:
        vantageEnabled = True

    if "cancelTA" in defSkills:
        defCA = defSkills["cancelTA"]

    if "pseudoMiracle" in defSkills and defHPGreaterEqual50Percent:
        defPseudoMiracleEnabled = True

    defSpEffects = {}
    for key in defSkills:
        if key == "healSelf": defSpEffects.update({"healSelf": defSkills[key]})
        if key == "defReduce": defSpEffects.update({"defReduce": defSkills[key]})
        if key == "dmgBoost": defSpEffects.update({"dmgBoost": defSkills[key]})
        if key == "resBoostSp": defSpEffects.update({"resBoost": defSkills[key]})
        if key == "closeShield": defSpEffects.update({"closeShield": defSkills[key]})
        if key == "distantShield": defSpEffects.update({"distantShield": defSkills[key]})
        if key == "miracleSP": defSpEffects.update({"miracleSP": defSkills[key]})

    # LITERALLY EVERYTHING THAT USES EXACT BONUS AND PENALTY VALUES GOES HERE

    if "dominance" in atkSkills and AtkPanicFactor == 1:
        for i in range(1,5): atkCombatBuffs[1] += attacker.buffs[i] * atkBonusesNeutralized[i]

    if "dominance" in defSkills and DefPanicFactor == 1:
        for i in range(1,5): defCombatBuffs[1] += defender.buffs[i] * defBonusesNeutralized[i]

    if "bonusDoublerW" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] += math.trunc(max(AtkPanicFactor * attacker.buffs[i] * atkBonusesNeutralized[i], 0) * 0.25 * atkSkills["bonusDoublerW"] + 0.25)

    if "bonusDoublerSk" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] += math.trunc(max(AtkPanicFactor * attacker.buffs[i] * atkBonusesNeutralized[i], 0) * 0.25 * atkSkills["bonusDoublerSk"] + 0.25)

    if "bonusDoublerSe" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] += math.trunc(max(AtkPanicFactor * attacker.buffs[i] * atkBonusesNeutralized[i], 0) * 0.25 * atkSkills["bonusDoublerSe"] + 0.25)

    if Status.BonusDoubler in attacker.statusPos:
        for i in range(1,5):
            atkCombatBuffs[i] += max(AtkPanicFactor * attacker.buffs[i] * atkBonusesNeutralized[i], 0)

    if "bonusDoublerW" in defSkills:
        for i in range(1,5):
            defCombatBuffs[i] += math.trunc(max(DefPanicFactor * defender.buffs[i] * defBonusesNeutralized[i], 0) * 0.25 * defSkills["bonusDoublerW"] + 0.25)

    if "bonusDoublerSk" in atkSkills: #UPDATE WITH DEF SKILLS
        for i in range(1, 5):
            defCombatBuffs[i] += math.trunc(max(DefPanicFactor * defender.buffs[i] * defBonusesNeutralized[i], 0) * 0.25 * defSkills["bonusDoublerSk"] + 0.25)

    if "bonusDoublerSe" in atkSkills: #UPDATE WITH DEF SKILLS
        for i in range(1,5):
            defCombatBuffs[i] += math.trunc(max(DefPanicFactor * defender.buffs[i] * defBonusesNeutralized[i], 0) * 0.25 * defSkills["bonusDoublerSe"] + 0.25)

    if Status.BonusDoubler in defender.statusPos:
        for i in range(1, 5):
            defCombatBuffs[i] += max(DefPanicFactor * defender.buffs[i] * defBonusesNeutralized[i], 0)

    if "I think that enemy got THE POINT" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        for i in range(1,5): atkCombatBuffs[i] += max(attacker.buffs[i] * AtkPanicFactor * atkBonusesNeutralized[i], 0)
        defenderLossWhenAttacked -= 1
        defenderLossWhenAttacking -= 1

    if "I think that enemy got THE POINT" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 5, defCombatBuffs)
        for i in range(1,5): defCombatBuffs[i] += max(defender.buffs[i] * DefPanicFactor * defBonusesNeutralized[i], 0)
        attackerLossWhenAttacked -= 1
        attackerLossWhenAttacking -= 1

    if "gregorSword!" in atkSkills:
        for i in range(1,5):
            defCombatBuffs -= 5 + max(defender.debuffs[i] * defPenaltiesNeutralized[i] * -1, 0) + max(defender.buffs[i] * DefPanicFactor * defPenaltiesNeutralized[i] * -1, 0)

    if "gregorSword!" in defSkills and defAllyWithin2Spaces:
        for i in range(1,5):
            atkCombatBuffs -= 5 + max(attacker.debuffs[i] * atkPenaltiesNeutralized[i] * -1, 0) + max(attacker.buffs[i] * AtkPanicFactor * atkPenaltiesNeutralized[i] * -1, 0)

    if "GiveMeYourBonuses" in atkSkills and DefPanicFactor == 1:
        totalBonuses = 0
        for i in range(1,5): totalBonuses += defender.buffs[i] * defBonusesNeutralized[i]
        map(lambda x: x + math.trunc(totalBonuses/2), atkCombatBuffs)

    if "ILoveBonusesAndWomenAndI'mAllOutOfBonuses" in atkSkills:
        tempAtkBonuses = 0
        tempDefBonuses = 0
        if AtkPanicFactor == 1:
            for i in range(1,5): tempAtkBonuses += attacker.buffs[i] + atkBonusesNeutralized[i]
        if DefPanicFactor == 1:
            for i in range(1,5): tempDefBonuses += defender.buffs[i] + defBonusesNeutralized[i]
        tempTotalBonuses = min(10, math.trunc((tempAtkBonuses + tempDefBonuses) * 0.4))
        map(lambda x: x + tempTotalBonuses, atkCombatBuffs)

    if "GiveMeYourBonuses" in defSkills and AtkPanicFactor == 1:
        totalBonuses = 0
        for i in range(1,5): totalBonuses += attacker.buffs[i] * atkBonusesNeutralized[i]
        map(lambda x: x + math.trunc(totalBonuses * 0.5), defCombatBuffs)

    if "ILoveBonusesAndWomenAndI'mAllOutOfBonuses" in defSkills:
        tempAtkBonuses = 0
        tempDefBonuses = 0
        if AtkPanicFactor == 1:
            for i in range(1,5): tempAtkBonuses += attacker.buffs[i] * atkBonusesNeutralized[i]
        if DefPanicFactor == 1:
            for i in range(1,5): tempDefBonuses += defender.buffs[i] * defBonusesNeutralized[i]
        tempTotalBonuses = min(10, math.trunc((tempAtkBonuses + tempDefBonuses) * 0.4))
        map(lambda x: x + tempTotalBonuses, defCombatBuffs)

    if "beeeg debuff" in atkSkills:
        defCombatBuffs[1] -= 4
        defCombatBuffs[2] -= 4
        defCombatBuffs[3] -= 4
        for i in range(1,5):
            atkCombatBuffs[ATK] += min(defender.debuffs[i] * defPenaltiesNeutralized[i], 0) * -1 + min(defender.buffs[i] * DefPanicFactor * defPenaltiesNeutralized[i], 0) * -1

    if "beeeg debuff" in defSkills and defAllyWithin2Spaces:
        atkCombatBuffs[1] -= 4
        atkCombatBuffs[2] -= 4
        atkCombatBuffs[3] -= 4
        for i in range(1, 5):
            defCombatBuffs[ATK] += min(attacker.debuffs[i] * atkPenaltiesNeutralized[i], 0) * -1 + min(attacker.buffs[i] * AtkPanicFactor * atkPenaltiesNeutralized[i], 0) * -1

    if "spectrumUnityMarth" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] += 4 + ((min(attacker.debuffs[i], 0) * -2) + (min(AtkPanicFactor * attacker.buffs[i], 0) * -2)) * (not atkPenaltiesNeutralized[i])

    if "spectrumUnityMarth" in defSkills and defAllyWithin2Spaces:
        for i in range(1, 5):
            defCombatBuffs[i] += 4 + ((min(defender.debuffs[i], 0) * -2) + (min(DefPanicFactor * defender.buffs[i], 0) * -2)) * (not defPenaltiesNeutralized[i])

    if "penaltyReverse" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] += ((min(attacker.debuffs[i], 0) * -2) + (min(AtkPanicFactor * attacker.buffs[i], 0) * -2)) * (not atkPenaltiesNeutralized[i])

    if "penaltyReverse" in defSkills:
        for i in range(1, 5):
            defCombatBuffs[i] += ((min(defender.debuffs[i], 0) * -2) + (min(DefPanicFactor * defender.buffs[i], 0) * -2)) * (not defPenaltiesNeutralized[i])

    if "Minecraft Gaming" in atkSkills:
        for i in range(1, 5):
            defCombatBuffs[i] -= 5 + (max(DefPanicFactor * defender.buffs[i], 0) * -2) * (not defBonusesNeutralized[i])

    if "Minecraft Gaming" in defSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] -= 5 + (max(AtkPanicFactor * attacker.buffs[i], 0) * -2) * (not atkBonusesNeutralized[i])

    for i in range(1,5):
        atkCombatBuffs[i] -= atkPenaltiesNeutralized[i] * (attacker.debuffs[i] + max(attacker.buffs[i] * AtkPanicFactor, 0))
        atkCombatBuffs[i] += atkBonusesNeutralized[i] * min(attacker.buffs[i] * AtkPanicFactor, 0)
        defCombatBuffs[i] -= defPenaltiesNeutralized[i] * (defender.debuffs[i] + max(defender.buffs[i] * DefPanicFactor, 0))
        defCombatBuffs[i] += defBonusesNeutralized[i] * min(defender.buffs[i] * DefPanicFactor, 0)

    i = 0
    while i < 5:
        atkStats[i] += atkCombatBuffs[i]
        defStats[i] += defCombatBuffs[i]
        i += 1

    i = 0
    while i < 5:
        atkPhantomStats[i] += atkStats[i]
        defPhantomStats[i] += defStats[i]
        i += 1

    # From this point on, use atkStats/defStats for getting atk values
    # Use atkPhantomStats/defPhantomStats for comparisons
    # END OF STAT MODIFICATION SKILLS, NO MORE SHOULD EXIST BENEATH THIS LINE

    # SPECIAL CHARGE MODIFICATION

    # special charge goes down 1 by through being attacked or attacking
    # it can be modified to go down by 2 or not change at all through some skills
    # in addition, some skills can nullify special changes such as the ones above
    # hey you can make 4 nice variables to save some lines here too, you should do that, me :)

    if "heavyBlade" in atkSkills and atkPhantomStats[1] > defPhantomStats[1] + max(-2 * atkSkills["heavyBlade"] + 7, 1):
        attackerGainWhenAttacking += 1
    if "heavyBlade" in defSkills and defPhantomStats[1] > atkPhantomStats[1] + max(-2 * defSkills["heavyBlade"] + 7, 1):
        defenderGainWhenAttacking += 1

    if "royalSword" in atkSkills and atkAllyWithin2Spaces or "royalSword2" in atkSkills: attackerGainWhenAttacking += 1
    if ("royalSword" in defSkills or "royalSword2" in defSkills) and defAllyWithin2Spaces: defenderGainWhenAttacking += 1

    if "ourBoyBlade" in atkSkills:
        attackerGainWhenAttacking += 1
        attackerGainWhenAttacked += 1
        defenderLossWhenAttacked -= 1
        defenderLossWhenAttacking -= 1

    if "wanderer" in atkSkills and defHPGreaterEqual75Percent and atkPhantomStats[SPD] > defPhantomStats[SPD]:
        attackerGainWhenAttacking += 1
        attackerGainWhenAttacked += 1

    if "wanderer" in defSkills and atkHPGreaterEqual75Percent and defPhantomStats[SPD] > atkPhantomStats[SPD]:
        defenderGainWhenAttacking += 1
        defenderGainWhenAttacked += 1

    if "audBoost" in atkSkills and defHPEqual100Percent:
        defenderLossWhenAttacked -= 1
        defenderLossWhenAttacking -= 1

    if "audBoost" in defSkills:
        attackerLossWhenAttacked -= 1
        attackerLossWhenAttacking -= 1

    if "shez!" in atkSkills and atkHPCur / atkStats[0] >= 0.2:
        attackerGainWhenAttacking += 1
        attackerGainWhenAttacked += 1

    if "shez!" in defSkills and defHPCur / defStats[0] >= 0.2:
        defenderGainWhenAttacking += 1
        defenderGainWhenAttacked += 1

    if "BY MISSILETAINN!!!" in atkSkills:
        attackerGainWhenAttacked += 1

    if "BY MISSILETAINN!!!" in defSkills:
        defenderGainWhenAttacked += 1


    if "flashingBlade" in atkSkills and atkPhantomStats[2] > defPhantomStats[2] + max(-2 * atkSkills["flashingBlade"] + 7, 1):
        attackerGainWhenAttacking += 1
    if "flashingBlade" in defSkills and defPhantomStats[2] > atkPhantomStats[2] + max(-2 * defSkills["flashingBlade"] + 7, 1):
        defenderGainWhenAttacking += 1

    if "guardHP" in atkSkills and atkHPCur / atkStats[0] >= atkSkills["guardHP"]:
        defenderLossWhenAttacked -= 1
        defenderLossWhenAttacking -= 1

    # TEMPO WEAPONS/SKILLS

    if "swagDespPlusPlus" in atkSkills and defHPGreaterEqual75Percent:
        attackerLossWhenAttacking = 0
        attackerLossWhenAttacked = 0

    if "swagDespPlusPlus" in defSkills and atkHPGreaterEqual75Percent:
        defenderLossWhenAttacking = 0
        defenderLossWhenAttacked = 0

    if "moreeeeta" in atkSkills and atkHPGreaterEqual25Percent:
        attackerLossWhenAttacking = 0
        attackerLossWhenAttacked = 0

    if "moreeeeta" in defSkills and defHPGreaterEqual25Percent:
        defenderLossWhenAttacking = 0
        defenderLossWhenAttacked = 0

    if "ROY'S OUR BOY" in atkSkills and atkHPGreaterEqual25Percent:
        attackerLossWhenAttacking = 0
        attackerLossWhenAttacked = 0

    if "ROY'S OUR BOY" in defSkills and defHPGreaterEqual25Percent:
        defenderLossWhenAttacking = 0
        defenderLossWhenAttacked = 0

    if "larceiEdge2" in atkSkills and atkPhantomStats[2] > defPhantomStats[2] or defHPGreaterEqual75Percent:
        attackerLossWhenAttacking = 0
        attackerLossWhenAttacked = 0

    if "larceiEdge2" in defSkills and defPhantomStats[2] > atkPhantomStats[2] or atkHPGreaterEqual75Percent:
        defenderLossWhenAttacking = 0
        defenderLossWhenAttacked = 0

    if "up b side b" in atkSkills or "up b bair" in defSkills:
        defenderGainWhenAttacking = 0
        defenderGainWhenAttacked = 0
        attackerLossWhenAttacking = 0
        attackerLossWhenAttacked = 0

    if "up b side b" in defSkills or "up b bair" in defSkills:
        attackerGainWhenAttacking = 0
        attackerGainWhenAttacked = 0
        defenderLossWhenAttacking = 0
        defenderLossWhenAttacked = 0

    if "nintenesis" in atkSkills and atkTop3AllyBuffTotal >= 10:
        attackerLossWhenAttacked = 0
        attackerLossWhenAttacking = 0

    if "nintenesis" in defSkills and defAllyWithin2Spaces and defTop3AllyBuffTotal >= 10:
        defenderLossWhenAttacked = 0
        defenderLossWhenAttacking = 0

    if "Hello, I like money" in atkSkills and attacker.dragonflowers > 1:
        defenderGainWhenAttacking = 0
        defenderGainWhenAttacked = 0
        attackerLossWhenAttacking = 0
        attackerLossWhenAttacked = 0

    if "Hello, I like money" in defSkills and defAllyWithin2Spaces and defender.dragonflowers > 1:
        attackerGainWhenAttacking = 0
        attackerGainWhenAttacked = 0
        defenderLossWhenAttacking = 0
        defenderLossWhenAttacked = 0

    if "tempo" in atkSkills:
        defenderGainWhenAttacking = 0
        defenderGainWhenAttacked = 0
        attackerLossWhenAttacking = 0
        attackerLossWhenAttacked = 0

    if "tempo" in defSkills:
        attackerGainWhenAttacking = 0
        attackerGainWhenAttacked = 0
        defenderLossWhenAttacking = 0
        defenderLossWhenAttacked = 0

    attackerGainWhenAttacking = min(attackerGainWhenAttacking, 1) + max(attackerLossWhenAttacking,-1)
    attackerGainWhenAttacked = min(attackerGainWhenAttacked,1) + max(attackerLossWhenAttacked,-1)
    defenderGainWhenAttacking = min(defenderGainWhenAttacking,1) + max(defenderLossWhenAttacking,-1)
    defenderGainWhenAttacked = min(defenderGainWhenAttacked,1) + max(defenderLossWhenAttacked,-1)

    #attackerGainWhenAttacking = min(max(attackerGainWhenAttacking, -1), 1)
    #attackerGainWhenAttacked = min(max(attackerGainWhenAttacked, -1), 1)
    #defenderGainWhenAttacking = min(max(defenderGainWhenAttacking, -1), 1)
    #defenderGainWhenAttacked = min(max(defenderGainWhenAttacked, -1), 1)

    # WINDSWEEP PLEASE GET RID OF THAT WINDSWEEP CHECK THING IT SUCKS

    if "windsweep" in atkSkills:
        atkSkillFollowUpDenials -= 1
        if atkPhantomStats[2] > defPhantomStats[2] + (-2 * atkSkills["windsweep"] + 7) and defender.getTargetedDef() == -1:
            cannotCounter = True

    # I hate this skill up until level 4 why does it have all those conditions
    if "brashAssault" in atkSkills and (cannotCounter or not(attacker.getRange() == defender.getRange() or ignoreRng)) and atkHPCur / atkStats[0] <= 0.1 * atkSkills["brashAssault"] + 0.2:
        atkSkillFollowUps += 1

    if Status.NullFollowUp in attacker.statusPos and atkPhantomStats[2] > defPhantomStats[2]:
        atkSkillFollowUpDenials = 0
        defSkillFollowUps = 0

    if Status.NullFollowUp in defender.statusPos and defPhantomStats[2] > atkPhantomStats[2]:
        defSkillFollowUpDenials = 0
        atkSkillFollowUps = 0

    if atkNullDefFU: defSkillFollowUps = 0
    if defNullAtkFU: atkSkillFollowUps = 0
    if atkDoSkillFU: atkSkillFollowUpDenials = 0
    if defDoSkillFU: defSkillFollowUpDenials = 0

    # MOVE TO STAT AREA

    if "Barry B. Benson" in atkSkills and defHPGreaterEqual75Percent:
        atkSkillFollowUpDenials = 0
        defSkillFollowUps = 0

    if "Barry B. Benson" in defSkills and atkHPGreaterEqual75Percent:
        defSkillFollowUpDenials = 0
        atkSkillFollowUps = 0

    if "sweeeeeeep" in atkSkills and atkHPGreaterEqual25Percent and \
        defender.wpnType not in ["RTome", "BTome", "GTome", "CTome", "RDragon", "BDragon", "GDragon", "CDragon", "Staff"]\
        and atkPhantomStats[2] > defPhantomStats[2]:
        atkSkillFollowUpDenials = 0
        cannotCounter = True

    if "sweeeeeeep" in defSkills and defHPGreaterEqual25Percent and \
        attacker.wpnType not in ["RTome", "BTome", "GTome", "CTome", "RDragon", "BDragon", "GDragon", "CDragon", "Staff"]\
        and defPhantomStats[2] > atkPhantomStats[2]:
        defSkillFollowUpDenials = 0

    if "waitTurns" in atkSkills:
        atkSkillFollowUpDenials = 0
        defSkillFollowUps = 0

    if "waitTurns" in defSkills and defAllyWithin2Spaces:
        defSkillFollowUpDenials = 0
        atkSkillFollowUps = 0

    if "niuBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkSkillFollowUpDenials = 0
        defSkillFollowUps = 0

    if "niuBoost" in defSkills and defHPGreaterEqual25Percent:
        defSkillFollowUpDenials = 0
        atkSkillFollowUps = 0

    if "ascendingBlade" in atkSkills and atkHPGreaterEqual25Percent:
        atkSkillFollowUpDenials = 0
        defSkillFollowUps = 0

    if "ascendingBlade" in defSkills and defHPGreaterEqual25Percent:
        defSkillFollowUpDenials = 0
        atkSkillFollowUps = 0

    if "up b side b" or "up b bair" in atkSkills:
        atkSkillFollowUpDenials = 0
        defSkillFollowUps = 0

    if "up b side b" or "up b bair" in defSkills:
        defSkillFollowUpDenials = 0
        atkSkillFollowUps = 0

    if "thundabrand" in atkSkills and defHPGreaterEqual50Percent:
        atkSkillFollowUpDenials = 0

    if "thundabrand" in defSkills and atkHPGreaterEqual50Percent:
        defSkillFollowUpDenials = 0

    if ("SEGAAAA" in atkSkills or "nintenesis" in atkSkills) and atkTop3AllyBuffTotal >= 10:
        atkSkillFollowUpDenials = 0
        defSkillFollowUps = 0

    if ("SEGAAAA" in defSkills or "nintenesis" in defSkills) and defAllyWithin2Spaces and defTop3AllyBuffTotal >= 10:
        defSkillFollowUpDenials = 0
        atkSkillFollowUps = 0

    if "NFUSolo" in atkSkills and not atkAdjacentToAlly:
        atkSkillFollowUpDenials = 0
        defSkillFollowUps = 0

    if "NFUSolo" in defSkills and not defAdjacentToAlly:
        defSkillFollowUpDenials = 0
        atkSkillFollowUps = 0

    if "mareeeeta" in atkSkills and atkAdjacentToAlly <= 1:
        atkSkillFollowUpDenials = 0
        defSkillFollowUps = 0

    if "mareeeeta" in defSkills and defAdjacentToAlly <= 1:
        defSkillFollowUpDenials = 0
        atkSkillFollowUps = 0

    if "newVTyrfing" in atkSkills and (not atkHPEqual100Percent or defHPGreaterEqual75Percent):
        atkSkillFollowUpDenials = 0

    if "newVTyrfing" in defSkills:
        defSkillFollowUpDenials = 0

    # MOVE TO STAT AREA FOR EACH WEAPON

    # atkTrueDamageArr = list(map(lambda x: x + 5, atkTrueDamageArr))
    # defTrueDamageArr = list(map(lambda x: x + 5, defTrueDamageArr))

    # TRUE DAMAGE ADDITION
    if "SpdDmg" in atkSkills and atkPhantomStats[2] > defPhantomStats[2]:
        atkTrueDamageArr = list(map(lambda x: x + min(math.trunc((atkPhantomStats[2]-defPhantomStats[2]) * 0.1 * atkSkills["SpdDmg"]), atkSkills["SpdDmg"]), atkTrueDamageArr))
    if "SpdDmg" in defSkills and defPhantomStats[2] > atkPhantomStats[2]:
        defTrueDamageArr = list(map(lambda x: x + min(math.trunc((defPhantomStats[2]-atkPhantomStats[2]) * 0.1 * defSkills["SpdDmg"]), defSkills["SpdDmg"]), defTrueDamageArr))

    if "moreeeeta" in atkSkills and atkHPGreaterEqual25Percent:
        atkTrueDamageArr = list(map(lambda x: x + math.trunc(atkStats[2] * 0.1), atkTrueDamageArr))
    if "moreeeeta" in defSkills and defHPGreaterEqual25Percent:
        defTrueDamageArr = list(map(lambda x: x + math.trunc(defStats[2] * 0.1), defTrueDamageArr))

    if "thraicaMoment" in atkSkills and defStats[3] >= defStats[4] + 5:
        atkTrueDamageArr = list(map(lambda x: x + 7, atkTrueDamageArr))
    if "thraciaMoment" in defSkills and atkStats[3] >= atkStats[4] + 5:
        defTrueDamageArr = list(map(lambda x: x + 7, defTrueDamageArr))

    if "LOVE PROVIIIIDES, PROTECTS US" in atkSkills and atkHPGreaterEqual25Percent:
        atkTrueDamageArr = list(map(lambda x: x + math.trunc(atkStats[2] * 0.15), atkTrueDamageArr))
    if "LOVE PROVIIIIDES, PROTECTS US" in defSkills and defHPGreaterEqual25Percent:
        defTrueDamageArr = list(map(lambda x: x + math.trunc(defStats[2] * 0.15), defTrueDamageArr))

    if "vassalBlade" in atkSkills:
        atkTrueDamageArr = list(map(lambda x: x + math.trunc(atkStats[2] * 0.15), atkTrueDamageArr))
    if "vassalBlade" in defSkills and defAllyWithin2Spaces:
        defTrueDamageArr = list(map(lambda x: x + math.trunc(defStats[2] * 0.15), defTrueDamageArr))

    if "infiniteSpecial" in atkSkills:
        atkTrueDamageArr = list(map(lambda x: x + math.trunc(atkStats[2] * 0.15), atkTrueDamageArr))
    if "infiniteSpecial" in defSkills:
        defTrueDamageArr = list(map(lambda x: x + math.trunc(defStats[2] * 0.15), defTrueDamageArr))

    if "newVTyrfing" in atkSkills and (not atkHPEqual100Percent or defHPGreaterEqual75Percent):
        atkTrueDamageArr = list(map(lambda x: x + math.trunc(atkStats[1] * 0.15), atkTrueDamageArr))
    if "newVTyrfing" in defSkills:
        defTrueDamageArr = list(map(lambda x: x + math.trunc(defStats[1] * 0.15), defTrueDamageArr))

    if "hamburger" in atkSkills:
        atkTrueDamageArr = list(map(lambda x: x + math.trunc(atkStats[3] * 0.15), atkTrueDamageArr))
    if "hamburger" in atkSkills and defAllyWithin2Spaces:
        defTrueDamageArr = list(map(lambda x: x + math.trunc(defStats[3] * 0.15), defTrueDamageArr))

    if "I HATE FIRE JOKES >:(" in atkSkills and spacesMovedByAtkr:
        atkTrueDamageArr = list(map(lambda x: x + math.trunc(defStats[DEF] * 0.10 * min(spacesMovedByAtkr, 4)), atkTrueDamageArr))
    if "I HATE FIRE JOKES >:(" in defSkills and spacesMovedByAtkr:
        defTrueDamageArr = list(map(lambda x: x + math.trunc(atkStats[DEF] * 0.10 * min(spacesMovedByAtkr, 4)), defTrueDamageArr))

    if "renaisTwins" in atkSkills and (atkHasBonus or atkHasPenalty):
        atkTrueDamageArr = list(map(lambda x: x + math.trunc(defStats[3] * 0.20), atkTrueDamageArr))
        atkMidCombatHeal += math.trunc(defStats[3] * 0.20)

    if "renaisTwins" in defSkills and defAllyWithin2Spaces and (defHasBonus or defHasPenalty):
        defTrueDamageArr = list(map(lambda x: x + math.trunc(atkStats[3] * 0.20), defTrueDamageArr))
        defMidCombatHeal += math.trunc(atkStats[3] * 0.20)

    if "megaAstra" in atkSkills and atkPhantomStats[1] > defPhantomStats[3]:
        atkTrueDamageArr = list(map(lambda x: x + max(math.trunc((atkStats[1] - defStats[3]) * 0.5), 0), atkTrueDamageArr))

    if "megaAstra" in defSkills and defPhantomStats[1] > atkPhantomStats[3]:
        defTrueDamageArr = list(map(lambda x: x + max(math.trunc((defStats[1] - atkStats[3]) * 0.5), 0), defTrueDamageArr))

    # transform into lambda function, all for Owain's refined effect
    atkSpTrueDamageFunc = lambda x: atkFixedSpDmgBoost
    defSpTrueDamageFunc = lambda x: defFixedSpDmgBoost

    if "Sacred Stones Strike!" in atkSkills and atkAllyWithin3Spaces:
        atkSpTrueDamageFunc = lambda x: x + atkFixedSpDmgBoost

    if "Sacred Stones Strike!" in defSkills and defAllyWithin3Spaces:
        defSpTrueDamageFunc = lambda x: x + defFixedSpDmgBoost

    # TRUE DAMAGE SUBTRACTION

    # what do you mean you haven't done anything yet

    # EFFECTIVENESS CHECK

    oneEffAtk = False
    oneEffDef = False

    if "effInf" in atkSkills and defender.move == 0: oneEffAtk = True
    if "effInf" in defSkills and attacker.move == 0: oneEffDef = True

    if "effCav" in atkSkills and "nullEffCav" not in defSkills and defender.move == 1: oneEffAtk = True
    if "effCav" in defSkills and "nullEffCav" not in atkSkills and attacker.move == 1: oneEffDef = True

    if "effFly" in atkSkills and "nullEffFly" not in defSkills and defender.move == 2: oneEffAtk = True
    if "effFly" in defSkills and "nullEffFly" not in atkSkills and attacker.move == 2: oneEffDef = True

    if "effArm" in atkSkills and "nullEffArm" not in defSkills and defender.move == 3: oneEffAtk = True
    if "effArm" in defSkills and "nullEffArm" not in atkSkills and attacker.move == 3: oneEffDef = True

    if ("effDrg" in atkSkills or Status.EffDragons in attacker.statusPos) and "nullEffDrg" not in defSkills and (defender.getTargetedDef() == 0 or "loptous" in defSkills):
        oneEffAtk = True
    if ("effDrg" in defSkills or Status.EffDragons in defender.statusPos) and "nullEffDrg" not in atkSkills and (attacker.getTargetedDef() == 0 or "loptous" in atkSkills):
        oneEffDef = True

    if "effMagic" in atkSkills and defender.wpnType in ["RTome", "BTome", "GTome", "CTome"]: oneEffAtk = True
    if "effMagic" in defSkills and attacker.wpnType in ["RTome", "BTome", "GTome", "CTome"]: oneEffDef = True

    if "effBeast" in atkSkills and defender.wpnType in ["RBeast", "BBeast", "GBeast", "CBeast"]:
        oneEffAtk = True
    if "effBeast" in defSkills and attacker.wpnType in ["RBeast", "BBeast", "GBeast", "CBeast"]:
        oneEffDef = True

    if "effCaeda" in atkSkills and (defender.wpnType in ["Sword", "Lance", "Axe", "CBow"] or (defender.move == 3 and "nullEffArm" not in defSkills)):
        oneEffAtk = True
    if "effCaeda" in defSkills and (attacker.wpnType in ["Sword", "Lance", "Axe", "CBow"] or (attacker.move == 3 and "nullEffArm" not in atkSkills)):
        oneEffDef = True

    if "effShez" in atkSkills:
        if defender.move == 0 and defender.wpnType not in ["RDragon", "BDragon", "GDragon", "CDragon", "RBeast", "BBeast", "GBeast", "CBeast"]:
            threshold = defPhantomStats[2] + 20
        else:
            threshold = defPhantomStats[2] + 5

        if atkPhantomStats[2] >= threshold:
            oneEffAtk = True

    if defender.wpnType == "BTome" and "haarEff" in atkSkills:
        oneEffDef = True
    if attacker.wpnType == "BTome" and "haarEff" in defSkills:
        oneEffAtk = True

    if oneEffAtk: atkStats[1] += math.trunc(atkStats[1] * 0.5)
    if oneEffDef: defStats[1] += math.trunc(defStats[1] * 0.5)


    # COLOR ADVANTAGE

    if (attacker.getColor() == "Red" and defender.getColor() == "Green") or (attacker.getColor() == "Green" and defender.getColor() == "Blue") or \
            (attacker.getColor() == "Blue" and defender.getColor() == "Red") or (defender.getColor() == "Colorless" and "colorlessAdv" in atkSkills):

        if (atkCA == 1 or defCA == 1) and triAdept != -1: triAdept = -1
        if defCA == 2 and triAdept != -1: triAdept = -1
        if atkCA == 3 and triAdept != -1: triAdept = -5

        atkStats[1] += math.trunc(atkStats[1] * (0.25 + .05 * triAdept))
        defStats[1] -= math.trunc(defStats[1] * (0.25 + .05 * triAdept))

        wpnAdvHero = 0

    if (attacker.getColor() == "Blue" and defender.getColor() == "Green") or (attacker.getColor() == "Red" and defender.getColor() == "Blue") or \
            (attacker.getColor() == "Green" and defender.getColor() == "Red") or (attacker.getColor() == "Colorless" and "colorlessAdv" in defSkills):

        if (atkCA == 1 or defCA == 1) and triAdept != -1: triAdept = -1
        if atkCA == 2 and triAdept != -1: triAdept = -1
        if atkCA == 3 and triAdept != -1: triAdept = -5
        atkStats[1] -= math.trunc(atkStats[1] * (0.25 + .05 * triAdept))
        defStats[1] += math.trunc(defStats[1] * (0.25 + .05 * triAdept))

        wpnAdvHero = 1

    # WHICH DEFENSE ARE WE TARGETING?

    r = int(attacker.getTargetedDef() == 1)

    if attacker.getTargetedDef() == 0 and "dragonCheck" in atkSkills:
        if defender.getRange() == 2 and defStats[3] > defStats[4]:
            r += 1
        elif defender.getRange() != 2:
            r += 1

    q = int(defender.getTargetedDef() == 1)

    if defender.getTargetedDef() == 0 and "dragonCheck" in defSkills:
        if attacker.getRange() == 2 and atkStats[3] > atkStats[4]:
            q += 1
        elif attacker.getRange() != 2:
            q += 1

    if "permHexblade" in atkSkills: q = int(defStats[3] < defStats[4])
    if "permHexblade" in defSkills: r = int(atkStats[3] < atkStats[4])

    # additional follow-up granted by outspeeding
    outspeedFactor = 5
    atkPotentFU = False
    defPotentFU = False

    if "FOR THE PRIDE OF BRODIA" in atkSkills: outspeedFactor += 20
    if "FOR THE PRIDE OF BRODIA" in defSkills: outspeedFactor += 20

    if "potentStrike" in atkSkills and atkStats[SPD] >= defStats[SPD] + (outspeedFactor - 25):
        atkPotentFU = True

    if "potentStrike" in defSkills and defStats[SPD] >= atkStats[SPD] + (outspeedFactor - 25):
        defPotentFU = True

    if (atkStats[2] >= defStats[2] + outspeedFactor): atkSpdFollowUps += 1
    if (atkStats[2] + outspeedFactor <= defStats[2]): defSpdFollowUps += 1

    atkAlive = True
    defAlive = True

    def getSpecialHitDamage(effs, initStats, otherStats, defOrRes):

        spdDmg = 0  # For Lunar Flash + Lunar Flash II

        if "spdBoost" in effs:
            spdDmg = math.trunc(initStats[2] * .10 * effs["spdBoost"])
            if "defReduce" not in effs: return spdDmg

        if "atkBoost" in effs:
            atkDmg = math.trunc(initStats[1] * .10 * effs["atkBoost"])
            return atkDmg

        if "defBoost" in effs:
            defDmg = math.trunc(initStats[3] * .10 * effs["defBoost"])
            return defDmg

        if "resBoost" in effs:
            resDmg = math.trunc(initStats[4] * .10 * effs["resBoost"])
            return resDmg

        if "rupturedSky" in effs:
            atkDmg = math.trunc(otherStats[1] * .10 * effs["rupturedSky"])
            return atkDmg

        if "staffRes" in effs:
            resDmg = math.trunc(otherStats[1] * .10 * effs["staffRes"])
            return resDmg

        targeted_defense = otherStats[defOrRes + 3]

        if "defReduce" in effs:
            # standard attack damage
            nonSpAttack = initStats[1] - targeted_defense
            if nonSpAttack < 0: nonSpAttack = 0
            # reduce defense/resistance
            targeted_defense -= math.trunc(targeted_defense * .10 * effs["defReduce"])
            # attack damage with reduced defense/resistance
            attack = initStats[1] - targeted_defense
            if attack < 0: attack = 0
            # return difference
            return attack - nonSpAttack + spdDmg

        if "dmgBoost" in effs:
            # standard attack damage
            nonSpAttack = initStats[1] - targeted_defense
            if nonSpAttack < 0: nonSpAttack = 0
            return math.trunc(nonSpAttack * 0.1 * effs["dmgBoost"])

        return 0


    # COMPUTE TURN ORDER
    cannotCounterFinal = cannotCounter or not(attacker.getRange() == defender.getRange() or ignoreRng)
    # Will never counter if defender has no weapon
    if defender.getWeapon() == NIL_WEAPON: cannotCounterFinal == True

    # Follow-Up Granted if sum of allowed - denied follow-ups is > 0
    followupA = atkSpdFollowUps + atkSkillFollowUps + atkSkillFollowUpDenials > 0
    followupD = defSpdFollowUps + defSkillFollowUps + defSkillFollowUpDenials > 0

    if vantageEnabled:
        startString = "DA"
        if followupD:
            startString += "D"
        if followupA:
            startString += "A"
    else:
        startString = "AD"
        if followupA:
            startString += "A"
        if followupD:
            startString += "D"

    if startString[0] == 'A':
        firstCheck = desperateA
        secondCheck = desperateD
    else:
        firstCheck = desperateD
        secondCheck = desperateA

    if firstCheck:
        startString = move_letters(startString, startString[0])
    if secondCheck:
        startString = move_letters(startString, set(["A", "D"]).difference([startString[0]]).pop())

    newString = ""

    # duplicate letters if Brave Eff
    # it makes zero sense how two D's need to be added, but only one A, but I don't care it works
    for c in startString:
        if c == 'A' and braveATKR:
            newString += c
        if c == 'D' and braveDEFR:
            newString += c * 2
        else:
            newString += c

    # potent strike
    if atkPotentFU:
        last_a_index = newString.rfind('A')
        newString = newString[:last_a_index + 1] + 'A' + newString[last_a_index + 1:]

    if defPotentFU:
        last_a_index = newString.rfind('D')
        newString = newString[:last_a_index + 1] + 'D' + newString[last_a_index + 1:]

    # code don't work without these idk why
    startString = newString
    startString2 = startString

    if cannotCounterFinal: startString2 = startString.replace("D", "")

    # list of attack objects
    attackList = []
    A_Count = 0
    D_Count = 0
    i = 0

    while i < len(startString2):
        if startString2[i] == "A":
            A_Count += 1
            isFollowUp = A_Count == 2 and (followupA or atkPotentFU) and not braveATKR or A_Count in [3, 4, 5]
            isConsecutive = True if A_Count >= 2 and startString2[i - 1] == "A" else False
            attackList.append(Attack(0, isFollowUp, isConsecutive, A_Count, A_Count + D_Count, None if A_Count + D_Count == 1 else attackList[i - 1]))
        else:
            D_Count += 1
            isFollowUp = D_Count == 2 and (followupD or defPotentFU) and not braveDEFR or D_Count in [3, 4, 5]
            isConsecutive = True if D_Count >= 2 and startString2[i - 1] == "D" else False
            attackList.append(Attack(1, isFollowUp, isConsecutive, D_Count, A_Count + D_Count, None if A_Count + D_Count == 1 else attackList[i - 1]))
        i += 1

    # Damage reduction per hit
    # Computed here due to attack order/damage reduction reduction needing to be computed first

    # M!Shez - Crimson Blades - Base
    if "shez!" in atkSkills and atkHPCur / atkStats[0] >= 0.4: defHit1Reduction *= 1 - (defDmgReduFactor * 0.4)
    if "shez!" in defSkills and defHPCur / atkStats[0] >= 0.4: atkHit1Reduction *= 1 - (atkDmgReduFactor * 0.4)

    # Ituski - Mirage Falchion - Refined Eff
    if "Nintendo has forgotten about Mario…" in atkSkills: defHit1Reduction *= 1 - (defDmgReduFactor * 0.3)
    if "Nintendo has forgotten about Mario…" in defSkills and defAllyWithin2Spaces: atkHit1Reduction *= 1 - (atkDmgReduFactor * 0.3)

    # Byleth - Creator Sword - Refined Eff
    if "HERE'S SOMETHING TO BELIEVE IN" in atkSkills and atkHPGreaterEqual25Percent: defHit1Reduction *= 1 - (defDmgReduFactor * 0.3)
    if "HERE'S SOMETHING TO BELIEVE IN" in defSkills and defHPGreaterEqual25Percent: atkHit1Reduction *= 1 - (atkDmgReduFactor * 0.3)

    # SU!Edelgard - Regal Sunshade - Base
    if "regalSunshade" in atkSkills and atkHPGreaterEqual25Percent: defHit1Reduction *= 1 - (0.4 * defDmgReduFactor)
    if "regalSunshade" in defSkills and defHPGreaterEqual25Percent: atkHit1Reduction *= 1 - (0.4 * atkDmgReduFactor)

    # CH!Ike - Sturdy War Sword - Base
    if "sturdyWarrr" in atkSkills and atkHPGreaterEqual25Percent and attacker.getSpecialType() == "Offense" and atkAllyWithin4Spaces >= 2:
        defHit1Reduction *= 1 - (0.1 * attacker.getMaxSpecialCooldown() * defDmgReduFactor)
    if "sturdyWarrr" in defSkills and defHPGreaterEqual25Percent and defender.getSpecialType() == "Offense" and defAllyWithin4Spaces >= 2:
        atkHit1Reduction *= 1 - (0.1 * defender.getMaxSpecialCooldown() * atkDmgReduFactor)

    # Reginn - Lyngheiðr - Base
    if "reginn :)" in atkSkills: defHit1Reduction *= 1 - (defDmgReduFactor * 0.3)

    # Seliph/Sigurd - Divine Tyrfing - Base
    if ("divTyrfing" in atkSkills or "refDivTyrfing" in atkSkills) and defender.wpnType in ["RTome", "BTome", "GTome", "CTome"]:defHit1Reduction *= 1 - (defDmgReduFactor * 0.5)
    if ("divTyrfing" in defSkills or "refDivTyrfing" in defSkills) and attacker.wpnType in ["RTome", "BTome", "GTome", "CTome"]:atkHit1Reduction *= 1 - (atkDmgReduFactor * 0.5)

    # L!Seliph - Virtuous Tyrfing - Refined Eff
    if "NO MORE LOSSES" in atkSkills:
        if defender.wpnType in ["RTome", "BTome", "GTome", "CTome", "Staff"]:
            defHit1Reduction *= 1 - (defDmgReduFactor * 0.8)
            defHit2Reduction *= 1 - (defDmgReduFactor * 0.8)
            defHit3Reduction *= 1 - (defDmgReduFactor * 0.8)
            defHit4Reduction *= 1 - (defDmgReduFactor * 0.8)
        else:
            defHit1Reduction *= 1 - (defDmgReduFactor * 0.4)
            defHit2Reduction *= 1 - (defDmgReduFactor * 0.4)
            defHit3Reduction *= 1 - (defDmgReduFactor * 0.4)
            defHit4Reduction *= 1 - (defDmgReduFactor * 0.4)

    if "NO MORE LOSSES" in defSkills and defAllyWithin3Spaces:
        if attacker.wpnType in ["RTome", "BTome", "GTome", "CTome", "Staff"]:
            atkHit1Reduction *= 1 - (atkDmgReduFactor * 0.8)
            atkHit2Reduction *= 1 - (atkDmgReduFactor * 0.8)
            atkHit3Reduction *= 1 - (atkDmgReduFactor * 0.8)
            atkHit4Reduction *= 1 - (atkDmgReduFactor * 0.8)
        else:
            atkHit1Reduction *= 1 - (atkDmgReduFactor * 0.4)
            atkHit2Reduction *= 1 - (atkDmgReduFactor * 0.4)
            atkHit3Reduction *= 1 - (atkDmgReduFactor * 0.4)
            atkHit4Reduction *= 1 - (atkDmgReduFactor * 0.4)

    if "gregorSword!" in atkSkills: defHit1Reduction *= 1 - (defDmgReduFactor * 0.4)
    if "gregorSword!" in defSkills and defAllyWithin2Spaces: atkHit1Reduction *= 1 - (atkDmgReduFactor * 0.4)

    # L!Sigurd - Hallowed Tyrfing - Base
    if "WaitIsHeAGhost" in atkSkills: defHit1Reduction *= 1 - (defDmgReduFactor * 0.4)
    if "WaitIsHeAGhost" in defSkills and defender.getRange() == 2: atkHit4Reduction *= 1 - (atkDmgReduFactor * 0.4)

    # B!Marth
    if "denesis" in atkSkills and atkHPGreaterEqual25Percent:
        defHit1Reduction *= 1 - (defDmgReduFactor * 0.4)
        if braveDEFR:
            defHit2Reduction *= 1 - (defDmgReduFactor * 0.4)

    if "denesis" in defSkills and defHPGreaterEqual25Percent:
        atkHit1Reduction *= 1 - (atkDmgReduFactor * 0.4)
        if braveATKR:
            atkHit2Reduction *= 1 - (atkDmgReduFactor * 0.4)

    # Ayra
    if "Ayragate" in atkSkills and defHPGreaterEqual75Percent: defHit1Reduction *= 1 - (defDmgReduFactor * 0.2)
    if "Ayragate" in defSkills and atkHPGreaterEqual25Percent: atkHit1Reduction *= 1 - (atkDmgReduFactor * 0.2)

    # Kempf
    if "MY TRAP! 🇺🇸" in atkSkills and atkAdjacentToAlly <= 1: defHit1Reduction *= 1 - (defDmgReduFactor * 0.3)
    if "MY TRAP! 🇺🇸" in defSkills and defAdjacentToAlly <= 1: atkHit1Reduction *= 1 - (atkDmgReduFactor * 0.3)

    # uhhhhhhh
    if "Just Lean" in atkSkills and atkHPGreaterEqual25Percent and atkPhantomStats[2] > defPhantomStats[2]:
        defHit1Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - defPhantomStats[2]), 0.4))
        defHit2Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - defPhantomStats[2]), 0.4))
        defHit3Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - defPhantomStats[2]), 0.4))
        defHit4Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - defPhantomStats[2]), 0.4))

    if "Just Lean" in defSkills and defHPGreaterEqual25Percent and defPhantomStats[2] > atkPhantomStats[2]:
        atkHit1Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))
        atkHit2Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))
        atkHit3Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))
        atkHit4Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))

    # Rutger - Wanderer Blade - Refined Eff
    if "like the university" in atkSkills and atkHPGreaterEqual25Percent and atkPhantomStats[2] > defPhantomStats[2]:
        defHit1Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - defPhantomStats[2]), 0.4))
        defHit2Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - defPhantomStats[2]), 0.4))
        defHit3Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - defPhantomStats[2]), 0.4))
        defHit4Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - defPhantomStats[2]), 0.4))

    if "like the university" in defSkills and defHPGreaterEqual25Percent and defPhantomStats[2] > atkPhantomStats[2]:
        atkHit1Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))
        atkHit2Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))
        atkHit3Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))
        atkHit4Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))

    if "BONDS OF FIIIIRE, CONNECT US" in atkSkills and atkHPGreaterEqual25Percent and atkPhantomStats[2] > defPhantomStats[2]:
        defHit1Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - defPhantomStats[2]), 0.4))
        defHit2Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - defPhantomStats[2]), 0.4))
        defHit3Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - defPhantomStats[2]), 0.4))
        defHit4Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - defPhantomStats[2]), 0.4))

    if "BONDS OF FIIIIRE, CONNECT US" in defSkills and defHPGreaterEqual25Percent and defPhantomStats[2] > atkPhantomStats[2]:
        atkHit1Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))
        atkHit2Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))
        atkHit3Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))
        atkHit4Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))

    if "LOVE PROVIIIIDES, PROTECTS US" in atkSkills and atkHPGreaterEqual25Percent and atkPhantomStats[2] > defPhantomStats[2]:
        defHit1Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - defPhantomStats[2]), 0.4))
        defHit2Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - defPhantomStats[2]), 0.4))
        defHit3Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - defPhantomStats[2]), 0.4))
        defHit4Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - defPhantomStats[2]), 0.4))

    if "LOVE PROVIIIIDES, PROTECTS US" in defSkills and defHPGreaterEqual25Percent and defPhantomStats[2] > atkPhantomStats[2]:
        atkHit1Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))
        atkHit2Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))
        atkHit3Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))
        atkHit4Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))

    # Dodge Status
    if Status.Dodge in atkSkills and atkPhantomStats[2] > defPhantomStats[2]:
        defHit1Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - atkPhantomStats[2]), 0.4))
        defHit2Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - atkPhantomStats[2]), 0.4))
        defHit3Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - atkPhantomStats[2]), 0.4))
        defHit4Reduction *= 1 - (defDmgReduFactor * min(0.04 * (atkPhantomStats[2] - atkPhantomStats[2]), 0.4))

    if Status.Dodge in defSkills and defPhantomStats[2] > atkPhantomStats[2]:
        atkHit1Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))
        atkHit2Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))
        atkHit3Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))
        atkHit4Reduction *= 1 - (atkDmgReduFactor * min(0.04 * (defPhantomStats[2] - atkPhantomStats[2]), 0.4))

    if "reduFU" in atkSkills and turn % 2 == 1 or not defHPEqual100Percent:
        defHit1Reduction *= 1 - (defDmgReduFactor * 0.3 * (1 + int(followupD)))

    if "reduFU" in defSkills and turn % 2 == 1 or not atkHPEqual100Percent:
        atkHit1Reduction *= 1 - (atkDmgReduFactor * 0.3 * (1 + int(followupA)))

    if "ow" in atkSkills and atkHPGreaterEqual25Percent:
        defHit1Reduction *= 1 - (defDmgReduFactor * 0.3)

    if "ow" in defSkills and defHPGreaterEqual25Percent:
        atkHit1Reduction *= 1 - (atkDmgReduFactor * 0.3)

    # Change these to be introduced before, should be True if AOE special triggers (actually should it?)
    atkSpecialTriggered = False
    defSpecialTriggered = False

    # post combat charge
    if "A man has fallen into the river in LEGO City!" in atkSkills and atkHPGreaterEqual25Percent:
        atkPostCombatSpCharge += 1

    if "A man has fallen into the river in LEGO City!" in defSkills and defHPGreaterEqual25Percent:
        defPostCombatSpCharge += 1

    # method to attack
    # yeah that's a lot of stuff to consider, I swear I need it
    def attack(striker, strikee, stkSpEffects, steSpEffects, stkStats, steStats, defOrRes, strSpMod, steSpMod,
               curReduction, curMiracle, trueDmg, curTrueDmg, curSpTrueDmg, curHeal, curDWA, spPierce, alwPierce, curTriggered,
               stkDisabledSpecial, steDisabledSpecial, stkHPCur, steHPCur, stkSpCount, steSpCount):

        stkSpecialTriggered = False
        steSpecialTriggered = False
        dmgBoost = 0

        if stkSpCount == 0 and striker.getSpecialType() == "Offense" and not stkDisabledSpecial:
            if not isInSim: print(striker.getName() + " procs " + striker.getSpName() + ".")
            #print(striker.getSpecialLine())
            dmgBoost = getSpecialHitDamage(stkSpEffects, stkStats, steStats, defOrRes) + curSpTrueDmg(min(stkStats[0] - stkHPCur, 30)) # owain :)
            stkSpecialTriggered = True

        attack = stkStats[1] - steStats[3 + defOrRes]

        if attack < 0: attack = 0
        attack += trueDmg
        attack += dmgBoost
        attack += curTrueDmg(stkSpCount == 0 or curTriggered)
        if striker.getSpecialType() == "Staff": attack = math.trunc(attack * 0.5)
        curReduction = curReduction * (not(stkSpecialTriggered and spPierce) and not(alwPierce))
        attack = math.ceil(attack * curReduction)

        if steSpCount == 0 and strikee.getSpecialType() == "Defense" and not steDisabledSpecial:
            if striker.getRange() == 1 and "closeShield" in steSpEffects:
                if not isInSim: print(strikee.getName() + " procs " + strikee.getSpName() + ".")
                #print(strikee.getSpecialLine())
                attack -= math.trunc(attack * 0.10 * steSpEffects["closeShield"])
                steSpecialTriggered = True
            elif striker.getRange() == 2 and "distantShield" in steSpEffects:
                if not isInSim: print(strikee.getName() + " procs " + strikee.getSpName() + ".")
                #print(strikee.getSpecialLine())
                attack -= math.trunc(attack * 0.10 * steSpEffects["distantShield"])
                steSpecialTriggered = True

        curMiracleTriggered = False
        if curMiracle and steHPCur - attack < 1 and steHPCur != 1:
            attack = steHPCur - 1
            curMiracleTriggered = True

        if steSpCount == 0 and "miracleSP" in steSpEffects and steHPCur - attack < 1 and steHPCur != 1 and not curMiracle:
            if not isInSim: print(strikee.getName() + " procs " + strikee.getSpName() + ".")
            #print(strikee.getSpecialLine())
            attack = steHPCur - 1
            steSpecialTriggered = True

        if curMiracleTriggered: curMiracle = False

        # the attack™
        steHPCur -= attack  # goodness gracious
        if not isInSim: print(striker.getName() + " attacks " + strikee.getName() + " for " + str(attack) + " damage.")  # YES THEY DID

        # used for determining full attack damage
        presented_attack = attack
        # to evaluate noontime heal on hit that kills
        if steHPCur < 1: attack += steHPCur

        stkSpCount = max(stkSpCount - (1 + strSpMod), 0)
        steSpCount = max(steSpCount - (1 + steSpMod), 0)

        if stkSpecialTriggered: stkSpCount = striker.specialMax
        if steSpecialTriggered: steSpCount = striker.specialMax

        totalHealedAmount = 0

        if ("absorb" in striker.getSkills() or stkSpecialTriggered and "healSelf" in stkSpEffects or curHeal(stkSpCount == 0 or curTriggered) > 0) and stkHPCur < stkStats[0]:
            # damage healed from this attack

            if "absorb" in striker.getSkills():
                amountHealed = math.trunc(attack * 0.5)
            if stkSpecialTriggered and "healSelf" in stkSpEffects:
                amountHealed = math.trunc(attack * 0.1 * stkSpEffects["healSelf"])

            totalHealedAmount = amountHealed + curHeal(stkSpCount == 0 or curTriggered)

            if Status.DeepWounds in striker.statusNeg:
                amountHealed = amountHealed - math.trunc((1-curDWA) * totalHealedAmount)

            stkHPCur += totalHealedAmount

            if "absorb" in striker.getSkills():
                if not isInSim: print(striker.getName() + " heals " + str(totalHealedAmount) + " HP during combat.")
            if stkSpecialTriggered and "healSelf" in stkSpEffects:
                if not isInSim: print(striker.getName() + " restores " + str(totalHealedAmount) + " HP.")

            if stkHPCur > stkStats[0]: stkHPCur = stkStats[0]

        return curMiracle, stkSpecialTriggered, steSpecialTriggered, stkHPCur, steHPCur, stkSpCount, steSpCount, presented_attack, totalHealedAmount

    # PERFORM THE ATTACKS

    i = 0
    #while i < len(attackList):
    while i < len(attackList) and (atkAlive and defAlive or isInSim):
        curAtk = attackList[i]
        if curAtk.attackOwner == 0 and curAtk.attackNumSelf == 1 and atkRecoilDmg > 0: atkSelfDmg += atkRecoilDmg
        if curAtk.attackOwner == 0 and curAtk.attackNumSelf == 1 and NEWatkOtherDmg > 0: atkOtherDmg += NEWatkOtherDmg
        if curAtk.attackOwner == 1 and curAtk.attackNumSelf == 1 and defRecoilDmg > 0: defSelfDmg += defRecoilDmg
        if curAtk.attackOwner == 1 and curAtk.attackNumSelf == 1 and NEWdefOtherDmg > 0: defOtherDmg += NEWdefOtherDmg

        if curAtk.attackOwner == 0 and curAtk.attackNumSelf == 1:
            atkPostCombatStatusesApplied[0] = atkPostCombatStatusesApplied[0] + atkPostCombatStatusesApplied[1]
            defPostCombatStatusesApplied[0] = defPostCombatStatusesApplied[0] + defPostCombatStatusesApplied[2]

            attacker.chargeSpecial(atkSpChargeBeforeFirstStrike)

        if curAtk.attackOwner == 1 and curAtk.attackNumSelf == 1:
            defPostCombatStatusesApplied[0] = defPostCombatStatusesApplied[0] + defPostCombatStatusesApplied[1]
            atkPostCombatStatusesApplied[0] = atkPostCombatStatusesApplied[0] + atkPostCombatStatusesApplied[2]

            defender.chargeSpecial(defSpChargeBeforeFirstStrike)

        # this should've been done at the start of the program
        roles = [attacker, defender]
        effects = [atkSpEffects, defSpEffects]
        stats = [atkStats, defStats]
        checkedDefs = [r, q]
        gains = [attackerGainWhenAttacking, defenderGainWhenAttacking, defenderGainWhenAttacked, attackerGainWhenAttacked]
        reductions = [[atkHit1Reduction, atkHit2Reduction, atkHit3Reduction, atkHit4Reduction], [defHit1Reduction, defHit2Reduction, defHit3Reduction, defHit4Reduction]]
        miracles = [atkPseudoMiracleEnabled, defPseudoMiracleEnabled]
        trueDamages = [atkTrueDamageArr, defTrueDamageArr]
        dynamicTrueDamages = [atkTrueDamageFunc, defTrueDamageFunc]
        spTrueDamages = [atkSpTrueDamageFunc, defSpTrueDamageFunc]
        heals = [atkMidCombatHealFunc, defMidCombatHealFunc]
        deepWoundsAllowance = [atkDeepWoundsHealAllowance, defDeepWoundsHealAllowance]
        dmgReduPierces = [atkSpPierceDR, atkAlwaysPierceDR, defSpPierceDR, defAlwaysPierceDR]
        specialTriggers = [atkSpecialTriggered, defSpecialTriggered]
        spDisables = [atkSpecialDisabled, defSpecialDisabled]
        curHPs = [atkHPCur, defHPCur]
        curSpCounts = [atkSpCountCur, defSpCountCur]

        spongebob = curAtk.attackOwner
        patrick = int(not curAtk.attackOwner)

        curRedu = reductions[spongebob][curAtk.attackNumSelf-1]

        # this sucks
        strikeResult = attack(roles[spongebob], roles[patrick], effects[spongebob], effects[patrick], stats[spongebob], stats[patrick],
               checkedDefs[spongebob], gains[spongebob], gains[spongebob + 2], curRedu, miracles[patrick], trueDamages[spongebob][curAtk.attackNumSelf-1], dynamicTrueDamages[spongebob],
               spTrueDamages[spongebob], heals[spongebob], deepWoundsAllowance[spongebob], dmgReduPierces[spongebob], dmgReduPierces[spongebob + 2],
               specialTriggers[spongebob], spDisables[spongebob], spDisables[patrick], curHPs[spongebob], curHPs[patrick], curSpCounts[spongebob], curSpCounts[patrick])

        miracles[patrick] = strikeResult[0]

        atkSpecialTriggered = strikeResult[spongebob + 1]
        defSpecialTriggered = strikeResult[patrick + 1]

        atkHPCur = strikeResult[3 + spongebob]
        defHPCur = strikeResult[3 + patrick]

        atkSpCountCur = strikeResult[5]
        defSpCountCur = strikeResult[6]

        damageDealt = strikeResult[7]
        healthHealed = strikeResult[8]

        curAtk.impl_atk(damageDealt, healthHealed, (atkHPCur, defHPCur), (atkSpCountCur, defSpCountCur))

        #print(strikeResult)

        # I am dead
        if atkHPCur <= 0:
            atkHPCur = 0
            atkAlive = False
            if not isInSim: print(attacker.name + " falls.")
            curAtk.is_finisher = True

        if defHPCur <= 0:
            defHPCur = 0
            defAlive = False
            if not isInSim: print(defender.name + " falls.")
            curAtk.is_finisher = True

        i += 1  # increment buddy!

    # post combat healing/damage, should move to its own process
    if atkAlive and (atkSelfDmg != 0 or defOtherDmg != 0 or atkPostCombatHealing):
        resultDmg = ((atkSelfDmg + defOtherDmg) - atkPostCombatHealing * int(not(Status.DeepWounds in attacker.statusNeg)))
        atkHPCur -= resultDmg
        if resultDmg > 0: print(attacker.getName() + " takes " + str(resultDmg) + " damage after combat.")
        else: print(attacker.getName() + " heals " + str(resultDmg) + " health after combat.")
        if atkHPCur < 1: atkHPCur = 1
        if atkHPCur > atkStats[0]: atkHPCur = atkStats[0]

    if defAlive and (defSelfDmg != 0 or atkOtherDmg != 0 or defPostCombatHealing):
        resultDmg = ((defSelfDmg + atkOtherDmg) - defPostCombatHealing * int(not(Status.DeepWounds in defender.statusNeg)))
        defHPCur -= resultDmg
        if resultDmg > 0: print(defender.getName() + " takes " + str(defSelfDmg + atkOtherDmg) + " damage after combat.")
        else: print(defender.getName() + " heals " + str(defSelfDmg + atkOtherDmg) + " health after combat.")
        if defHPCur < 1: defHPCur = 1
        if defHPCur > defStats[0]: defHPCur = defStats[0]

    # post combat special incrementation, again move to seperate process
    if "specialSpiralW" in atkSkills and atkSpecialTriggered:
        atkPostCombatSpCharge += math.ceil(atkSkills["specialSpiralW"]/2)

    if "specialSpiralW" in defSkills and defSkills["specialSpiral"] > 1 and defSpecialTriggered:
        defPostCombatSpCharge += math.ceil(defSkills["specialSpiralW"]/2)

    if "specialSpiralS" in atkSkills and atkSpecialTriggered:
        atkPostCombatSpCharge += math.ceil(atkSkills["specialSpiralS"]/2)

    if "specialSpiralS" in defSkills and defSkills["specialSpiral"] > 1 and defSpecialTriggered:
        defPostCombatSpCharge += math.ceil(defSkills["specialSpiralS"]/2)

    if "infiniteSpecial" and atkHPGreaterEqual25Percent and attacker.specialCount == attacker.specialMax:
        atkPostCombatSpCharge += 1

    if "infiniteSpecial" and defHPGreaterEqual25Percent and defender.specialCount == defender.specialMax:
        defPostCombatSpCharge += 1

    if atkAlive: attacker.chargeSpecial(atkPostCombatSpCharge)
    if defAlive: defender.chargeSpecial(defPostCombatSpCharge)

    # here ya go
    if atkAlive:
        for m in atkPostCombatStatusesApplied[0]:
            attacker.inflict(m)

    if defAlive:
        for n in defPostCombatStatusesApplied[0]:
            attacker.inflict(n)


    return atkHPCur, defHPCur, atkCombatBuffs, defCombatBuffs, wpnAdvHero, oneEffAtk, oneEffDef,attackList

# new combat function needs to return the following:
# attack values for all attacks in combat, regardless of a unit's death ✓
# which attack finishes a unit ✓
# FEH Math calculation (have to redo true damage calculation)
# special cooldowns after each attack ✓
# hashmap of post-combat effects (oooo we'll get there don't need now)
# weapon triangle advantage ✓
# combat buffs ✓

# FEH Math
# Atk - Def/Res + True Damage applied for all hits

# function should not deal damage to units/charge special/do post-combat things,
# these will be handled by wherever after the combat function is called

class Attack():
    def __init__(self, attackOwner, isFollowUp, isConsecutive, attackNumSelf, attackNumAll, prevAttack):
        self.attackOwner = attackOwner
        self.isFollowUp = isFollowUp
        self.isConsecutive = isConsecutive
        self.attackNumSelf = attackNumSelf
        self.attackNumAll = attackNumAll
        self.prevAttack = prevAttack

        self.damage = -1
        self.spCharges = (-1, -1)
        self.curHPs = (-1, -1)
        self.healed = -1

        self.is_finisher = False

    def impl_atk(self, damage, healed, spCharges, curHPs):
        self.damage = damage
        self.spCharges = spCharges
        self.curHPs = curHPs
        self.healed = healed


# effects distributed to allies/foes within their combats
# this is a demo, final version should be placed within the map and initialized at the start of game

exRange1 = lambda s: lambda o: abs(s[0] - o[0]) <= 1 #within 3 columns centers on unit
exRange2 = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2 # within 2 spaces
exCondition = lambda s: lambda o: o.hasPenalty()
exEffect = {"atkRein": 5, "defRein": 5}
flowerofease_base = {"atkRein": 3, "defRein": 3, "resRein": 3}
flowerofease_ref = {"atkRein": 4, "defRein": 4, "resRein": 4}

class EffectField():
    def __init__(self, owner, range, condition, affectSelf, affectedSide, effect):
        self.owner = owner
        self.range = range(owner.tile)
        self.condition = condition(owner)
        self.affectSelf = affectSelf
        self.affectedSide = affectedSide # 0 for same as owner, 1 otherwise
        self.effect = effect


#flowerOfEaseField = EffectField(mirabilis, exRange1, exCondition, False, True, flowerofease_base)

# SPECIALS
daylight = Special("Daylight", "Restores HP = 30% of damage dealt.", {"healSelf": 3}, 3, SpecialType.Offense)
noontime = Special("Noontime", "Restores HP = 30% of damage dealt.", {"healSelf": 3}, 2, SpecialType.Offense)
sol = Special("Sol", "Restores HP = 50% of damage dealt.", {"healSelf": 5}, 3, SpecialType.Offense)
aether = Special("Aether", "Treats foe's Def/Res as if reduced by 50% during combat. Restores HP = half of damage dealt.", {"defReduce": 5, "healSelf": 5}, 5, SpecialType.Offense)
mayhemAether = Special("Mayhem Aether", "During combat, treats foe's Def/Res as if reduced by 50%. Restores HP = 50% of damage dealt.", {"defReduce": 5, "healSelf": 5}, 4, SpecialType.Offense)
radiantAether = Special("Radiant Aether", "During combat, treats foe's Def/Res as if reduced by 50%. Restores HP = 50% of damage dealt.", {"defReduce": 5, "healSelf": 5}, 4, SpecialType.Offense)
radiantAether2 = Special("Radiant Aether II",
                         "At the start of turn 1, grants Special cooldown count-2 to unit. Treats foe's Def/Res as if reduced by 50% during combat. Restores HP = 50% of damage dealt.",
                         {"defReduce": 5, "healSelf": 5, "turn1Pulse": 2}, 4, SpecialType.Offense)

newMoon = Special("New Moon", "Treats foe's Def/Res as if reduced by 30% during combat.", {"defReduce": 3}, 3, SpecialType.Offense)
moonbow = Special("Moonbow", "Treats foe's Def/Res as if reduced by 30% during combat.", {"defReduce": 3}, 2, SpecialType.Offense)
luna = Special("Luna", "Treats foe's Def/Res as if reduced by 50% during combat.", {"defReduce": 5}, 3, SpecialType.Offense)
blackLuna = Special("Black Luna", "Treats foe's Def/Res as if reduced by 80% during combat. (Skill cannot be inherited.)", {"defReduce": 8}, 3, SpecialType.Offense)
brutalShell = Special("Brutal Shell", "At the start of turn 1, grants Special cooldown count-3 to unit. Treats foe's Def/Res as if reduced by 50% when Special triggers.",
                      {"defReduce": 5, "turn1Pulse": 3}, 3, SpecialType.Offense)
lethality = Special("Lethality", "When Special triggers, treats foe's Def/Res as if reduced by 75% during combat. Disables non-Special skills that \"reduce damage by X%.\"",
                    {"defReduce": 7.5, "spIgnorePercDmgReduc": 0}, 4, SpecialType.Offense)

nightSky = Special("Night Sky", "Boosts damage dealt by 50%.", {"dmgBoost": 5}, 3, SpecialType.Offense)
glimmer = Special("Glimmer", "Boosts damage dealt by 50%.", {"dmgBoost": 5}, 2, SpecialType.Offense)
astra = Special("Astra", "Boosts damage dealt by 150%.", {"dmgBoost": 15}, 4, SpecialType.Offense)

dragonGaze = Special("Dragon Gaze", "Boosts damage by 30% of unit's Atk.", {"atkBoostSp": 3}, 4, SpecialType.Offense)
draconicAura = Special("Draconic Aura", "Boosts damage by 30% of unit's Atk.", {"atkBoostSp": 3}, 3, SpecialType.Offense)
dragonFang = Special("Dragon Fang", "Boosts damage by 50% of unit's Atk.", {"atkBoostSp": 5}, 4, SpecialType.Offense)

lunarFlash = Special("Lunar Flash", "Treats foe’s Def/Res as if reduced by 20% during combat. Boosts damage by 20% of unit's Spd.", {"defReduce": 2, "spdBoostSp": 2}, 2, SpecialType.Offense)

glowingEmber = Special("Glowing Ember", "Boosts damage by 50% of unit's Def.", {"defBoostSp": 5}, 4, SpecialType.Offense)
bonfire = Special("Bonfire", "Boosts damage by 50% of unit's Def.", {"defBoostSp": 5}, 3, SpecialType.Offense)
ignis = Special("Ignis", "Boost damage by 80% of unit's Def.", {"defBoostSp": 8}, 4, SpecialType.Offense)

chillingWind = Special("Chilling Wind", "Boosts damage by 50% of unit's Res.", {"resBoostSp": 5}, 4, SpecialType.Offense)
iceberg = Special("Iceberg", "Boosts damage by 50% of unit's Res.", {"resBoostSp": 5}, 3, SpecialType.Offense)
glacies = Special("Glacies", "Boosts damage by 80% of unit's Res.", {"resBoostSp": 8}, 4, SpecialType.Offense)

# BASED ON POSITIONING, NOT FOE'S RANGE!!!!!
# CHANGE THIS ONCE YOU GET TO THE MAP!!!!!
buckler = Special("Buckler", "Reduces damage from an adjacent foe's attack by 30%.", {"closeShield": 3}, 3, SpecialType.Defense)
pavise = Special("Pavise", "Reduces damage from an adjacent foe's attack by 50%.", {"closeShield": 5}, 3, SpecialType.Defense)
escutcheon = Special("Escutcheon", "Reduces damage from an adjacent foe's attack by 30%.", {"closeShield": 3}, 2, SpecialType.Defense)

holyVestiments = Special("Holy Vestments", "If foe is 2 spaces from unit, reduces damage from foe's attack by 30%.", {"distantShield": 3}, 3, SpecialType.Defense)
sacredCowl = Special("Sacred Cowl", "If foe is 2 spaces from unit, reduces damage from foe's attack by 30%.", {"distantShield": 3}, 2, SpecialType.Defense)
aegis = Special("Aegis", "If foe is 2 spaces from unit, reduces damage from foe's attack by 50%.", {"distantShield": 5}, 3, SpecialType.Defense)

miracle = Special("Miracle","If unit's HP > 1 and foe would reduce unit's HP to 0, unit survives with 1 HP.", {"miracleSP": 0}, 5, SpecialType.Defense)

# A SKILLS

fury4 = Skill("Fury 4", "Grants Atk/Spd/Def/Res+4. After combat, deals 8 damage to unit.", {"atkBoost": 4, "spdBoost": 4, "defBoost": 4, "resBoost": 4, "selfDmg": 8})

# HIGHEST TRIANGLE ADEPT LEVEL USED
# SMALLER LEVELS DO NOT STACK WITH ONE ANOTHER
# ONLY HIGHEST LEVEL USED

svalinnShield = Skill("Svalinn Shield", "Neutralizes \"effective against armored\" bonuses.", {"nullEffArm": 0})
graniShield = Skill("Grani's Shield", "Neutralizes \"effective against cavalry\" bonuses.", {"nullEffCav": 0})
ioteShield = Skill("Iote's Shield", "Neutralizes \"effective against fliers\" bonuses.", {"nullEffFly": 0})

bonusDoubler1 = Skill("Bonus Doubler 1", "Grants bonus to Atk/Spd/Def/Res during combat = 50% of current bonus on each of unit’s stats. Calculates each stat bonus independently.", {"bonusDoublerSk": 1})
bonusDoubler2 = Skill("Bonus Doubler 2", "Grants bonus to Atk/Spd/Def/Res during combat = 75% of current bonus on each of unit’s stats. Calculates each stat bonus independently.", {"bonusDoublerSk": 2})
bonusDoubler3 = Skill("Bonus Doubler 3", "Grants bonus to Atk/Spd/Def/Res during combat = current bonus on each of unit’s stats. Calculates each stat bonus independently.", {"bonusDoublerSk": 3})

sorceryBlade1 = Skill("Sorcery Blade 1", "At start of combat, if unit’s HP = 100% and unit is adjacent to a magic ally, calculates damage using the lower of foe’s Def or Res.", {"sorceryBlade": 1})
sorceryBlade2 = Skill("Sorcery Blade 2", "At start of combat, if unit’s HP ≥ 50% and unit is adjacent to a magic ally, calculates damage using the lower of foe’s Def or Res.", {"sorceryBlade": 2})
sorceryBlade3 = Skill("Sorcery Blade 3", "At start of combat, if unit is adjacent to a magic ally, calculates damage using the lower of foe’s Def or Res.", {"sorceryBlade": 3})

# B SKILLS

specialSpiral3 = Skill ("Special Spiral 3","I dunno", {"specialSpiralS":3})

vantage1 = Skill("Vantage 1", "If unit's HP ≤ 25% and foe initiates combat, unit can counterattack before foe's first attack.", {"vantage": 1})
vantage2 = Skill("Vantage 2", "If unit's HP ≤ 50% and foe initiates combat, unit can counterattack before foe's first attack.", {"vantage": 2})
vantage3 = Skill("Vantage 3", "If unit's HP ≤ 75% and foe initiates combat, unit can counterattack before foe's first attack.", {"vantage": 3})

quickRiposte1 = Skill("Quick Riposte 1", "If unit's HP ≥ 90% and foe initiates combat, unit makes a guaranteed follow-up attack.", {"QRS": 1})
quickRiposte2 = Skill("Quick Riposte 2", "If unit's HP ≥ 80% and foe initiates combat, unit makes a guaranteed follow-up attack.", {"QRS": 2})
quickRiposte3 = Skill("Quick Riposte 3", "If unit's HP ≥ 70% and foe initiates combat, unit makes a guaranteed follow-up attack.", {"QRS": 3})

windsweep1 = Skill("Windsweep 1",
                   "If unit initiates combat, unit cannot make a follow-up attack. If unit’s Spd ≥ foe’s Spd+5 and foe uses sword, lance, axe, bow, dagger, or beast damage, foe cannot counterattack.",
                   {"windsweep": 1})
windsweep2 = Skill("Windsweep 2",
                   "If unit initiates combat, unit cannot make a follow-up attack. If unit’s Spd ≥ foe’s Spd+3 and foe uses sword, lance, axe, bow, dagger, or beast damage, foe cannot counterattack.",
                   {"windsweep": 2})
windsweep3 = Skill("Windsweep 3",
                   "If unit initiates combat, unit cannot make a follow-up attack. If unit’s Spd > foe’s Spd and foe uses sword, lance, axe, bow, dagger, or beast damage, foe cannot counterattack.",
                   {"windsweep": 3})

cancelAffinity1 = Skill("Cancel Affinity 1", "Neutralizes all weapon-triangle advantage granted by unit's and foe's skills.", {"cancelTA": 1})
cancelAffinity2 = Skill("Cancel Affinity 2",
                        "Neutralizes weapon-triangle advantage granted by unit's skills. If unit has weapon-triangle disadvantage, neutralizes weapon-triangle advantage granted by foe's skills.",
                        {"cancelTA": 2})
cancelAffinity3 = Skill("Cancel Affinity 3",
                        "Neutralizes weapon-triangle advantage granted by unit's skills. If unit has weapon-triangle disadvantage, reverses weapon-triangle advantage granted by foe's skills.",
                        {"cancelTA": 3})

guard1 = Skill("Guard 1", "At start of combat, if unit's HP = 100%, inflicts Special cooldown charge -1 on foe per attack. (Only highest value applied. Does not stack.)", {"guardHP": 1})
guard2 = Skill("Guard 2", "At start of combat, if unit's HP ≥ 90%, inflicts Special cooldown charge -1 on foe per attack. (Only highest value applied. Does not stack.)", {"guardHP": 0.9})
guard3 = Skill("Guard 3", "At start of combat, if unit's HP ≥ 80%, inflicts Special cooldown charge -1 on foe per attack. (Only highest value applied. Does not stack.)", {"guardHP": 0.8})
guard4 = Skill("Guard 4",
               "At start of combat, if unit's HP ≥ 25%, inflicts Atk-4 and Special cooldown charge -1 on foe per attack during combat (only highest value applied; does not stack) and reduces damage from foe's first attack during combat by 30%.",
               {"guardHP": 0.25, "lullAtk": 4, "reduceFirst": 30})

# C SKILLS

spurRes3 = Skill("Spur Res 3", "Grants Res+4 to adjacent allies during combat.", {"spurRes": 4})
wardCavalry = Skill("Ward Cavalry", "Grants Def/Res+4 to cavalry allies within 2 spaces during combat.", {"ward": 1})
goadArmor = Skill("Goad Armor", "Grants Atk/Spd+4 to armored allies within 2 spaces during combat.", {"goad": 3})

# PW Brave y (weapon)
# EW Brave Y
# BW Brave Y
# PS Brave Y (skill)

#noah = Hero("Noah", 40, 42, 45, 35, 25, "Sword", 0, marthFalchion, luna, None, None, None)
#mio = Hero("Mio", 38, 39, 47, 27, 29, "BDagger", 0, tacticalBolt, moonbow, None, None, None)

#player = makeHero("M!Alear")
#enemy = makeHero("Mirabilis")

#player_weapon = makeWeapon("Resolute BladeEff")
#enemy_weapon = makeWeapon("Flower of Ease")

player = Hero("Marth", "E!Marth", 0, "Sword", 0, [41, 45, 47, 33, 27], [50, 80, 90, 55, 40], 5, 165)
enemy = Hero("Lucina", "B!Lucina", 0, "Lance", 0, [41, 34, 36, 27, 19], [50, 60, 60, 45, 35], 30, 165)

player_weapon = Weapon("Hero-King Sword", "Hero-King Sword", "", 1, 1, "Sword", {"slaying": 1, "effDragon": 0, "BraveAW": 0}, {})
enemy_weapon = Weapon("Iron Lance", "Iron Lance", "", 6, 1, "Lance", {}, {})

player.set_skill(player_weapon, WEAPON)
enemy.set_skill(enemy_weapon, WEAPON)

# 50, 10
# 60, 20
# 70, 30
# 80, 40
potent1 = Skill("Potent 1", "", {"potentStrike": 1})
defStance = Skill("Thing", "", {"defStance": 3})

player.set_skill(potent1, BSKILL)
enemy.set_skill(defStance, ASKILL)

#player.set_skill(glimmer, 2)
#enemy.set_skill(luna, 2)

print(simulate_combat(player, enemy, 0, 1, 2, []))

# noah.addSpecialLines("\"I'm sorry, but you're in our way!\"",
#                      "\"For the greater good!\"",
#                      "\"The time is now!\"",
#                      "\"We will seize our destiny!\"")

# mio.addSpecialLines("\"Your fate was sealed when you rose up against us!\"",
#                     "\"For the greater good!\"",
#                     "\"Oh, we're not done yet!\"",
#                     "\"We will seize our destiny!\"")

#alpha = mia
#omega = hector
#omega.inflictDamage(0)

# alpha.inflict(Status.Panic)
# alpha.inflictStat(1,+7)
# omega.inflictStat(4,-1)
#omega.chargeSpecial(0)

#combatEffects = []

#badaboom = simulate_combat(alpha,omega,False, 3, 0, combatEffects)
#print(badaboom)

# APPLY THE EFFECTS ON THE UNITS BEING AFFECTED AND NOT THE UNIT CAUSING THE EFFECT ON THE MAP
# IF MARTH IS FIGHTING EPHRAIM WITH THREATEN DEF 3, GIVE MARTH (IF UNIT IS WITHIN 2 SPACES WITHIN
# EPHRAIM, GIVE -7 DEF. I AM A GENIUS.

# ATK AND WEAPON SKILLS DO STACK W/ HOW PYTHON MERGES DICTIONARIES
# JUST KEEP IN MIND ONCE YOU GET TO THAT BRIDGE WITH SKILLS NOT MEANT TO STACK

# OR WHAT IF I WANT THAT SOMETIMES >:]
