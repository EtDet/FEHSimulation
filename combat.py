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
    # Another case if attacker does not have weapon...?
    if attacker.HPcur <= 0 or defender.HPcur <= 0 or attacker.getWeapon() == NIL_WEAPON: return (-1,-1)

    attacker.unitCombatInitiates += 1
    defender.enemyCombatInitiates += 1

    # lists of attacker/defender's skills & stats
    atkSkills = attacker.getSkills()
    atkStats = attacker.getStats()
    atkPhantomStats = [0] * 5

    if "phantomSpd" in atkSkills: atkPhantomStats[2] += max(atkSkills["phantomSpd"] * 3 + 2, 10)

    defSkills = defender.getSkills()
    defStats = defender.getStats()
    defPhantomStats = [0] * 5

    if "phantomSpd" in defSkills: defPhantomStats[2] += max(defSkills["phantomSpd"] * 3 + 2, 10)

    unit = [attacker, defender]
    stats = [atkStats, defStats]
    skills = [atkSkills, defSkills]
    phantomStats = [atkPhantomStats, defPhantomStats]

    # stored combat buffs (death blow, swift sparrow, essentially everything)
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
    else:
        atkAdjacentToAlly = 0
        atkAllyWithin2Spaces = 0
        atkAllyWithin3Spaces = 0
        atkAllyWithin4Spaces = 0

    if isInSim:
        atkFoeWithin2Spaces = attacker.tile.unitsWithinNSpaces(1, False)
    else:
        atkFoeWithin2Spaces = 0

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
    atkHPGreaterEqual25Percent = attacker.HPcur / atkStats[0] >= 0.25
    atkHPGreaterEqual50Percent = attacker.HPcur / atkStats[0] >= 0.50
    atkHPGreaterEqual75Percent = attacker.HPcur / atkStats[0] >= 0.75
    atkHPEqual100Percent = attacker.HPcur == atkStats[0]

    defHPGreaterEqual25Percent = defender.HPcur / defStats[0] >= 0.25
    defHPGreaterEqual50Percent = defender.HPcur / defStats[0] >= 0.50
    defHPGreaterEqual75Percent = defender.HPcur / defStats[0] >= 0.75
    defHPEqual100Percent = defender.HPcur == defStats[0]

    HPGreaterEqual25Percent = [0,0]
    HPGreaterEqual50Percent = [0,0]
    HPGreaterEqual75Percent = [0,0]
    HPEqual100Percent = [0,0]

    for i in range(2):
        HPGreaterEqual25Percent[i] = unit[i].HPcur / stats[i][0] >= 0.25
        HPGreaterEqual50Percent[i] = unit[i].HPcur / stats[i][0] >= 0.50
        HPGreaterEqual50Percent[i] = unit[i].HPcur / stats[i][0] >= 0.75
        HPEqual100Percent[i] = unit[0].HPcur == stats[i][0]

    # If Laslow is within 3 spaces of at least 2 allies who each have total buffs >= 10
    atkTheLaslowCondition = False
    defTheLaslowCondition = False

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
    panicFactor = [AtkPanicFactor, DefPanicFactor]

    # buffs + debuffs calculation
    # throughout combat, PanicFactor * buff produces the current buff value
    if Status.Panic in attacker.statusNeg: AtkPanicFactor *= -1
    if Status.Panic in defender.statusNeg: DefPanicFactor *= -1

    if Status.NullPanic in attacker.statusPos: AtkPanicFactor = 1
    if Status.NullPanic in defender.statusPos: DefPanicFactor = 1

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
    defNullAtkFU = False
    atkDoSkillFU = False # prevent's foe's skills that disable follow-ups
    defDoSkillFU = False

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
    defDmgReduFactor = 1 #

    # pseudo-Miracle effects (refined Tyrfing)
    atkPseudoMiracleEnabled = False
    defPseudoMiracleEnabled = False

    # true damage when attacking
    atkTrueDamage = 0
    defTrueDamage = 0
    # LAMBDA THIS w/ finish skills
    atkFinishTrueDamage = 0
    defFinishTrueDamage = 0

    atkTrueDamageFunc = lambda α: atkTrueDamage + atkFinishTrueDamage * α
    defTrueDamageFunc = lambda δ: defTrueDamage + defFinishTrueDamage * δ

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

    # mid-combat healing per hit, negated by deep wounds
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

    if "fireBoost" in atkSkills and attacker.HPcur >= defender.HPcur + 3: atkCombatBuffs[1] += atkSkills["fireBoost"] * 2
    if "windBoost" in atkSkills and attacker.HPcur >= defender.HPcur + 3: atkCombatBuffs[2] += atkSkills["windBoost"] * 2
    if "earthBoost" in atkSkills and attacker.HPcur >= defender.HPcur + 3: atkCombatBuffs[3] += atkSkills["earthBoost"] * 2
    if "waterBoost" in atkSkills and attacker.HPcur >= defender.HPcur + 3: atkCombatBuffs[4] += atkSkills["waterBoost"] * 2

    if "brazenAtk" in atkSkills and attacker.HPcur / atkStats[HP] <= 0.8: atkCombatBuffs[1] += atkSkills["brazenAtk"]
    if "brazenSpd" in atkSkills and attacker.HPcur / atkStats[HP] <= 0.8: atkCombatBuffs[2] += atkSkills["brazenSpd"]
    if "brazenDef" in atkSkills and attacker.HPcur / atkStats[HP] <= 0.8: atkCombatBuffs[3] += atkSkills["brazenDef"]
    if "brazenRes" in atkSkills and attacker.HPcur / atkStats[HP] <= 0.8: atkCombatBuffs[4] += atkSkills["brazenRes"]

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

    if "caedaVantage" in defSkills and (attacker.wpnType in ["Sword", "Lance", "Axe", "CBow"] or attacker.move == 3 or defender.HPcur/defStats[0] <= 0.75):
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

    if "HPWarrior" in atkSkills and atkStats[0] >= defender.curHP + 1: map(lambda x: x + 4, atkCombatBuffs)
    if "HPWarrior" in defSkills and defStats[0] >= attacker.curHP + 1: map(lambda x: x + 4, defCombatBuffs)

    if ("belovedZofia" in atkSkills and atkHPEqual100Percent) or "belovedZofia2" in atkSkills:
        map(lambda x: x + 4, atkCombatBuffs)
        atkRecoilDmg += 4

    if "A man has fallen into the river in LEGO City!" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        atkPostCombatHealing += 7

    if "ALMMM" in atkSkills and (not atkHPEqual100Percent or not defHPEqual100Percent):
        map(lambda x: x + 4, atkCombatBuffs)
        atkMidCombatHeal += 7

    if "SUPER MARIO!!!" in atkSkills and attacker.specialCount == 0:
        map(lambda x: x + 3, atkCombatBuffs)

    if "SUPER MARIO!!!" in defSkills and defender.specialCount == 0:
        map(lambda x: x + 3, atkCombatBuffs)
        ignoreRng = True

    if "berkutBoost" in atkSkills and defHPEqual100Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        atkCombatBuffs[2] -= 5

    if "baseTyrfing" in atkSkills and attacker.HPcur / atkStats[0] <= 0.5:
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

    if "laslowBrave" in atkSkills and atkTheLaslowCondition:
        atkCombatBuffs[1] += 3
        atkCombatBuffs[3] += 3
        braveATKR = True

    if "laslowBrave" in defSkills and defTheLaslowCondition:
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
        if atkHPGreaterEqual25Percent:
            map(lambda x:x+4, atkCombatBuffs)

    if "HERE'S SOMETHING TO BELIEVE IN" in defSkills:
        defSpPierceDR = True
        if defHPGreaterEqual25Percent:
            map(lambda x:x+4, defCombatBuffs)

    if "regalSunshade" in atkSkills and atkHPGreaterEqual25Percent:
        numFoesLeft = 0
        numFoesWithin3Columns3Rows = 0
        atkCombatBuffs[1] += 6
        atkCombatBuffs[3] += 6
        X = 1 if numFoesLeft <= 2 else (2 if 3 <= numFoesLeft <= 5 else 3)
        if X <= numFoesWithin3Columns3Rows: braveATKR

    if "regalSunshade" in defSkills and defHPGreaterEqual25Percent:
        numFoesLeft = 0
        numFoesWithin3Columns3Rows = 0
        defCombatBuffs[1] += 6
        defCombatBuffs[3] += 6
        X = 1 if numFoesLeft <= 2 else (2 if 3 <= numFoesLeft <= 5 else 3)
        if X <= numFoesWithin3Columns3Rows: braveDEFR

    if "thundabrand" in atkSkills and defHPGreaterEqual50Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5
        desperateA = True

    if "thundabrand" in defSkills and atkHPGreaterEqual50Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[1] += 5

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
        map(lambda x: x + 5, atkCombatBuffs)
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

    if "FollowUpEph" in atkSkills and attacker.HPcur / atkStats[0] > 0.90: atkSkillFollowUps += 1

    if "BraveAW" in atkSkills or "BraveAS" in atkSkills or "BraveBW" in atkSkills: braveATKR = True

    if "swordBreak" in atkSkills and defender.wpnType == "Sword" and attacker.HPcur / atkStats[0] > 1.1 - (atkSkills["swordBreak"] * 0.2): atkSkillFollowUps += 1; defSkillFollowUpDenials -= 1
    if "lanceBreak" in atkSkills and defender.wpnType == "Lance" and attacker.HPcur / atkStats[0] > 1.1 - (atkSkills["lanceBreak"] * 0.2): atkSkillFollowUps += 1; defSkillFollowUpDenials -= 1
    if "axeBreak" in atkSkills and defender.wpnType == "Axe" and attacker.HPcur / atkStats[0] > 1.1 - (atkSkills["axeBreak"] * 0.2): atkSkillFollowUps += 1; defSkillFollowUpDenials -= 1
    if "rtomeBreak" in atkSkills and defender.wpnType == "RTome" and attacker.HPcur / atkStats[0] > 1.1 - (atkSkills["rtomeBreak"] * 0.2): atkSkillFollowUps += 1; defSkillFollowUpDenials -= 1
    if "btomeBreak" in atkSkills and defender.wpnType == "BTome" and attacker.HPcur / atkStats[0] > 1.1 - (atkSkills["btomeBreak"] * 0.2): atkSkillFollowUps += 1; defSkillFollowUpDenials -= 1
    if "gtomeBreak" in atkSkills and defender.wpnType == "GTome" and attacker.HPcur / atkStats[0] > 1.1 - (atkSkills["gtomeBreak"] * 0.2): atkSkillFollowUps += 1; defSkillFollowUpDenials -= 1
    if "cBowBreak" in atkSkills and defender.wpnType == "CBow" and attacker.HPcur / atkStats[0] > 1.1 - (atkSkills["cBowBreak"] * 0.2): atkSkillFollowUps += 1; defSkillFollowUpDenials -= 1
    if "cDaggerBreak" in atkSkills and defender.wpnType == "CDagger" and attacker.HPcur / atkStats[0] > 1.1 - (atkSkills["cDaggerBreak"] * 0.2): atkSkillFollowUps += 1; defSkillFollowUpDenials -= 1

    if "spDamageAdd" in atkSkills: atkFixedSpDmgBoost += atkSkills["spDamageAdd"]

    if "firesweep" in atkSkills or "firesweep" in defSkills:
        cannotCounter = True

    if "hardyBearing" in atkSkills:
        hardyBearingAtk = True
        hardyBearingDef = attacker.HPcur/atkStats[0] >= 1.5 - (atkSkills["hardyBearing"] * .5)

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

    if "fireBoost" in defSkills and defender.HPcur >= attacker.HPcur + 3: defCombatBuffs[1] += defSkills["fireBoost"] * 2
    if "windBoost" in defSkills and defender.HPcur >= attacker.HPcur + 3: defCombatBuffs[2] += defSkills["windBoost"] * 2
    if "earthBoost" in defSkills and defender.HPcur >= attacker.HPcur + 3: defCombatBuffs[3] += defSkills["earthBoost"] * 2
    if "waterBoost" in defSkills and defender.HPcur >= attacker.HPcur + 3: defCombatBuffs[4] += defSkills["waterBoost"] * 2

    if "closeDef" in defSkills and attacker.weapon.range == 1:
        defCombatBuffs[3] += defSkills["distDef"] * 2
        defCombatBuffs[4] += defSkills["distDef"] * 2

    if "distDef" in defSkills and attacker.weapon.range == 2:
        defCombatBuffs[3] += defSkills["distDef"] * 2
        defCombatBuffs[4] += defSkills["distDef"] * 2

    if "brazenAtk" in defSkills and defender.HPcur / defStats[HP] <= 0.8: defCombatBuffs[1] += defSkills["brazenAtk"]
    if "brazenSpd" in defSkills and defender.HPcur / defStats[HP] <= 0.8: defCombatBuffs[2] += defSkills["brazenSpd"]
    if "brazenDef" in defSkills and defender.HPcur / defStats[HP] <= 0.8: defCombatBuffs[3] += defSkills["brazenDef"]
    if "brazenRes" in defSkills and defender.HPcur / defStats[HP] <= 0.8: defCombatBuffs[4] += defSkills["brazenRes"]

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

    if "baseTyrfing" in defSkills and defender.HPcur / defStats[0] <= 0.5:
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

    if "sealedFalchion" in defSkills and not HPEqual100Percent:
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

    if "QRW" in defSkills and defender.HPcur / defStats[0] >= 1.0 - (defSkills["QRW"] * 0.1): defSkillFollowUps += 1
    if "QRS" in defSkills and defender.HPcur / defStats[0] >= 1.0 - (defSkills["QRS"] * 0.1): defSkillFollowUps += 1

    if "desperation" in defSkills and defender.HPcur / defStats[0] <= 0.25 * defSkills["desperation"]: desperateA = True

    if "swordBreak" in defSkills and attacker.wpnType == "Sword": defSkillFollowUps += 1; atkSkillFollowUpDenials -= 1
    if "lanceBreak" in defSkills and attacker.wpnType == "Lance": defSkillFollowUps += 1; atkSkillFollowUpDenials -= 1
    if "axeBreak" in defSkills and attacker.wpnType == "Axe": defSkillFollowUps += 1; atkSkillFollowUpDenials -= 1
    if "rtomeBreak" in defSkills and attacker.wpnType == "RTome": defSkillFollowUps += 1; atkSkillFollowUpDenials -= 1
    if "btomeBreak" in defSkills and attacker.wpnType == "BTome": defSkillFollowUps += 1; atkSkillFollowUpDenials -= 1
    if "gtomeBreak" in defSkills and attacker.wpnType == "GTome": defSkillFollowUps += 1; atkSkillFollowUpDenials -= 1
    if "cBowBreak" in defSkills and attacker.wpnType == "CBow": defSkillFollowUps += 1; atkSkillFollowUpDenials -= 1
    if "cDaggerBreak" in defSkills and attacker.wpnType == "CDagger": defSkillFollowUps += 1; atkSkillFollowUpDenials -= 1

    if "spDamageAdd" in defSkills: defFixedSpDmgBoost += defSkills["spDamageAdd"]

    if "vantage" in defSkills and defender.HPcur / defStats[0] <= 0.75 - (0.25 * (3 - defSkills["vantage"])):
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

    if "shez!" in atkSkills and attacker.HPcur / atkStats[0] >= 0.2:
        attackerGainWhenAttacking += 1
        attackerGainWhenAttacked += 1

    if "shez!" in defSkills and defender.HPcur / defStats[0] >= 0.2:
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

    if "guardHP" in atkSkills and attacker.HPcur / atkStats[0] >= atkSkills["guardHP"]:
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

    attackerGainWhenAttacking = attackerGainWhenAttacking + attackerLossWhenAttacking
    attackerGainWhenAttacked = attackerGainWhenAttacked + attackerLossWhenAttacked
    defenderGainWhenAttacking = defenderGainWhenAttacking + defenderLossWhenAttacking
    defenderGainWhenAttacked = defenderGainWhenAttacked + defenderLossWhenAttacked

    attackerGainWhenAttacking = min(max(attackerGainWhenAttacking, -1), 1)
    attackerGainWhenAttacked = min(max(attackerGainWhenAttacked, -1), 1)
    defenderGainWhenAttacking = min(max(defenderGainWhenAttacking, -1), 1)
    defenderGainWhenAttacked = min(max(defenderGainWhenAttacked, -1), 1)

    # WINDSWEEP PLEASE GET RID OF THAT WINDSWEEP CHECK THING IT SUCKS

    if "windsweep" in atkSkills:
        atkSkillFollowUpDenials -= 1
        if atkPhantomStats[2] > defPhantomStats[2] + (-2 * atkSkills["windsweep"] + 7) and defender.getTargetedDef() == -1:
            cannotCounter = True

    # I hate this skill up until level 4 why does it have all those conditions
    if "brashAssault" in atkSkills and (cannotCounter or not(attacker.getRange() == defender.getRange() or ignoreRng)) and attacker.HPcur / atkStats[0] <= 0.1 * atkSkills["brashAssault"] + 0.2:
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

    # TRUE DAMAGE ADDITION
    if "SpdDmg" in atkSkills and atkPhantomStats[2] > defPhantomStats[2]:
        atkTrueDamage += min(math.trunc((atkPhantomStats[2]-defPhantomStats[2]) * 0.1 * atkSkills["SpdDmg"]), atkSkills["SpdDmg"])
    if "SpdDmg" in defSkills and defPhantomStats[2] > atkPhantomStats[2]:
        defTrueDamage += min(math.trunc((defPhantomStats[2]-atkPhantomStats[2]) * 0.1 * defSkills["SpdDmg"]), defSkills["SpdDmg"])

    if "moreeeeta" in atkSkills and atkHPGreaterEqual25Percent: atkTrueDamage += math.trunc(atkStats[2] * 0.1)
    if "moreeeeta" in defSkills and defHPGreaterEqual25Percent: defTrueDamage += math.trunc(defStats[2] * 0.1)

    if "thraicaMoment" in atkSkills and defStats[3] >= defStats[4] + 5: atkTrueDamage += 7
    if "thraciaMoment" in defSkills and atkStats[3] >= atkStats[4] + 5: defTrueDamage += 7

    if "LOVE PROVIIIIDES, PROTECTS US" in atkSkills and atkHPGreaterEqual25Percent: atkTrueDamage += math.trunc(atkStats[2] * 0.15)
    if "LOVE PROVIIIIDES, PROTECTS US" in defSkills and defHPGreaterEqual25Percent: defTrueDamage += math.trunc(defStats[2] * 0.15)

    if "vassalBlade" in atkSkills: atkTrueDamage += math.trunc(atkStats[2] * 0.15)
    if "vassalBlade" in defSkills and defAllyWithin2Spaces: defTrueDamage += math.trunc(defStats[2] * 0.15)

    if "infiniteSpecial" in atkSkills: atkTrueDamage += math.trunc(atkStats[2] * 0.15)
    if "infiniteSpecial" in defSkills: defTrueDamage += math.trunc(defStats[2] * 0.15)

    if "newVTyrfing" in atkSkills and (not atkHPEqual100Percent or defHPGreaterEqual75Percent): atkTrueDamage += math.trunc(atkStats[1] * 0.15)
    if "newVTyrfing" in defSkills: defTrueDamage += math.trunc(defStats[1] * 0.15)

    if "hamburger" in atkSkills: atkTrueDamage += math.trunc(atkStats[3] * 0.15)
    if "hamburger" in atkSkills and defAllyWithin2Spaces: defTrueDamage += math.trunc(defStats[3] * 0.15)

    if "I HATE FIRE JOKES >:(" in atkSkills and spacesMovedByAtkr: atkTrueDamage += math.trunc(defStats[DEF] * 0.10 * min(spacesMovedByAtkr, 4))
    if "I HATE FIRE JOKES >:(" in defSkills and spacesMovedByAtkr: defTrueDamage += math.trunc(atkStats[DEF] * 0.10 * min(spacesMovedByAtkr, 4))

    if "renaisTwins" in atkSkills and (atkHasBonus or atkHasPenalty):
        atkTrueDamage += math.trunc(defStats[3] * 0.20)
        atkMidCombatHeal += math.trunc(defStats[3] * 0.20)

    if "renaisTwins" in defSkills and defAllyWithin2Spaces and (defHasBonus or defHasPenalty):
        defTrueDamage += math.trunc(atkStats[3] * 0.20)
        defMidCombatHeal += math.trunc(atkStats[3] * 0.20)

    if "megaAstra" in atkSkills and atkPhantomStats[1] > defPhantomStats[3]:
        atkTrueDamage += max(math.trunc((atkStats[1] - defStats[3]) * 0.5), 0)

    if "megaAstra" in defSkills and defPhantomStats[1] > atkPhantomStats[3]:
        defTrueDamage += max(math.trunc((defStats[1] - atkStats[3]) * 0.5), 0)

    # transform into lambda function, all for Owain's refined effect
    atkSpTrueDamageFunc = lambda x: atkFixedSpDmgBoost
    defSpTrueDamageFunc = lambda x: defFixedSpDmgBoost

    if "Sacred Stones Strike!" in atkSkills and atkAllyWithin3Spaces:
        atkSpTrueDamageFunc = lambda x: x + atkFixedSpDmgBoost

    if "Sacred Stones Strike!" in defSkills and defAllyWithin3Spaces:
        defSpTrueDamageFunc = lambda x: x + defFixedSpDmgBoost

    # TRUE DAMAGE SUBTRACTION



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

    if attacker.wpnType == "BTome" and "haarEff" in atkSkills:
        oneEffDef = True
    if defender.wpnType == "BTome" and "haarEff" in defSkills:
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

    if (attacker.getColor() == "Blue" and defender.getColor() == "Green") or (attacker.getColor() == "Red" and defender.getColor() == "Blue") or \
            (attacker.getColor() == "Green" and defender.getColor() == "Red") or (attacker.getColor() == "Colorless" and "colorlessAdv" in defSkills):

        if (atkCA == 1 or defCA == 1) and triAdept != -1: triAdept = -1
        if atkCA == 2 and triAdept != -1: triAdept = -1
        if atkCA == 3 and triAdept != -1: triAdept = -5
        atkStats[1] -= math.trunc(atkStats[1] * (0.25 + .05 * triAdept))
        defStats[1] += math.trunc(defStats[1] * (0.25 + .05 * triAdept))

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

    if "FOR THE PRIDE OF BRODIA" in atkSkills: outspeedFactor += 20
    if "FOR THE PRIDE OF BRODIA" in defSkills: outspeedFactor += 20

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
            isFollowUp = A_Count == 2 and followupA and not braveATKR or A_Count in [3, 4] and braveATKR
            isConsecutive = True if A_Count >= 2 and startString2[i - 1] == "A" else False
            attackList.append(Attack(0, isFollowUp, isConsecutive, A_Count, A_Count + D_Count, None if A_Count + D_Count == 1 else attackList[i - 1]))
        else:
            D_Count += 1
            isFollowUp = D_Count == 2 and followupD and not braveDEFR or D_Count in [3, 4] and braveDEFR
            isConsecutive = True if D_Count >= 2 and startString2[i - 1] == "D" else False
            attackList.append(Attack(1, isFollowUp, isConsecutive, D_Count, A_Count + D_Count, None if A_Count + D_Count == 1 else attackList[i - 1]))
        i += 1

    # Damage reduction per hit
    # Computed here due to attack order needing to be computed

    # M!Shez - Crimson Blades - Base
    if "shez!" in atkSkills and attacker.HPcur / atkStats[0] >= 0.4: defHit1Reduction *= 1 - (defDmgReduFactor * 0.4)
    if "shez!" in defSkills and defender.HPcur / atkStats[0] >= 0.4: atkHit1Reduction *= 1 - (atkDmgReduFactor * 0.4)

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
    # yeah that's a lot of stuff to consider
    def attack(striker, strikee, stkSpEffects, steSpEffects, stkStats, steStats, defOrRes, strSpMod, steSpMod,
               curReduction, curMiracle, curTrueDmg, curSpTrueDmg, curHeal, curDWA, spPierce, alwPierce, curTriggered,
               stkDisabledSpecial, steDisabledSpecial):

        stkSpecialTriggered = False
        steSpecialTriggered = False
        dmgBoost = 0

        if striker.specialCount == 0 and striker.getSpecialType() == "Offense" and not stkDisabledSpecial:
            print(striker.getName() + " procs " + striker.getSpName() + ".")
            print(striker.getSpecialLine())
            dmgBoost = getSpecialHitDamage(stkSpEffects, stkStats, steStats, defOrRes) + curSpTrueDmg(min(stkStats[0] - striker.HPcur, 30)) # owain :)
            stkSpecialTriggered = True

        attack = stkStats[1] - steStats[3 + defOrRes]

        if attack < 0: attack = 0
        attack += dmgBoost
        attack += curTrueDmg(striker.specialCount == 0 or curTriggered)
        if striker.getSpecialType() == "Staff": attack = math.trunc(attack * 0.5)
        curReduction = curReduction * (not(stkSpecialTriggered and spPierce) and not(alwPierce))
        attack = math.ceil(attack * curReduction)

        if strikee.specialCount == 0 and strikee.getSpecialType() == "Defense" and not steDisabledSpecial:
            if striker.getRange() == 1 and "closeShield" in steSpEffects:
                print(strikee.getName() + " procs " + strikee.getSpName() + ".")
                print(strikee.getSpecialLine())
                attack -= math.trunc(attack * 0.10 * steSpEffects["closeShield"])
                steSpecialTriggered = True
            elif striker.getRange() == 2 and "distantShield" in steSpEffects:
                print(strikee.getName() + " procs " + strikee.getSpName() + ".")
                print(strikee.getSpecialLine())
                attack -= math.trunc(attack * 0.10 * steSpEffects["distantShield"])
                steSpecialTriggered = True

        curMiracleTriggered = False
        if curMiracle and strikee.HPcur - attack < 1 and strikee.HPcur != 1:
            attack = strikee.HPcur - 1
            curMiracleTriggered = True

        if strikee.specialCount == 0 and "miracleSP" in steSpEffects and strikee.HPcur - attack < 1 and strikee.HPcur != 1 and not curMiracle:
            print(strikee.getName() + " procs " + strikee.getSpName() + ".")
            print(strikee.getSpecialLine())
            attack = strikee.HPcur - 1
            steSpecialTriggered = True

        if curMiracleTriggered: curMiracle = False

        # the attack™
        strikee.HPcur -= attack  # goodness gracious
        print(striker.getName() + " attacks " + strikee.getName() + " for " + str(attack) + " damage.")  # YES THEY DID

        if strikee.HPcur < 1: attack += strikee.HPcur  # to evaluate noontime heal on hit that kills

        striker.specialCount = max(striker.specialCount - (1 + strSpMod), 0)
        strikee.specialCount = max(strikee.specialCount - (1 + steSpMod), 0)

        if stkSpecialTriggered: striker.specialCount = striker.specialMax
        if steSpecialTriggered: striker.specialCount = striker.specialMax

        if ("absorb" in striker.getSkills() or stkSpecialTriggered and "healSelf" in stkSpEffects or curHeal(striker.specialCount == 0 or curTriggered) > 0) and striker.HPcur < stkStats[0]:
            # damage healed from this attack
            totalHealedAmount = 0

            if "absorb" in striker.getSkills():
                amountHealed = math.trunc(attack * 0.5)
            if stkSpecialTriggered and "healSelf" in stkSpEffects:
                amountHealed = math.trunc(attack * 0.1 * stkSpEffects["healSelf"])

            totalHealedAmount = amountHealed + curHeal(striker.specialCount == 0 or curTriggered)

            if Status.DeepWounds in striker.statusNeg:
                amountHealed = amountHealed - math.trunc((1-curDWA) * totalHealedAmount)

            striker.HPcur += totalHealedAmount

            if "absorb" in striker.getSkills():
                print(striker.getName() + " heals " + str(amountHealed) + " HP during combat.")
            if stkSpecialTriggered and "healSelf" in stkSpEffects:
                print(striker.getName() + " restores " + str(amountHealed) + " HP.")

            if striker.HPcur > stkStats[0]: striker.HPcur = stkStats[0]

        return curMiracle, stkSpecialTriggered, steSpecialTriggered

    # PERFORM THE ATTACKS

    i = 0
    while i < len(attackList) and atkAlive and defAlive:
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
        trueDamages = [atkTrueDamageFunc, defTrueDamageFunc]
        spTrueDamages = [atkSpTrueDamageFunc, defSpTrueDamageFunc]
        heals = [atkMidCombatHealFunc, defMidCombatHealFunc]
        deepWoundsAllowance = [atkDeepWoundsHealAllowance, defDeepWoundsHealAllowance]
        dmgReduPierces = [atkSpPierceDR, atkAlwaysPierceDR, defSpPierceDR, defAlwaysPierceDR]
        specialTriggers = [atkSpecialTriggered, defSpecialTriggered]
        spDisables = [atkSpecialDisabled, defSpecialDisabled]

        spongebob = curAtk.attackOwner
        patrick = int(not curAtk.attackOwner)

        curRedu = reductions[spongebob][curAtk.attackNumSelf-1]

        strikeResult = attack(roles[spongebob], roles[patrick], effects[spongebob], effects[patrick], stats[spongebob], stats[patrick],
               checkedDefs[spongebob], gains[spongebob], gains[spongebob + 2], curRedu, miracles[patrick], trueDamages[spongebob], spTrueDamages[spongebob],
               heals[spongebob], deepWoundsAllowance[spongebob], dmgReduPierces[spongebob], dmgReduPierces[spongebob + 2], specialTriggers[spongebob],
               spDisables[spongebob], spDisables[patrick])

        miracles[patrick] = strikeResult[0]

        atkSpecialTriggered = strikeResult[spongebob + 1]
        defSpecialTriggered = strikeResult[patrick + 1]

        # I am dead
        if attacker.HPcur <= 0:
            attacker.HPcur = 0
            atkAlive = False
            print(attacker.getName() + " falls.")

        if defender.HPcur <= 0:
            defender.HPcur = 0
            defAlive = False
            print(defender.getName() + " falls.")

        i += 1  # increment buddy!

    if atkAlive and (atkSelfDmg != 0 or defOtherDmg != 0 or atkPostCombatHealing):
        resultDmg = ((atkSelfDmg + defOtherDmg) - atkPostCombatHealing * int(not(Status.DeepWounds in attacker.statusNeg)))
        attacker.HPcur -= resultDmg
        if resultDmg > 0: print(attacker.getName() + " takes " + str(resultDmg) + " damage after combat.")
        else: print(attacker.getName() + " heals " + str(resultDmg) + " health after combat.")
        if attacker.HPcur < 1: attacker.HPcur = 1
        if attacker.HPcur > atkStats[0]: attacker.HPcur = atkStats[0]

    if defAlive and (defSelfDmg != 0 or atkOtherDmg != 0 or defPostCombatHealing):
        resultDmg = ((defSelfDmg + atkOtherDmg) - defPostCombatHealing * int(not(Status.DeepWounds in defender.statusNeg)))
        defender.HPcur -= resultDmg
        if resultDmg > 0: print(defender.getName() + " takes " + str(defSelfDmg + atkOtherDmg) + " damage after combat.")
        else: print(defender.getName() + " heals " + str(defSelfDmg + atkOtherDmg) + " health after combat.")
        if defender.HPcur < 1: defender.HPcur = 1
        if defender.HPcur > defStats[0]: defender.HPcur = defStats[0]

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

    if atkAlive:
        for m in atkPostCombatStatusesApplied[0]:
            attacker.inflict(m)

    if defAlive:
        for n in defPostCombatStatusesApplied[0]:
            attacker.inflict(n)

    return attacker.HPcur, defender.HPcur


class Attack():
    def __init__(self, attackOwner, isFollowUp, isConsecutive, attackNumSelf, attackNumAll, prevAttack):
        self.attackOwner = attackOwner
        self.isFollowUp = isFollowUp
        self.isConsecutive = isConsecutive
        self.attackNumSelf = attackNumSelf
        self.attackNumAll = attackNumAll
        self.prevAttack = prevAttack

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

# maps are weighted graphs oh god

folkvangr = Weapon("Fólkvangr", "At start of turn, if unit's HP ≤ 50%, grants Atk+5 for 1 turn.", 16, 1, {"defiantAtk": 2})
fensalir = Weapon("Fensalir", "At start of turn, inflicts Atk-4 on foes within 2 spaces through their next actions.", 16, 1, {"threatAtk": 2})
noatun = Weapon("Nóatún", "If unit's HP ≤ 40%, unit can move to a space adjacent to any ally.", 16, 1, {"escRoute": 2})
lordlyLance = Weapon("Lordly Lance", "Effective against armored foes.", 16, 1, {"effArm": 56})
guardianAxe = Weapon("Guardian's Axe", "Accelerates Special trigger (cooldown count-1)", 16, 1, {"slaying": 1})
irisTome = Weapon("Iris's Tome", "Grants bonus to unit’s Atk = total bonuses on unit during combat.", 14, 2, {"combAtk": 0})
bindingBlade = Weapon("Binding Blade", "If foe initiates combat, grants Def/Res+2 during combat.", 16, 1, {"defStance": 1, "resStance": 1})
fujinYumi = Weapon("Fujin Yumi", "Effective against flying foes. If unit's HP ≥ 50%, unit can move through foes' spaces.", 14, 2, {"pass": 2, "effFly": 0})
gloomBreath = Weapon("Gloom Breath",
                     "At start of turn, inflicts Atk/Spd-7 on foes within 2 spaces through their next actions. After combat, if unit attacked, inflicts Atk/Spd-7 on target and foes within 2 spaces of target through their next actions. If foe's Range = 2, calculates damage using the lower of foe's Def or Res.",
                     16, 1, {"threatAtk": 3, "threatSpd": 7, "sealAtk": 3, "sealSpd": 3, "atkSmoke": 3, "spdSmoke": 3, "dragonCheck": 0})
cordeliaLance = Weapon("Cordelia's Lance", "Inflicts Spd-2. If unit initiates combat, unit attacks twice.", 10, 1, {"spdBoost": -2, "BraveAW": 1})
armads = Weapon("Armads", "If unit's HP ≥ 80% and foe initiates combat, unit makes a guaranteed follow-up attack.", 16, 1, {"QRW": 2})
pantherLance = Weapon("Panther Lance", "During combat, boosts unit's Atk/Def by number of allies within 2 spaces × 2. (Maximum bonus of +6 to each stat.)", 16, 1,
                      {"localBoost2Atk": 2, "localBoost2Def": 2})
bullBlade = Weapon("Bull Blade", "During combat, boosts unit's Atk/Def by number of allies within 2 spaces × 2. (Maximum bonus of +6 to each stat.)", 16, 1, {"localBoost2Atk": 2, "localBoost2Def": 2})
darkRoyalSpear = Weapon("Dark Royal Spear", "If foe initiates combat or if foe's HP = 100% at start of combat, grants Atk/Def/Res+5 to unit during combat.", 16, 1, {"berkutBoost": 5})
chercheAxe = Weapon("Cherche's Axe", "Inflicts Spd-5. If unit initiates combat, unit attacks twice.", 11, 1, {"spdBoost": -5, "BraveAW": 1})
durandal = Weapon("Durandal", "If unit initiates combat, grants Atk+4 during combat.", 16, 1, {"atkBlow": 2})
argentBow = Weapon("Argent Bow", "Effective against flying foes. Inflicts Spd-2. If unit initiates combat, unit attacks twice.", 8, 2, {"effFly": 0, "spdBoost": -2, "BraveAW": 1})
solitaryBlade = Weapon("Solitary Blade", "Accelerates Special trigger (cooldown count-1).", 16, 1, {"slaying": 1})
purifyingBreath = Weapon("Purifying Breath",
                         "Slows Special trigger (cooldown count+1). Unit can counterattack regardless of foe's range. If foe's Range = 2, calculates damage using the lower of foe's Def or Res.", 14,
                         1, {"slaying": -1, "dragonCheck": 0, "dCounter": 0})
tomeOfOrder = Weapon("Tome of Order",
                     "Effective against flying foes. Grants weapon-triangle advantage against colorless foes, and inflicts weapon-triangle disadvantage on colorless foes during combat.", 14, 2,
                     {"effFly": 0, "colorlessAdv": 0})
devilAxe = Weapon("Devil Axe", "Grants Atk/Spd/Def/Res+4 during combat, but if unit attacked, deals 4 damage to unit after combat.", 16, 1,
                  {"atkBlow": 2, "spdBlow": 2, "defBlow": 2, "resBlow": 2, "atkStance": 2, "spdStance": 2, "defStance": 2, "resStance": 2, "atkOnlySelfDmg": 4})
forblaze = Weapon("Forblaze", "At start of turn, inflicts Res-7 on foe on the enemy team with the highest Res through its next action.", 14, 2, {"atkChill": 3})
corvusTome = Weapon("Corvus Tome", "Grants weapon-triangle advantage against colorless foes, and inflicts weapon-triangle disadvantage on colorless foes during combat.", 14, 2, {"colorlessAdv": 0})
tacticalBolt = Weapon("Tactical Bolt", "Grants weapon-triangle advantage against colorless foes, and inflicts weapon-triangle disadvantage on colorless foes during combat.", 14, 2,
                      {"colorlessAdv": 0})
arthurAxe = Weapon("Arthur's Axe", "If a bonus granted by a skill like Rally or Hone is active on unit, grants Atk/Spd/Def/Res+3 during combat.", 16, 1,
                   {"buffGrantsAtk": 3, "buffGrantsSpd": 3, "buffGrantsDef": 3, "buffGrantsRes": 3})
axeOfVirility = Weapon("Axe of Virility", "Effective against armored foes.", 16, 1, {"effArm": 0})
siegfried = Weapon("Siegfried", "Unit can counterattack regardless of foe's range.", 16, 1, {"dCounter": 0})
berukaAxe = Weapon("Beruka's Axe", "Accelerates Special trigger (cooldown count-1).", 16, 1, {"slaying": 1})
wingSword = Weapon("Wing Sword", "Effective against armored and cavalry foes.", 16, 1, {"effArm": 0, "effCav": 0})
camillaAxe = Weapon("Camilla's Axe", "If unit is within 2 spaces of a cavalry or flying ally, grants Atk/Spd+4 during combat.", 16, 1, {"camillaBoost": 0})
whitewingLance = Weapon("Whitewing Lance", "Accelerates Special trigger (cooldown count-1).", 16, 1, {"slaying": 1})
marthFalchion = Weapon("Falchion", "Effective against dragon foes. At the start of every third turn, restores 10 HP.", 16, 1, {"effDragon": 0, "recover": 2})
awkFalchion = Weapon("Falchion", "Effective against dragon foes. At the start of every third turn, restores 10 HP.", 16, 1, {"effDragon": 0, "recover": 2})
yato = Weapon("Yato", "If unit initiates combat, grants Spd+4 during combat.", 16, 1, {"spdBlow": 2})
hewnLance = Weapon("Hewn Lance", "Inflicts Spd-5. If unit initiates combat, unit attacks twice.", 11, 1, {"spdBoost": -5, "BraveAW": 1})
stalwartSword = Weapon("Stalwart Sword", "If foe initiates combat, inflicts Atk-6 on foe during combat.", 16, 1, {"draugBlade": 0})
effieLance = Weapon("Effie's Lance", "At start of combat, if unit's HP ≥ 50%, grants Atk+6 during combat.", 16, 1, {"effieLance": 0})
eliseStaff = Weapon("Elise's Staff",
                    "Grants Spd+3. Calculates damage from staff like other weapons. After combat, if unit attacked, inflicts 【Gravity】on target and foes within 1 space of target. 【Gravity】 Restricts target's movement to 1 space through its next action.",
                    14, 2, {"spdBoost": 3, "wrathStaff": 3, "gravityLocal": 0})
whitewingSpear = Weapon("Whitewing Spear", "Effective against armored foes.", 16, 1, {"effArm"})
eternalBreath = Weapon("Eternal Breath",
                       "At start of turn, if an ally is within 2 spaces of unit, grants Atk/Spd/Def/Res+5 to unit and allies within 2 spaces for 1 turn. If foe's Range = 2, calculates damage using the lower of foe's Def or Res.",
                       16, 1, {"honeFae": 0, "dragonCheck": 20})
feliciaPlate = Weapon("Felicia's Plate",
                      "After combat, if unit attacked, inflicts Def/Res-7 on target and foes within 2 spaces through their next actions. Calculates damage using the lower of foe's Def or Res.", 14, 2,
                      {"dagger": 7, "targetLowerDef": 0})

americaSword = Weapon("American Sword", "Super American, believe me.", 16, 1, {"AMERICA":1776})

assault = Weapon("Assault", "", 10, 2, {})
pain = Weapon("Pain", "Deals 10 damage to target after combat.", 3, 2, {"atkOnlyOtherDmg": 10})
painPlus = Weapon("Pain+", "Deals 10 damage to target and foes within 2 spaces of target after combat.", 10, 2, {"atkOnlyOtherDmg": 10, "savageBlow": 4.5})
absorb = Weapon("Absorb", "Restores HP = 50% of damage dealt.", 3, 2, {"absorb": 0})
absorbPlus = Weapon("Absorb+", "Restores HP = 50% of damage dealt. After combat, if unit attacked, restores 7 HP to allies within 2 spaces of unit.", 7, 2, {"absorb": 0})
fear = Weapon("Fear", "After combat, if unit attacked, inflicts Atk-6 on foe through its next action.", 5, 2, {"sealAtk": 2.5})
fearPlus = Weapon("Fear+", "After combat, if unit attacked, inflicts Atk-7 on target and foes within 2 spaces of target through their next actions.", 12, 2, {"sealAtk": 3, "atkSmoke": 3})

sapphireLance = Weapon("Sapphire Lance", "If unit has weapon-triangle advantage, boosts Atk by 20%. If unit has weapon-triangle disadvantage, reduces Atk by 20%.", 8, 1, {"triangleAdeptW": 3})
sapphireLancePlus = Weapon("Sapphire Lance+", "If unit has weapon-triangle advantage, boosts Atk by 20%. If unit has weapon-triangle disadvantage, reduces Atk by 20%.", 12, 1, {"triangleAdeptW": 3})

siegmund = Weapon("Siegmund", "At start of turn, grants Atk+3 to adjacent allies for 1 turn.", 16, 1, {"honeAtk": 2})
siegmundEff = Weapon("Siegmund (+Eff)", "At start of turn, grants Atk+4 to adjacent allies for 1 turn. If unit's HP ≥ 90% and unit initiates combat, unit makes a guaranteed follow-up attack", 16, 1,
                     {"HPBoost": 3, "FollowUpEph": 0})
tyrfingSpd = Weapon("Tyrfing (+Spd)", "At start of combat, if unit's HP ≥ 50%, grants: “If unit’s HP > 1 and foe would reduce unit’s HP to 0, unit survives with 1 HP. (Once per combat. Does not stack.)”", 16, 1, {"pseudoMiracle":0, "HPBoost": 5, "spdBoost": 3})
naga = Weapon("Naga", "Effective against dragon foes. If foe initiates combat, grants Def/Res+2 during combat.", 14, 2, {"defStance": 1, "resStance": 1, "effDragon": 0})

almFalchion = Weapon("Falchion", "Effective against dragons. At the start of every third turn, unit recovers 10 HP.", 16, 1, {"effDragon": 0, "recover": 2})
ragnell = Weapon("Ragnell", "Unit can counterattack regardless of foe's range.", 16, 1, {"dCounter": 0})

nidhogg = Weapon("Nidhogg", "Effective against flying foes. During combat, boosts unit's Atk/Spd/Def/Res by number of adjacent allies × 2.", 14, 2, {"effFly": 0, "owlBoost": 2})

alondite = Weapon("Alondite", "Unit can counterattack regardless of foe's range.", 16, 1, {"dCounter": 0})
alonditeEff = Weapon("Alondite",
                     "Enables counterattack regardless of distance if this unit is attacked. Accelerates Special trigger (cooldown count-1). At start of combat, if unit's HP ≥ 25%, grants Atk/Spd/Def/Res+4.",
                     16, 1, {"dCounter": 0, "slaying": 1, "WILLYOUSURVIVE?": 4})

divTyrfing = Weapon("Divine Tyrfing", "Grants Res+3. Reduces damage from magic foe's first attack by 50%.", 16, 1, {"divTyrfing":0, "resBoost": 3})

resoluteBlade = Weapon("Resolute Blade", "Grants Atk+3. Deals +10 damage when Special triggers.", 16, 1, {"atkBoost": 3, "spDamageAdd": 10})

reginleifEff = Weapon("Reginleif", """Effective against armored and cavalry foes. Grants Atk+3. Unit cannot be slowed by terrain. (Does not apply to impassable terrain.) At start of combat, if unit's Atk > foe's Atk or if【Bonus】is active on unit, grants Atk/Spd/Def/Res+4 to unit during combat. During combat, if unit's Atk > foe's Atk or if【Bonus】is active on unit, unit makes a guaranteed follow-up attack.

【Bonus】
All effects that last "for 1 turn" or "that turn only." Includes bonuses granted by a skill like Rally or Hone and positive status effects (extra movement or effects like Dominance).

If【Bonus】is active on unit, enables 【Canto (Rem. +1)】. At start of even-numbered turns, unit can move 1 extra space. (That turn only. Does not stack.) At start of combat, if unit's HP ≥ 25%, grants Atk/Spd/Def/Res+4 to unit during combat, and if【Bonus】is active on unit, foe cannot make a follow-up attack.

【Bonus】
All effects that last "for 1 turn" or "that turn only." Includes bonuses granted by a skill like Rally or Hone and positive status effects (extra movement or effects like Dominance).

【Canto (Rem. +1)】
After an attack, Assist skill, or structure destruction, unit can move spaces = any movement not already used that turn +1. (If unit used a movement skill that warped them, its remaining movement is 0.)

(Unit moves according to movement type. Once per turn. Cannot attack or assist. Only highest value applied. Does not stack. After moving, if a skill that grants another action would be triggered (like with Galeforce), Canto will trigger after the granted action. Unit's base movement has no effect on movement granted. Cannot warp (using skills like Wings of Mercy) a distance greater than unit's remaining movement +1.)""",
                      16, 1, {"duoEphRef": 0})

testOwain = Weapon("Test Owain", "TEMP", 16, 1, {"Sacred Stones Strike!": 4})

amatsu = Weapon("Amatsu", "Accelerates Special trigger (cooldown count-1). At start of combat, if unit's HP ≥ 50%, unit can counterattack regardless of foe's range.", 16, 1,
                {"amatsuDC": 0, "slaying": 1})

alliedSword = Weapon("Allied Sword", "Grants Atk/Def+4 to allies within 2 spaces during combat. If unit is within 2 spaces of an ally, grants Atk/Def+4 to unit during combat.", 10, 1,
                     {"driveAtk": 3, "driveDef": 3, "alliedAtk": 4, "alliedDef": 4})
alliedSwordPlus = Weapon("Allied Sword+", "Grants Atk/Def+4 to allies within 2 spaces during combat. If unit is within 2 spaces of an ally, grants Atk/Def+4 to unit during combat.", 14, 1,
                         {"driveAtk": 3, "driveDef": 3, "alliedAtk": 4, "alliedDef": 4})

crimsonBlades = Weapon("Crimson Blades",
                       "Grants Spd+5. Inflicts Def/Res-5. Unit attacks twice. At start of combat, the following effects will occur based on unit's HP: if ≥ 20%, grants Special cooldown charge +1 to unit per attack (only highest value applied; does not stack), and also, if ≥ 40%, reduces damage from foe's first attack during combat by 40%.",
                       11, 1, {"spdBoost": 5, "defBoost": -5, "resBoost": -5, "BraveBW": 0, "shez!": 0})

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

hp3 = Skill("HP +3", "Grants HP+3.", {"HPBoost": 3})
hp4 = Skill("HP +4", "Grants HP+4.", {"HPBoost": 4})
hp5 = Skill("HP +5", "Grants HP+5.", {"HPBoost": 5})
atk1 = Skill("Attack +1", "Grants Atk+1", {"atkBoost": 1})
atk2 = Skill("Attack +2", "Grants Atk+2", {"atkBoost": 2})
atk3 = Skill("Attack +3", "Grants Atk+3", {"atkBoost": 3})
spd1 = Skill("Speed +1", "Grants Spd+1", {"spdBoost": 1})
spd2 = Skill("Speed +2", "Grants Spd+2", {"spdBoost": 2})
spd3 = Skill("Speed +3", "Grants Spd+3", {"spdBoost": 3})
def1 = Skill("Defense +1", "Grants Def+1.", {"defBoost": 1})
def2 = Skill("Defense +2", "Grants Def+2.", {"defBoost": 2})
def3 = Skill("Defense +3", "Grants Def+3.", {"defBoost": 3})
res1 = Skill("Resistance +1", "Grants Res+1.", {"resBoost": 1})
res2 = Skill("Resistance +2", "Grants Res+2.", {"resBoost": 2})
res3 = Skill("Resistance +3", "Grants Res+3.", {"resBoost": 3})

hp_atk1 = Skill("HP/Atk 1", "Grants HP +3, Atk +1.", {"HPBoost": 3, "atkBoost": 1})
hp_atk2 = Skill("HP/Atk 2", "Grants HP +4, Atk +2.", {"HPBoost": 4, "atkBoost": 2})
hp_spd1 = Skill("HP/Spd 1", "Grants HP +3, Spd +1.", {"HPBoost": 3, "spdBoost": 1})
hp_spd2 = Skill("HP/Spd 2", "Grants HP +4, Spd +2.", {"HPBoost": 4, "spdBoost": 2})
hp_def1 = Skill("HP/Def 1", "Grants HP +3, Def +1.", {"HPBoost": 3, "defBoost": 1})
hp_def2 = Skill("HP/Def 2", "Grants HP +4, Def +2.", {"HPBoost": 4, "defBoost": 2})
hp_res1 = Skill("HP/Res 1", "Grants HP +3, Res +1.", {"HPBoost": 3, "resBoost": 1})
hp_res2 = Skill("HP/Res 2", "Grants HP +4, Res +2.", {"HPBoost": 4, "resBoost": 2})

atk_spd1 = Skill("Atk/Spd 1", "Grants Atk/Spd +1.", {"atkBoost": 1, "spdBoost": 1})
atk_spd2 = Skill("Atk/Spd 2", "Grants Atk/Spd +2.", {"atkBoost": 2, "spdBoost": 2})
atk_def1 = Skill("Attack/Def +1", "Grants Atk/Def +1.", {"atkBoost": 1, "defBoost": 1})
atk_def2 = Skill("Attack/Def +2", "Grants Atk/Def +2.", {"atkBoost": 2, "defBoost": 2})
atk_res1 = Skill("Attack/Res 1", "Grants Atk/Res +1.", {"atkBoost": 1, "resBoost": 1})
atk_res2 = Skill("Attack/Res 2", "Grants Atk/Res +2.", {"atkBoost": 2, "resBoost": 2})

spd_def1 = Skill("Spd/Def 1", "Grants Spd/Def +1.", {"spdBoost": 1, "defBoost": 1})
spd_def2 = Skill("Spd/Def 2", "Grants Spd/Def +2.", {"spdBoost": 2, "defBoost": 2})
spd_res1 = Skill("Spd/Res 1", "Grants Spd/Res +1.", {"spdBoost": 1, "resBoost": 1})
spd_res2 = Skill("Spd/Res 2", "Grants Spd/Res +2.", {"spdBoost": 2, "resBoost": 2})

def_res1 = Skill("Def/Res 1", "	Grants Def/Res +1.", {"defBoost": 1, "resBoost": 1})
def_res2 = Skill("Def/Res 2", "	Grants Def/Res +2.", {"defBoost": 2, "resBoost": 2})

fortressDef1 = Skill("Fortress Def 1", "Grants Def+3. Inflicts Atk-3.", {"defBoost": 3, "atkBoost": -3})
fortressDef2 = Skill("Fortress Def 2", "Grants Def+4. Inflicts Atk-3.", {"defBoost": 4, "atkBoost": -3})
fortressDef3 = Skill("Fortress Def 3", "Grants Def+5. Inflicts Atk-3.", {"defBoost": 5, "atkBoost": -3})
fortressRes1 = Skill("Fortress Res 1", "Grants Res+3. Inflicts Atk-3.", {"resBoost": 3, "atkBoost": -3})
fortressRes2 = Skill("Fortress Res 2", "Grants Res+4. Inflicts Atk-3.", {"resBoost": 4, "atkBoost": -3})
fortressRes3 = Skill("Fortress Res 3", "Grants Res+5. Inflicts Atk-3.", {"resBoost": 5, "atkBoost": -3})
fortressDefRes1 = Skill("Fort. Def/Res 1", "Grants Def/Res +3. Inflicts Atk -3.", {"defBoost": 3, "resBoost": 3, "atkBoost": -3})
fortressDefRes2 = Skill("Fort. Def/Res 2", "Grants Def/Res +4. Inflicts Atk -3.", {"defBoost": 4, "resBoost": 4, "atkBoost": -3})
fortressDefRes3 = Skill("Fort. Def/Res 3", "Grants Def/Res +6. Inflicts Atk -2.", {"defBoost": 6, "resBoost": 6, "atkBoost": -2})

lifeAndDeath1 = Skill("Life and Death 1", "Grants Atk/Spd +3. Inflicts Def/Res -3.", {"atkBoost": 3, "spdBoost": 3, "defBoost": -3, "resBoost": -3})
lifeAndDeath2 = Skill("Life and Death 2", "Grants Atk/Spd +4. Inflicts Def/Res -4.", {"atkBoost": 4, "spdBoost": 4, "defBoost": -4, "resBoost": -4})
lifeAndDeath3 = Skill("Life and Death 3", "Grants Atk/Spd +5. Inflicts Def/Res -5.", {"atkBoost": 5, "spdBoost": 5, "defBoost": -5, "resBoost": -5})
lifeAndDeath4 = Skill("Life and Death 4", "Grants Atk/Spd +7. Inflicts Def/Res -5.", {"atkBoost": 7, "spdBoost": 7, "defBoost": -5, "resBoost": -5})

fury1 = Skill("Fury 1", "Grants Atk/Spd/Def/Res+1. After combat, deals 2 damage to unit.", {"atkBoost": 1, "spdBoost": 1, "defBoost": 1, "resBoost": 1, "selfDmg": 2})
fury2 = Skill("Fury 2", "Grants Atk/Spd/Def/Res+2. After combat, deals 4 damage to unit.", {"atkBoost": 2, "spdBoost": 2, "defBoost": 2, "resBoost": 2, "selfDmg": 4})
fury3 = Skill("Fury 3", "Grants Atk/Spd/Def/Res+3. After combat, deals 6 damage to unit.", {"atkBoost": 3, "spdBoost": 3, "defBoost": 3, "resBoost": 3, "selfDmg": 6})
fury4 = Skill("Fury 4", "Grants Atk/Spd/Def/Res+4. After combat, deals 8 damage to unit.", {"atkBoost": 4, "spdBoost": 4, "defBoost": 4, "resBoost": 4, "selfDmg": 8})

solidGround1 = Skill("Solid Ground 1", "Grants Atk/Def+3. Inflicts Res-3.", {"atkBoost": 3, "defBoost": 3, "resBoost": -3})
solidGround2 = Skill("Solid Ground 2", "Grants Atk/Def+4. Inflicts Res-4.", {"atkBoost": 4, "defBoost": 4, "resBoost": -4})
solidGround3 = Skill("Solid Ground 3", "Grants Atk/Def+5. Inflicts Res-5.", {"atkBoost": 5, "defBoost": 5, "resBoost": -5})
solidGround4 = Skill("Solid Ground 4", "Grants Atk/Def+7. Inflicts Res-5.", {"atkBoost": 7, "defBoost": 7, "resBoost": -5})
stillWater1 = Skill("Still Water 1", "Grants Atk/Res+3. Inflicts Def-3.", {"atkBoost": 3, "resBoost": 3, "defBoost": -3})
stillWater2 = Skill("Still Water 2", "Grants Atk/Res+4. Inflicts Def-4.", {"atkBoost": 4, "resBoost": 4, "defBoost": -4})
stillWater3 = Skill("Still Water 3", "Grants Atk/Res+5. Inflicts Def-5.", {"atkBoost": 5, "resBoost": 5, "defBoost": -5})
stillWater4 = Skill("Still Water 4", "Grants Atk/Res+7. Inflicts Def-5.", {"atkBoost": 7, "resBoost": 7, "defBoost": -5})

deathBlow1 = Skill("Death Blow 1", "If unit initiates combat, grants Atk+2 during combat.", {"atkBlow": 1})
deathBlow2 = Skill("Death Blow 2", "If unit initiates combat, grants Atk+4 during combat.", {"atkBlow": 2})
deathBlow3 = Skill("Death Blow 3", "If unit initiates combat, grants Atk+6 during combat.", {"atkBlow": 3})
dartingBlow1 = Skill("Darting Blow 1", "If unit initiates combat, grants Spd+2 during combat.", {"spdBlow": 1})
dartingBlow2 = Skill("Darting Blow 2", "If unit initiates combat, grants Spd+4 during combat.", {"spdBlow": 2})
dartingBlow3 = Skill("Darting Blow 3", "If unit initiates combat, grants Spd+6 during combat.", {"spdBlow": 3})
armoredBlow1 = Skill("Armored Blow 1", "If unit initiates combat, grants Def+2 during combat.", {"defBlow": 1})
armoredBlow2 = Skill("Armored Blow 2", "If unit initiates combat, grants Def+4 during combat.", {"defBlow": 2})
armoredBlow3 = Skill("Armored Blow 3", "If unit initiates combat, grants Def+6 during combat.", {"defBlow": 3})
wardingBlow1 = Skill("Warding Blow 1", "If unit initiates combat, grants Res+2 during combat.", {"resBlow": 1})
wardingBlow2 = Skill("Warding Blow 2", "If unit initiates combat, grants Res+4 during combat.", {"resBlow": 2})
wardingBlow3 = Skill("Warding Blow 3", "If unit initiates combat, grants Res+6 during combat.", {"resBlow": 3})

fierceStance1 = Skill("Fierce Stance 1", "If foe initiates combat, grants Atk+2 during combat.", {"atkStance": 1})
fierceStance2 = Skill("Fierce Stance 2", "If foe initiates combat, grants Atk+4 during combat.", {"atkStance": 2})
fierceStance3 = Skill("Fierce Stance 3", "If foe initiates combat, grants Atk+6 during combat.", {"atkStance": 3})
dartingStance1 = Skill("Darting Stance 1", "If foe initiates combat, grants Spd+2 during combat.", {"spdStance": 1})
dartingStance2 = Skill("Darting Stance 2", "If foe initiates combat, grants Spd+4 during combat.", {"spdStance": 2})
dartingStance3 = Skill("Darting Stance 3", "If foe initiates combat, grants Spd+6 during combat.", {"spdStance": 3})
steadyStance1 = Skill("Steady Stance 1", "If foe initiates combat, grants Def+2 during combat.", {"defStance": 1})
steadyStance2 = Skill("Steady Stance 2", "If foe initiates combat, grants Def+4 during combat.", {"defStance": 2})
steadyStance3 = Skill("Steady Stance 3", "If foe initiates combat, grants Def+6 during combat.", {"defStance": 3})
wardingStance1 = Skill("Warding Stance 1", "If foe initiates combat, grants Res+2 during combat.", {"resStance": 1})
wardingStance2 = Skill("Warding Stance 2", "If foe initiates combat, grants Res+4 during combat.", {"resStance": 2})
wardingStance3 = Skill("Warding Stance 3", "If foe initiates combat, grants Res+6 during combat.", {"resStance": 3})

waterBoost3 = Skill("Water Boost 3", "At start of combat, if unit's HP ≥ foe's HP+3, grants Res+6 during combat.", {"waterBoost": 3})

heavyBlade3 = Skill("Heavy Blade 3", "If unit's Atk > foe's Atk, grants Special cooldown charge +1 per unit's attack. (Only highest value applied. Does not stack.)", {"heavyBlade": 3})
flashingBlade3 = Skill("Flashing Blade 3", "If unit's Spd > foe's Spd, grants Special cooldown charge +1 per unit's attack. (Only highest value applied. Does not stack.)", {"flashingBlade": 3})
# HIGHEST TRIANGLE ADEPT LEVEL USED
# SMALLER LEVELS DO NOT STACK WITH ONE ANOTHER
# HIGHEST LEVEL IS BASICALLY MAX

triangleAdept1 = Skill("Triangle Adept 1", "If unit has weapon-triangle advantage, boosts Atk by 10%. If unit has weapon-triangle disadvantage, reduces Atk by 10%.", {"triAdeptS": 1})
triangleAdept2 = Skill("Triangle Adept 2", "If unit has weapon-triangle advantage, boosts Atk by 15%. If unit has weapon-triangle disadvantage, reduces Atk by 15%.", {"triAdeptS": 2})
triangleAdept3 = Skill("Triangle Adept 3", "If unit has weapon-triangle advantage, boosts Atk by 20%. If unit has weapon-triangle disadvantage, reduces Atk by 20%.", {"triAdeptS": 3})

closeCounter = Skill("Close Counter", "Unit can counterattack regardless of foe's range.", {"cCounter": 0})
distanctCounter = Skill("Distant Counter", "Unit can counterattack regardless of foe's range.", {"dCounter": 0})

svalinnShield = Skill("Svalinn Shield", "Neutralizes \"effective against armored\" bonuses.", {"nullEffArm": 0})
graniShield = Skill("Grani's Shield", "Neutralizes \"effective against cavalry\" bonuses.", {"nullEffCav": 0})
ioteShield = Skill("Iote's Shield", "Neutralizes \"effective against fliers\" bonuses.", {"nullEffFly": 0})

bonusDoubler1 = Skill("Bonus Doubler 1", "Grants bonus to Atk/Spd/Def/Res during combat = 50% of current bonus on each of unit’s stats. Calculates each stat bonus independently.", {"bonusDoubler": 1})
bonusDoubler2 = Skill("Bonus Doubler 2", "Grants bonus to Atk/Spd/Def/Res during combat = 75% of current bonus on each of unit’s stats. Calculates each stat bonus independently.", {"bonusDoubler": 2})
bonusDoubler3 = Skill("Bonus Doubler 3", "Grants bonus to Atk/Spd/Def/Res during combat = current bonus on each of unit’s stats. Calculates each stat bonus independently.", {"bonusDoubler": 3})

sorceryBlade1 = Skill("Sorcery Blade 1", "At start of combat, if unit’s HP = 100% and unit is adjacent to a magic ally, calculates damage using the lower of foe’s Def or Res.", {"sorceryBlade": 1})
sorceryBlade2 = Skill("Sorcery Blade 2", "At start of combat, if unit’s HP ≥ 50% and unit is adjacent to a magic ally, calculates damage using the lower of foe’s Def or Res.", {"sorceryBlade": 2})
sorceryBlade3 = Skill("Sorcery Blade 3", "At start of combat, if unit is adjacent to a magic ally, calculates damage using the lower of foe’s Def or Res.", {"sorceryBlade": 3})

# B SKILLS

swordBreaker1 = Skill("Swordbreaker 1", "If unit's HP ≥ 90% in combat against a sword foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"swordBreak": 1})
swordBreaker2 = Skill("Swordbreaker 2", "If unit's HP ≥ 70% in combat against a sword foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"swordBreak": 2})
swordBreaker3 = Skill("Swordbreaker 3", "If unit's HP ≥ 50% in combat against a sword foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"swordBreak": 3})
lanceBreaker1 = Skill("Lancebreaker 1", "If unit's HP ≥ 90% in combat against a lance foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"lanceBreak": 1})
lanceBreaker2 = Skill("Lancebreaker 2", "If unit's HP ≥ 70% in combat against a lance foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"lanceBreak": 2})
lanceBreaker3 = Skill("Lancebreaker 3", "If unit's HP ≥ 50% in combat against a lance foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"lanceBreak": 3})
axeBreaker1 = Skill("Axebreaker 1", "If unit's HP ≥ 90% in combat against an axe foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"axeBreak": 1})
axeBreaker2 = Skill("Axebreaker 2", "If unit's HP ≥ 70% in combat against an axe foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"axeBreak": 2})
axeBreaker3 = Skill("Axebreaker 3", "If unit's HP ≥ 50% in combat against an axe foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"axeBreak": 3})
rtomeBreaker1 = Skill("R Tomebreaker 1", "If unit's HP ≥ 90% in combat against a red tome foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"rtomeBreak": 1})
rtomeBreaker2 = Skill("R Tomebreaker 2", "If unit's HP ≥ 70% in combat against a red tome foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"rtomeBreak": 2})
rtomeBreaker3 = Skill("R Tomebreaker 3", "If unit's HP ≥ 50% in combat against a red tome foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"rtomeBreak": 3})
btomeBreaker1 = Skill("B Tomebreaker 1", "If unit's HP ≥ 90% in combat against a blue tome foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"btomeBreak": 1})
btomeBreaker2 = Skill("B Tomebreaker 2", "If unit's HP ≥ 70% in combat against a blue tome foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"btomeBreak": 2})
btomeBreaker3 = Skill("B Tomebreaker 3", "If unit's HP ≥ 50% in combat against a blue tome foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"btomeBreak": 3})
gtomeBreaker1 = Skill("G Tomebreaker 1", "If unit's HP ≥ 90% in combat against a green tome foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"gtomeBreak": 1})
gtomeBreaker2 = Skill("G Tomebreaker 2", "If unit's HP ≥ 70% in combat against a green tome foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"gtomeBreak": 2})
gtomeBreaker3 = Skill("G Tomebreaker 3", "If unit's HP ≥ 50% in combat against a green tome foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"gtomeBreak": 3})
bowBreaker1 = Skill("Bowbreaker 1", "If unit's HP ≥ 90% in combat against a colorless bow foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"cBowBreaker": 1})
bowBreaker2 = Skill("Bowbreaker 2", "If unit's HP ≥ 70% in combat against a colorless bow foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"cBowBreaker": 2})
bowBreaker3 = Skill("Bowbreaker 3", "If unit's HP ≥ 50% in combat against a colorless bow foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.", {"cBowBreaker": 3})
daggerBreaker1 = Skill("Daggerbreaker 1", "If unit's HP ≥ 90% in combat against a colorless dagger foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.",
                       {"cDaggerBreaker": 1})
daggerBreaker2 = Skill("Daggerbreaker 2", "If unit's HP ≥ 70% in combat against a colorless dagger foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.",
                       {"cDaggerBreaker": 2})
daggerBreaker3 = Skill("Daggerbreaker 3", "If unit's HP ≥ 50% in combat against a colorless dagger foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.",
                       {"cDaggerBreaker": 3})

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

# noah = Hero("Noah", 40, 42, 45, 35, 25, "Sword", 0, marthFalchion, luna, None, None, None)
# mio = Hero("Mio", 38, 39, 47, 27, 29, "BDagger", 0, tacticalBolt, moonbow, None, None, None)

# A HERO NEEDS
# def __init__(self, name, intName, side, game,
#               hp, at, sp, df, rs, wpnType, movement,
#               weapon, assist, special, askill, bskill, cskill, sSeal,
#               blessing):

# print(str(len(heroes)) + " Heroes present. " + str(927-len(heroes)) + " remain to be added.")

# noah.addSpecialLines("\"I'm sorry, but you're in our way!\"",
#                      "\"For the greater good!\"",
#                      "\"The time is now!\"",
#                      "\"We will seize our destiny!\"")

# mio.addSpecialLines("\"Your fate was sealed when you rose up against us!\"",
#                     "\"For the greater good!\"",
#                     "\"Oh, we're not done yet!\"",
#                     "\"We will seize our destiny!\"")

# playerUnits = [marth, robinM, takumi, ephraim]
# enemyUnits = [nowi, alm, hector, bartre]

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