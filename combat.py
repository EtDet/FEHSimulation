import math
import random
from enum import Enum

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



def simulate_combat(attacker, defender, isInSim):
    # lists of attacker/defender's skills & stats
    atkSkills = attacker.getSkills()
    atkStats = attacker.getStats()

    defSkills = defender.getSkills()
    defStats = defender.getStats()

    if attacker.HPcur <= 0 or defender.HPcur <= 0: return "Invalid Combat: One or more units are below 0 HP"

    # is unit affected by panic
    AtkPanicFactor = 1
    DefPanicFactor = 1

    # buffs + debuffs calculation

    if Status.Panic in attacker.statusNeg: AtkPanicFactor *= -1
    if Status.Panic in defender.statusNeg: DefPanicFactor *= -1

    if Status.NullPanic in attacker.statusPos: AtkPanicFactor = 1
    if Status.NullPanic in defender.statusPos: DefPanicFactor = 1

    atkStats[1] += attacker.buff_at * AtkPanicFactor + attacker.debuff_at
    atkStats[2] += attacker.buff_sp * AtkPanicFactor + attacker.debuff_sp
    atkStats[3] += attacker.buff_df * AtkPanicFactor + attacker.debuff_df
    atkStats[4] += attacker.buff_rs * AtkPanicFactor + attacker.debuff_rs

    defStats[1] += defender.buff_at * DefPanicFactor + defender.debuff_at
    defStats[2] += defender.buff_sp * DefPanicFactor + defender.debuff_sp
    defStats[3] += defender.buff_df * DefPanicFactor + defender.debuff_df
    defStats[4] += defender.buff_rs * DefPanicFactor + defender.debuff_rs

    # triangle adept, default of -1
    triAdept = -1

    # cancel affinity, differs between ally and foe for levels 2/3
    atkCA = 0
    defCA = 0

    # ignore range
    ignoreRng = False

    # prevents counterattacks from defender
    cannotCounter = False

    # enables check for firesweep & watersweep
    doWindsweepCheck = False
    doWatersweepCheck = False

    # grants brave effect
    braveATKR = False
    braveDEFR = False

    # vantage
    vantageEnabled = False

    # hardy bearing
    hardyBearingAtk = False
    hardyBearingFoe = False

    # number of follow-ups permitted
    atkSkillFollowUps = 0
    defSkillFollowUps = 0
    atkSpdFollowUps = 0
    defSpdFollowUps = 0

    # special cooldown charge boost (affected by heavy blade, guard, etc.)
    attackerGainWhenAttacking = 0
    attackerGainWhenAttacked = 0

    defenderGainWhenAttacking = 0
    defenderGainWhenAttacked = 0

    atkHit1Reduction = 1
    atkHit2Reduction = 1
    atkHit3Reduction = 1
    atkHit4Reduction = 1

    defHit1Reduction = 1
    defHit2Reduction = 1
    defHit3Reduction = 1
    defHit4Reduction = 1

    # true damage when attacking
    atkFixedTrueDmgBoost = 0
    defFixedTrueDmgBoost = 0

    # true damage when attacking (special only)
    atkFixedSpDmgBoost = 0
    defFixedSpDmgBoost = 0

    # unit deals damage to themselves after combat
    atkDoSelfDmgCheck = False
    defDoSelfDmgCheck = False

    # unit deals damage to enemy after combat
    atkDoOtherDmgCheck = False
    defDoOtherDmgCheck = False

    # damage done to self after combat (can be negative)
    atkSelfDmg = 0
    defSelfDmg = 0

    # damage done to other after combat (can be negative)
    atkOtherDmg = 0
    defOtherDmg = 0

    # list of effects that occur when special triggers
    atkSpEffects = {}

    # loop which checks for each possible skill (ew)

    if "atkBlow" in atkSkills: atkStats[1] += atkSkills["atkBlow"] * 2
    if "spdBlow" in atkSkills: atkStats[2] += atkSkills["spdBlow"] * 2
    if "defBlow" in atkSkills: atkStats[3] += atkSkills["defBlow"] * 2
    if "resBlow" in atkSkills: atkStats[4] += atkSkills["resBlow"] * 2

    if "fireBoost" in atkSkills and attacker.HPcur >= defender.HPcur + 3: atkStats[1] += atkSkills["fireBoost"] * 2
    if "windBoost" in atkSkills and attacker.HPcur >= defender.HPcur + 3: atkStats[2] += atkSkills["windBoost"] * 2
    if "earthBoost" in atkSkills and attacker.HPcur >= defender.HPcur + 3: atkStats[3] += atkSkills["earthBoost"] * 2
    if "waterBoost" in atkSkills and attacker.HPcur >= defender.HPcur + 3: atkStats[4] += atkSkills["waterBoost"] * 2

    if "selfDmg" in atkSkills: atkSelfDmg += atkSkills["selfDmg"]  # damage to self after combat always
    if "atkOnlySelfDmg" in atkSkills: atkDoSelfDmgCheck = True     # damage to attacker after combat iff attacker had attacked
    if "atkOnlyOtherDmg" in atkSkills: atkDoOtherDmgCheck = True   # damage to other unit after combat if attacker had attacked

    if "triAdeptS" in atkSkills and atkSkills["triAdeptS"] > triAdept: triAdept = atkSkills["triAdeptS"]
    if "triAdeptW" in atkSkills and atkSkills["triAdeptW"] > triAdept: triAdept = atkSkills["triAdeptW"]

    if "owlBoost" in atkSkills:
        if not isInSim: numAlliesNearby = 0
        else: numAlliesNearby = 0
        atkStats[1] += 2 * numAlliesNearby
        atkStats[2] += 2 * numAlliesNearby
        atkStats[3] += 2 * numAlliesNearby
        atkStats[4] += 2 * numAlliesNearby

    if "FollowUpEph" in atkSkills and attacker.HPcur / atkStats[0] > 0.90:
        atkSkillFollowUps += 1

    if "berkutBoost" in atkSkills and defender.curHP == defStats[0]:
        atkStats[1] += 5
        atkStats[3] += 5
        atkStats[4] += 5

    if "BraveAW" in atkSkills or "BraveAS" in atkSkills or "BraveBW" in atkSkills: braveATKR = True

    if "swordBreak" in atkSkills and defender.wpnType == "Sword" and attacker.HPcur / atkStats[0] > .50: atkSkillFollowUps += 1; defSkillFollowUps -= 1
    if "lanceBreak" in atkSkills and defender.wpnType == "Lance" and attacker.HPcur / atkStats[0] > .50: atkSkillFollowUps += 1; defSkillFollowUps -= 1
    if "axeBreak" in atkSkills and defender.wpnType == "Axe" and attacker.HPcur / atkStats[0] > .50: atkSkillFollowUps += 1; defSkillFollowUps -= 1
    if "rtomeBreak" in atkSkills and defender.wpnType == "RTome" and attacker.HPcur / atkStats[0] > .50: atkSkillFollowUps += 1; defSkillFollowUps -= 1
    if "btomeBreak" in atkSkills and defender.wpnType == "BTome" and attacker.HPcur / atkStats[0] > .50: atkSkillFollowUps += 1; defSkillFollowUps -= 1
    if "gtomeBreak" in atkSkills and defender.wpnType == "GTome" and attacker.HPcur / atkStats[0] > .50: atkSkillFollowUps += 1; defSkillFollowUps -= 1
    if "cBowBreak" in atkSkills and defender.wpnType == "CBow" and attacker.HPcur / atkStats[0] > .50: atkSkillFollowUps += 1; defSkillFollowUps -= 1
    if "cDaggerBreak" in atkSkills and defender.wpnType == "CDagger" and attacker.HPcur / atkStats[0] > .50: atkSkillFollowUps += 1; defSkillFollowUps -= 1

    if "spDmgAdd" in atkSkills: atkFixedSpDmgBoost += atkSkills["spDmgAdd"]

    if "windsweep" in atkSkills:
        doWindsweepCheck = True
        atkSkillFollowUps -= 1

    if "hardyBearing" in atkSkills:
        hardyBearingAtk = True
        hardyBearingFoe = attacker.HPcur/atkStats[0] >= 1.5 - (atkSkills["hardyBearing"] * .5)

    if "cancelTA" in atkSkills: atkCA = atkSkills["cancelTA"]

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



    defSpEffects = {}

    if "atkStance" in defSkills: defStats[1] += defSkills["atkStance"] * 2
    if "spdStance" in defSkills: defStats[2] += defSkills["spdStance"] * 2
    if "defStance" in defSkills: defStats[3] += defSkills["defStance"] * 2
    if "resStance" in defSkills: defStats[4] += defSkills["resStance"] * 2
    if "draugBlade" in defSkills: atkStats[1] -= 6

    if "fireBoost" in defSkills and defender.HPcur >= attacker.HPcur + 3: defStats[1] += defStats["fireBoost"] * 2
    if "windBoost" in defSkills and defender.HPcur >= attacker.HPcur + 3: defStats[2] += defStats["windBoost"] * 2
    if "earthBoost" in defSkills and defender.HPcur >= attacker.HPcur + 3: defStats[3] += defStats["earthBoost"] * 2
    if "waterBoost" in defSkills and defender.HPcur >= attacker.HPcur + 3: defStats[4] += defStats["waterBoost"] * 2

    if "triAdeptS" in defSkills and defSkills["triAdeptS"] > triAdept: triAdept = defSkills["triAdeptS"]
    if "triAdeptW" in defSkills and defSkills["triAdeptW"] > triAdept: triAdept = defSkills["triAdeptW"]

    if "cCounter" in defSkills or "dCounter" in defSkills: ignoreRng = True

    if "berkutBoost" in defSkills:
        defStats[1] += 5
        defStats[3] += 5
        defStats[4] += 5

    if "BraveDW" in defSkills or "BraveBW" in defSkills: braveDEFR = True

    for key in defSkills:

        if key == "spDmgAdd": defFixedSpDmgBoost += defSkills[key]

        if key == "atkOnlySelfDmg": defDoSelfDmgCheck = True
        if key == "atkOnlyOtherDmg": defDoOtherDmgCheck = True
        if key == "selfDmg": defSelfDmg += defSkills[key]

        if key == "QRW" or key == "QRS": defSkillFollowUps += 1

        if key == "swordBreak" and attacker.wpnType == "Sword": defSkillFollowUps += 1; atkSkillFollowUps -= 1
        if key == "lanceBreak" and attacker.wpnType == "Lance": defSkillFollowUps += 1; atkSkillFollowUps -= 1
        if key == "axeBreak" and attacker.wpnType == "Axe": defSkillFollowUps += 1; atkSkillFollowUps -= 1
        if key == "rtomeBreak" and attacker.wpnType == "RTome": defSkillFollowUps += 1; atkSkillFollowUps -= 1
        if key == "btomeBreak" and attacker.wpnType == "BTome": defSkillFollowUps += 1; atkSkillFollowUps -= 1
        if key == "gtomeBreak" and attacker.wpnType == "GTome": defSkillFollowUps += 1; atkSkillFollowUps -= 1
        if key == "cBowBreak" and attacker.wpnType == "CBow": defSkillFollowUps += 1; atkSkillFollowUps -= 1
        if key == "cDaggerBreak" and attacker.wpnType == "CDagger": defSkillFollowUps += 1; atkSkillFollowUps -= 1

        if key == "vantage":
            if defender.HPcur / defStats[0] <= 0.75 - (0.25 * (3 - defSkills["vantage"])):
                vantageEnabled = True

        if key == "cancelTA":
            defCA = defSkills[key]

        if key == "healSelf": defSpEffects.update({"healSelf": defSkills[key]})
        if key == "defReduce": defSpEffects.update({"defReduce": defSkills[key]})
        if key == "dmgBoost": defSpEffects.update({"dmgBoost": defSkills[key]})
        if key == "resBoostSp": defSpEffects.update({"resBoost": defSkills[key]})
        if key == "closeShield": defSpEffects.update({"closeShield": defSkills[key]})
        if key == "distantShield": defSpEffects.update({"distantShield": defSkills[key]})

    # SPECIAL CHARGE MODIFICATION

    if "heavyBlade" in atkSkills and atkStats[1] > defStats[1] + (-2 * atkSkills["heavyBlade"] + 7):
        attackerGainWhenAttacking += 1
    if "heavyBlade" in defSkills and defStats[1] > atkStats[1] + (-2 * defSkills["heavyBlade"] + 7):
        defenderGainWhenAttacking += 1

    if "shez!" in atkSkills and attacker.HPcur / atkStats[0] >= 0.2:
        attackerGainWhenAttacking += 1
        attackerGainWhenAttacked += 1

    if "shez!" in defSkills and defender.HPcur / defStats[0] >= 0.2:
        defenderGainWhenAttacking += 1
        defenderGainWhenAttacked += 1

    if "flashingBlade" in atkSkills and atkStats[2] > defStats[2] + (-2 * atkSkills["flashingBlade"] + 7):
        attackerGainWhenAttacking += 1
    if "flashingBlade" in defSkills and defStats[2] > atkStats[2] + (-2 * defSkills["flashingBlade"] + 7):
        defenderGainWhenAttacking += 1

    if "guardHP" in atkSkills and attacker.HPcur / atkStats[0] >= atkSkills["guardHP"]:
        defenderGainWhenAttacked -= 1
        defenderGainWhenAttacking -= 1

    attackerGainWhenAttacking = min(max(attackerGainWhenAttacking, -1), 1)
    attackerGainWhenAttacked = min(max(attackerGainWhenAttacked, -1), 1)
    defenderGainWhenAttacking = min(max(defenderGainWhenAttacking, -1), 1)
    defenderGainWhenAttacked = min(max(defenderGainWhenAttacked, -1), 1)

    # WINDSWEEP CHECK

    if doWindsweepCheck and atkStats[2] > defStats[2] + (-2 * atkSkills["windsweep"] + 7) and defender.getTargetedDef() == -1:
        cannotCounter = True

    # EFFECTIVENESS CHECK

    oneEffAtk = False
    oneEffDef = False

    if "effInf" in atkSkills and defender.move == 0:
        atkStats[1] += math.trunc(atkStats[1] * 0.5)
        oneEffAtk = True
    if "effInf" in defSkills and attacker.move == 0:
        defStats[1] += math.trunc(defStats[1] * 0.5)
        oneEffDef = True

    if "effCav" in atkSkills and "nullEffCav" not in defSkills and defender.move == 1:
        atkStats[1] += math.trunc(atkStats[1] * 0.5)
        oneEffAtk = True
    if "effCav" in defSkills and "nullEffCav" not in atkSkills and attacker.move == 1:
        defStats[1] += math.trunc(defStats[1] * 0.5)
        oneEffDef = True

    if "effFly" in atkSkills and "nullEffFly" not in defSkills and defender.move == 2:
        atkStats[1] += math.trunc(atkStats[1] * 0.5)
        oneEffAtk = True
    if "effFly" in defSkills and "nullEffFly" not in atkSkills and attacker.move == 2:
        defStats[1] += math.trunc(defStats[1] * 0.5)
        oneEffDef = True

    if "effArm" in atkSkills and "nullEffArm" not in defSkills and defender.move == 3:
        atkStats[1] += math.trunc(atkStats[1] * 0.5)
        oneEffAtk = True
    if "effArm" in defSkills and "nullEffArm" not in atkSkills and attacker.move == 3:
        defStats[1] += math.trunc(defStats[1] * 0.5)
        oneEffDef = True

    if ("effDrg" in atkSkills or Status.EffDragons in attacker.statusPos) and "nullEffDrg" not in defSkills and (defender.getTargetedDef() == 0 or "loptous" in defSkills) and not oneEffAtk:
        atkStats[1] += math.trunc(atkStats[1] * 0.5)
        oneEffAtk = True

    if ("effDrg" in defSkills or Status.EffDragons in defender.statusPos) and "nullEffDrg" not in atkSkills and (attacker.getTargetedDef() == 0 or "loptous" in atkSkills) and not oneEffDef:
        defStats[1] += math.trunc(defStats[1] * 0.5)
        oneEffDef = True

    if "effMagic" in atkSkills and defender.wpnType in ["RTome", "BTome", "GTome", "CTome"] and not oneEffAtk:
        atkStats[1] += math.trunc(atkStats[1] * 0.5)
        oneEffAtk = True
    if "effMagic" in defSkills and attacker.wpnType in ["RTome", "BTome", "GTome", "CTome"] and not oneEffAtk:
        defStats[1] += math.trunc(defStats[1] * 0.5)
        oneEffDef = True

    if "effBeast" in atkSkills and defender.wpnType in ["RBeast", "BBeast", "GBeast", "CBeast"] and not oneEffAtk:
        atkStats[1] += math.trunc(atkStats[1] * 0.5)
        oneEffAtk = True
    if "effBeast" in defSkills and attacker.wpnType in ["RBeast", "BBeast", "GBeast", "CBeast"] and not oneEffAtk:
        defStats[1] += math.trunc(defStats[1] * 0.5)
        oneEffDef = True

    if "effCaeda" in atkSkills and defender.wpnType in ["Sword", "Lance", "Axe", "CBow"] and not oneEffAtk:
        atkStats[1] += math.trunc(atkStats[1] * 0.5)
        oneEffAtk = True
    if "effCaeda" in defSkills and attacker.wpnType in ["Sword", "Lance", "Axe", "CBow"] and not oneEffDef:
        defStats[1] += math.trunc(defStats[1] * 0.5)
        oneEffDef = True

    if "effShez" in atkSkills:
        if defender.move == 0 and defender.wpnType not in ["RDragon", "BDragon", "GDragon", "CDragon", "RBeast", "BBeast", "GBeast", "CBeast"]:
            threshold = defStats[2] + 20
        else:
            threshold = defStats[2] + 5

        if atkStats[2] >= threshold:
            atkStats[1] += math.trunc(atkStats[1] * 0.5)

    # COLOR ADVANTAGE CHECK

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

    x = int(defender.getTargetedDef() == 1)

    if defender.getTargetedDef() == 0 and "dragonCheck" in defSkills:
        if attacker.getRange() == 2 and atkStats[3] > atkStats[4]:
            x += 1
        elif attacker.getRange() != 2:
            x += 1

    # additional follow-up granted by outspeeding

    if (atkStats[2] > defStats[2] + 4): atkSpdFollowUps += 1

    if (atkStats[2] + 4 < defStats[2]): defSpdFollowUps += 1

    atkAlive = True
    defAlive = True

    # damage reduction per hit

    if "shez!" in atkSkills and attacker.HPcur / atkStats[0] >= 0.4:
        atkHit1Reduction = atkHit1Reduction - 0.4

    if "shez!" in defSkills and defender.HPcur / atkStats[0] >= 0.4:
        defHit1Reduction = defHit1Reduction - 0.4

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

    def attack(striker, strikee, stkSpEffects, steSpEffects, stkStats, steStats, defOrRes, strSpMod, steSpMod):
        stkSpecialTriggered = False
        steSpecialTriggered = False
        dmgBoost = 0

        if striker.specialCount == 0 and striker.getSpecialType() == "Offense":
            print(striker.getName() + " procs " + striker.getSpName() + ".")
            print(striker.getSpecialLine())
            dmgBoost = getSpecialHitDamage(stkSpEffects, stkStats, steStats, defOrRes)
            stkSpecialTriggered = True

        attack = stkStats[1] - steStats[3 + defOrRes]

        if attack < 0: attack = 0
        attack += dmgBoost
        if striker.getSpecialType() == "Staff": attack = math.trunc(attack * 0.5)

        if strikee.specialCount == 0 and strikee.getSpecialType() == "Defense":
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

        # the attack™
        strikee.HPcur -= attack  # goodness gracious
        print(striker.getName() + " attacks " + strikee.getName() + " for " + str(attack) + " damage.")  # YEAH THEY DID

        if strikee.HPcur < 1: attack += strikee.HPcur  # to evaluate noontime damage on hit that kills

        striker.specialCount = max(striker.specialCount - (1 + strSpMod), 0)

        strikee.specialCount = max(strikee.specialCount - (1 + steSpMod), 0)

        if stkSpecialTriggered: striker.specialCount = striker.specialMax
        if steSpecialTriggered: striker.specialCount = striker.specialMax

        if ("absorb" in striker.getSkills() or stkSpecialTriggered and "healSelf" in stkSpEffects) and striker.HPcur < stkStats[0]:
            if "absorb" in striker.getSkills(): amountHealed = math.trunc(attack * 0.5)
            if stkSpecialTriggered and "healSelf" in stkSpEffects: amountHealed = math.trunc(attack * 0.1 * stkSpEffects["healSelf"])
            striker.HPcur += amountHealed
            if "absorb" in striker.getSkills(): print(striker.getName() + " absorbs " + str(amountHealed) + " HP.")
            if stkSpecialTriggered and "healSelf" in stkSpEffects: print(striker.getName() + " restores " + str(amountHealed) + " HP.")
            if striker.HPcur > stkStats[0]: striker.HPcur = stkStats[0]

    # COMPUTE TURN ORDER

    cannotCounter2 = cannotCounter or not(attacker.getRange() == defender.getRange() and ignoreRng)
    followupA = atkSpdFollowUps + atkSkillFollowUps > 0
    followupD = defSpdFollowUps + defSkillFollowUps > 0
    desperateA = False
    desperateD = False

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

    # it makes zero sense how two D's need to be added, but only 1 A, but I don't care it works
    for c in startString:
        if c == 'A' and braveATKR:
            newString += c
        if c == 'D' and braveDEFR:
            newString += c * 2
        else:
            newString += c

    startString = newString

    startString2 = startString
    if cannotCounter2: startString2 = startString.replace("D", "")


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

    # PERFORM ATTACKS

    i = 0
    while i < len(attackList) and atkAlive and defAlive:
        curAtk = attackList[i]

        if curAtk.attackOwner == 0 and curAtk.attackNumSelf == 1 and atkDoSelfDmgCheck == True: atkSelfDmg += atkSkills["atkOnlySelfDmg"]
        if curAtk.attackOwner == 0 and curAtk.attackNumSelf == 1 and atkDoOtherDmgCheck == True: atkOtherDmg += atkSkills["atkOnlyOtherDmg"]
        if curAtk.attackOwner == 1 and curAtk.attackNumSelf == 1 and defDoSelfDmgCheck == True: defSelfDmg += defSkills["atkOnlySelfDmg"]
        if curAtk.attackOwner == 1 and curAtk.attackNumSelf == 1 and defDoOtherDmgCheck == True: defOtherDmg += defSkills["atkOnlyOtherDmg"]

        roles = [attacker, defender]
        effects = [atkSpEffects, defSpEffects]
        stats = [atkStats, defStats]
        checkedDefs = [r, x]
        gains = [attackerGainWhenAttacking, defenderGainWhenAttacking, defenderGainWhenAttacked, attackerGainWhenAttacked]

        spongebob = curAtk.attackOwner
        patrick = int(not curAtk.attackOwner)

        attack(roles[spongebob], roles[patrick], effects[spongebob], effects[patrick], stats[spongebob], stats[patrick], checkedDefs[spongebob], gains[spongebob], gains[spongebob + 2])

        if attacker.HPcur <= 0:
            attacker.HPcur = 0
            atkAlive = False
            print(attacker.getName() + " falls.")

        if defender.HPcur <= 0:
            defender.HPcur = 0
            defAlive = False
            print(defender.getName() + " falls.")

        i += 1

    if atkAlive and atkSelfDmg != 0 or defOtherDmg != 0:
        atkStats[0] -= (atkSelfDmg + defOtherDmg)
        print(attacker.getName() + " takes " + str(atkSelfDmg + defOtherDmg) + " damage after combat.")
        if atkStats[0] < 1: atkStats[0] = 1

    if defAlive and defSelfDmg != 0 or atkOtherDmg != 0:
        defStats[0] -= (defSelfDmg + atkOtherDmg)
        print(defender.getName() + " takes " + str(defSelfDmg + atkOtherDmg) + " damage after combat.")
        if defStats[0] < 1: defStats[0] = 1

    return attacker.HPcur, defender.HPcur


class Attack():
    def __init__(self, attackOwner, isFollowUp, isConsecutive, attackNumSelf, attackNumAll, prevAttack):
        self.attackOwner = attackOwner
        self.isFollowUp = isFollowUp
        self.isConsecutive = isConsecutive
        self.attackNumSelf = attackNumSelf
        self.attackNumAll = attackNumAll
        self.prevAttack = prevAttack


class Hero:
    def __init__(self, name, intName, side, game, hp, at, sp, df, rs, wpnType, movement, weapon, assist, special, askill, bskill, cskill, sSeal, blessing):

        self.name = name  # Unit's name (Julia, Arthur, etc.)
        self.intName = intName  # Unit's specific name (M!Shez, HA!F!Grima, etc.)
        self.side = side  # 0 - player, 1 - enemy

        # FE Game of Origin - used by harmonic skills and Alear's Libération
        # 0 - Heroes
        # 1/3/11/12 - Shadow Dragon/(New) Mystery
        # 2/15 - Gaiden/Echoes
        # 4 - Genealogy of the Holy War
        # 5 - Thracia 776
        # 6 - Binding Blade
        # 7 - Blazing Blade
        # 8 - Sacred Stones
        # 9 - Path of Radiance
        # 10 - Radiant Dawn
        # 13 - Awakening
        # 14 - Fates
        # 16 - Three Houses/Three Hopes
        # 17 - Engage
        # 69 - Tokyo Mirage Sessions ♯FE
        # 99 - Other
        # 313 - Naga/H!Naga (Listed to have FE3 & FE13 as games of origin)
        # 776 - L!Lief (same as Naga w/ FE4 & FE5)
        self.game = game

        self.hp = hp
        self.at = at
        self.sp = sp
        self.df = df
        self.rs = rs

        self.HPcur = self.hp

        self.comp_hp = self.HPcur  # comparative stat used
        self.comp_at = at  # for condiations in skills
        self.comp_sp = sp  # such as heavy or flashing
        self.comp_df = df  # blade, can be affected by
        self.comp_rs = rs  # skills like phantom spd

        self.buff_at = 0  # field buffs for different
        self.buff_sp = 0  # stats, can be negative iff
        self.buff_df = 0  # hero has panic effect, can be
        self.buff_rs = 0  # flipped with Harsh Command+

        self.debuff_at = 0  # field debuffs for different
        self.debuff_sp = 0  # stats, can only be negative
        self.debuff_df = 0  # HC converts into buff, removes
        self.debuff_rs = 0  # debuff values from units

        self.statusPos = []  # array of positive status effects currently held, cleared upon start of unit's turn
        self.statusNeg = []  # array of positive status effects currently held, cleared upon end of unit's action

        self.growth_hp = 0  # growth rates for given unit
        self.growth_at = 0  # mainly used to determine
        self.growth_sp = 0  # assets & flaws, as well as
        self.growth_df = 0  # superassets and superflaws
        self.growth_rs = 0  # asc assets too they're neat

        # specific unit skills
        self.weapon = weapon
        self.assist = assist
        self.special = special
        self.askill = askill
        self.bskill = bskill
        self.cskill = cskill
        self.sSeal = sSeal

        tempSkills = self.getSkills()

        if "HPBoost" in tempSkills: self.hp += tempSkills["HPBoost"]; self.HPcur += tempSkills["HPBoost"]
        if "atkBoost" in tempSkills: self.at += tempSkills["atkBoost"]
        if "spdBoost" in tempSkills: self.sp += tempSkills["spdBoost"]
        if "defBoost" in tempSkills: self.df += tempSkills["defBoost"]
        if "resBoost" in tempSkills: self.rs += tempSkills["resBoost"]

        if self.weapon is not None: self.at += self.weapon.getMT()

        self.wpnType = wpnType
        self.move = movement  # 0 - inf, 1 - cav, 2 - fly, 3 - arm
        self.moveTiles = -(abs(self.move - 1)) + 3  # num of tiles unit can move

        self.specialCount = -1
        self.specialMax = -1
        if self.special is not None:
            if "slaying" in weapon.getEffects():
                self.specialCount = self.special.cooldown - weapon.getEffects()["slaying"]
                self.specialMax = self.special.cooldown - weapon.getEffects()["slaying"]
                if self.specialCount < 1: self.specialCount = 1
                if self.specialMax < 1: self.specialMax = 1

            else:
                self.specialCount = self.special.cooldown
                self.specialMax = self.special.cooldown

        self.merges = 0
        self.dragonflowers = 0

        self.allySupport = None
        self.summonerSupport = None

        self.blessing = blessing

        self.duoSkill = None
        self.harmoSkill = None

        self.combatCount = 0

        self.tile = None
        self.passStatus = False

        self.spLines = [""] * 4

    def getColor(self):
        if self.wpnType == "Sword" or self.wpnType == "RBow" or self.wpnType == "RDagger" or self.wpnType == "RTome" or self.wpnType == "RDragon" or self.wpnType == "RBeast":
            return "Red"
        if self.wpnType == "Axe" or self.wpnType == "GBow" or self.wpnType == "GDagger" or self.wpnType == "GTome" or self.wpnType == "GDragon" or self.wpnType == "GBeast":
            return "Green"
        if self.wpnType == "Lance" or self.wpnType == "BBow" or self.wpnType == "BDagger" or self.wpnType == "BTome" or self.wpnType == "BDragon" or self.wpnType == "BBeast":
            return "Blue"
        else:
            return "Colorless"

    # class Color(Enum):
    #    Sword,RBow,RDagger,RTome,RDragon,RBeast = 0
    #    Lance,BBow,BDagger,BTome,BDragon,BBeast = 1
    #    Axe,GBow,GDagger,GTome,GDragon,GBeast = 2
    #    Staff,CBow,CDagger,CTome,CDragon,CBeast = 3

    def inflict(self, status):
        if status.value > 100 and status not in self.statusPos:
            self.statusPos.append(status)
            print(self.name + " receives " + status.name + " (+).")
        elif status.value < 100 and status not in self.statusNeg:
            self.statusNeg.append(status)
            print(self.name + " receives " + status.name + " (-).")

    def clearPosStatus(self):
        self.posStatus.clear()

    def clearNegStatus(self):
        self.negStatus.clear()

    def inflictStat(self, stat, num):
        if num > 0:
            match stat:
                case 1:
                    self.buff_at = max(self.buff_at, num)
                case 2:
                    self.buff_sp = max(self.buff_sp, num)
                case 3:
                    self.buff_df = max(self.buff_df, num)
                case 4:
                    self.buff_rs = max(self.buff_rs, num)
        elif num < 0:
            match stat:
                case 1:
                    self.debuff_at = min(self.debuff_at, num)
                case 2:
                    self.debuff_sp = min(self.debuff_sp, num)
                case 3:
                    self.debuff_df = min(self.debuff_df, num)
                case 4:
                    self.debuff_rs = min(self.debuff_rs, num)

        statStr = ""
        match stat:
            case 1:
                statStr = "Atk"
            case 2:
                statStr = "Spd"
            case 3:
                statStr = "Def"
            case 4:
                statStr = "Res"

        print(self.name + "'s " + statStr + " was modified by " + str(num) + ".")

    def chargeSpecial(self, charge):
        if charge != -1:
            # will decrease special count by charge
            self.specialCount = max(0, self.specialCount - charge)
            self.specialCount = min(self.specialCount, self.specialMax)

            print(self.name + "'s special was charged by " + str(charge) + ". Currently is: " + str(self.specialCount))

    def inflictDamage(self, damage):
        self.HPcur -= damage
        if self.HPcur < 1: self.HPcur = 1
        print(self.name + " takes " + str(damage) + " damage out of combat.")

    def setTile(self, tile):
        self.tile = tile

    def getPass(self):
        return self.passStatus

    def setPass(self, bool):
        self.passStatus = bool

    def getTargetedDef(self):
        isTome = self.wpnType == "RTome" or self.wpnType == "BTome" or self.wpnType == "GTome" or self.wpnType == "CTome" or self.wpnType == "Staff"
        isDragon = self.wpnType == "RDragon" or self.wpnType == "BDragon" or self.wpnType == "GDragon" or self.wpnType == "CDragon"

        if isTome:
            return 1
        elif isDragon:
            return 0
        else:
            return -1

    def getRange(self):
        return self.weapon.getRange()

    def getWeaponType(self):
        return self.wpnType

    def getWeapon(self):
        if self.weapon is None: return Weapon("Null", "Null Weapon", 0, 0, {})
        return self.weapon

    def getAssist(self):
        return self.assist

    def getSkills(self):
        heroSkills = {}
        if self.weapon != None: heroSkills.update(self.weapon.getEffects())
        if self.special != None: heroSkills.update(self.special.getEffects())
        if self.askill != None: heroSkills.update(self.askill.getEffects())
        if self.bskill != None: heroSkills.update(self.bskill.getEffects())
        if self.cskill != None: heroSkills.update(self.cskill.getEffects())
        if self.sSeal != None: heroSkills.update(self.sSeal.getEffects())

        return heroSkills

    def getCooldown(self):
        if self.special != None:
            return self.special.getCooldown()
        else:
            return -1

    def getStats(self):
        return [self.hp, self.at, self.sp, self.df, self.rs]

    def setStats(self, stats):
        self.hp = stats[0]
        self.at = stats[1]
        self.sp = stats[2]
        self.df = stats[3]
        self.rs = stats[4]

    def getName(self):
        return self.name

    def getSpName(self):
        return self.special.getName()

    def getSpecialType(self):
        if self.special is not None:
            return self.special.type.name
        else:
            return ""

    def addSpecialLines(self, line0, line1, line2, line3):

        self.spLines[0] = line0
        self.spLines[1] = line1
        self.spLines[2] = line2
        self.spLines[3] = line3

    def getSpecialLine(self):
        x = random.randint(0, 3)
        return self.spLines[x]

    def haveAssist(self):
        if self.assist == None:
            return False
        else:
            return True

    def attackType(self):
        if self.weapon == None:
            return 0
        else:
            if self.weapon.getRange() == 1:
                return 2
            else:
                return 1

    def getSortKey(self):
        return (

        )


class Weapon:
    def __init__(self, name, desc, mt, range, effects):
        self.name = name
        self.desc = desc
        self.mt = mt
        self.range = range
        self.effects = effects

    def getMT(self):
        return self.mt

    def getEffects(self):
        return self.effects

    def getRange(self):
        return self.range

    def __str__(self):
        print(self.name + " \nMt: " + str(self.mt) + " Rng: " + str(self.range) + "\n" + self.desc)
        return ""


class Skill:
    def __init__(self, name, desc, effects):
        self.name = name
        self.desc = desc
        self.effects = effects

    def getEffects(self):
        return self.effects

    def __str__(self):
        print(self.name + "\n" + self.desc)
        return ""


class SpecialType(Enum):
    Offense = 0
    Defense = 1
    AreaOfEffect = 2
    Galeforce = 3
    Dancer = 4


class Special(Skill):
    def __init__(self, name, desc, effects, cooldown, type):
        self.name = name
        self.desc = desc
        self.effects = effects
        self.cooldown = cooldown
        self.type = type

    def getCooldown(self):
        return self.cooldown

    def getName(self):
        return self.name


class Blessing():
    def __init__(self, element, boostType, stat):
        # 9 - none
        # 0 - fire, 1 - water, 2 - wind, 3 - earth
        # 4 - light, 5 - dark, 6 - astra, 7 - anima
        self.element = element

        # 9 - none
        # 0 - blessing, for non-legendary/mythic unit
        # 1 - legendary effect 1 - stat boost
        #     OR mythic effect 1 - AR boost + stat boost
        # 2 - legendary effect 2 - pair up
        # 3 - legendary effect 3 - stat boost + pair up
        self.boostType = boostType

        # 9 - none
        # 1 - atk, 2 - spd, 3 - def, 4 - res
        self.stat = stat


null_blessing = Blessing(9, 9, 9)
fire_blessing = Blessing(0, 0, 9)
astra_blessing = Blessing(6, 0, 9)
L_lucina = Blessing(2, 1, 2)
earth_pair = Blessing(3, 2, 9)
L_myrrh = Blessing(2, 3, 3)
M_seiðr = Blessing(6, 1, 1)


class Stat(Enum):
    HP = 0
    ATK = 1
    SPD = 2
    DEF = 3
    RES = 4


class DuoSkill:
    def __init__(self, effect):
        # 0 - 20 non-special AOE damage to enemies within 3 columns
        # 1 - Inf & Arm allies within 2 spaces and self gain MobilityUp
        # 2 - Grants Atk/Spd/Def/Res+3 and BonusDoubler to Arm and Fly allies within 3 rows
        # 3 - Special cooldown -2 to self and Inf allies within 3 rows and columns
        # 4 - Neutralizes stat penalties and negative penalties, restores 30HP, and grants to Atk/Spd+6 on self and allies within 5 rows and columns
        # 5 - Grants Def/Res+6 and grants NullEffDragons and NullEffArmors to self and allies within 5 rows and columns
        # 6 - Grants MobilityUp to self and adjacent Fly allies
        # 7 - Grants Dominance to self and allies within 3 columns and inflicts Def/Res-7 on foes within 3 columns
        # 8 - Grants Desperation to self and allies within 2 spaces (WAIT NO THERE'S MORE THAN ONE TYPE OF REUSABLE DUO SKILL COME BACK TO THIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIISSSS)
        # 9 - Moves adjacent allies to other side of unit, if space is available for targeted unit

        effect = effect
        oncePerMap = False if effect in [8, 9] else True


class HarmonicSkill(DuoSkill):
    def __init__(self, hEffect, secondGame):
        hEffect = hEffect
        secondGame = secondGame


# positive status effects are removed upon the start of the next controllable phase
# negative status effects are removed upon the unit finishing that turn's action

# 🔴 - combat
# 🔵 - movement
# 🟢 - other

class Status(Enum):
    # negative

    Gravity = 0  # 🔵 Movement reduced to 1
    Panic = 1  # 🔴 Buffs are negated & treated as penalties
    NullCounterattacks = 2  # 🔴 Unable to counterattack
    TriAdept = 4  # 🔴 Triangle Adept 3, weapon tri adv/disadv affected by 20%
    Guard = 5  # 🔴 Special charge -1
    Isolation = 8  # 🟢 Cannot use or receive assist skills
    DeepWounds = 17  # 🟢 Cannot recover HP
    Stall = 26  # 🔵 Converts MobilityUp to Gravity
    FalseStart = 29  # 🟢 Disables "at start of turn" skills, does not neutralize beast transformations or reusable duo/harmonized skills, cancelled by Odd/Even Recovery Skills
    CantoControl = 32  # 🔵 If range = 1 Canto skill becomes Canto 1, if range = 2, turn ends when canto triggers
    Exposure = 38  # 🔴 Foe's attacks deal +10 true damage
    Undefended = 41  # 🔴 Cannot be protected by savior
    Feud = 42  # 🔴 Disables all allies' skills (excluding self) in combat, does not include savior, but you get undefended if you get this because Embla
    Sabotage = 48  # 🔴 Reduces atk/spd/def/res by lowest debuff among unit & allies within 2 spaces during combat
    Discord = 49  # 🔴 Reduces atk/spd/def/res by 2 + number of allies within 2 spaces of unit, max 3 during combat

    # positive

    MobilityUp = 103  # 🔵 Movement increased by 1, cancelled by Gravity
    AirOrders = 106  # 🔵 Unit can move to space adjacent to ally within 2 spaces
    EffDragons = 107  # 🔴 Gain effectiveness against dragons
    BonusDoubler = 109  # 🔴 Gain atk/spd/def/res boost by current bonus on stat, canceled by Panic
    NullEffDragons = 110  # 🔴 Gain immunity to "eff against dragons"
    NullEffArmors = 111  # 🔴 Gain immunity to "eff against armors"
    Dominance = 112  # 🔴 Deal true damage = number of stat penalties on foe (including Panic + Bonus)
    ResonanceBlades = 113  # 🔴 Grants Atk/Spd+4 during combat
    Desperation = 114  # 🔴 If unit initiates combat and can make follow-up attack, makes follow-up attack before foe can counter
    ResonanceShields = 115  # 🔴 Grants Def/Res+4 during combat and foe cannot make a follow-up attack in unit's first combat
    Vantage = 116  # 🔴 Unit counterattacks before foe's first attack
    FallenStar = 118  # 🔴 Reduces damage from foe's first attack by 80% in unit's first combat in player phase and first combat in enemy phase
    CancelFollowUp = 119  # 🔴 Foe cannot make a follow-up attack
    NullEffFlyers = 120  # 🔴 Gain immunity to "eff against flyers"
    Dodge = 121  # 🔴 If unit's spd > foe's spd, reduces combat & non-Røkkr AoE damage by X%, X = (unit's spd - foe's spd) * 4, max of 40%
    MakeFollowUp = 122  # 🔴 Unit makes follow-up attack when initiating combat
    TriAttack = 123  # 🔴 If within 2 spaces of 2 allies with TriAttack and initiating combat, unit attacks twice
    NullPanic = 124  # 🔴 Nullifies Panic
    CancelAffinity = 125  # 🔴 Cancel Affinity 3, reverses weapon triangle to neutral if Triangle Adept-having unit/foe has advantage
    NullFollowUp = 127  # 🔴 Disables skills that guarantee foe's follow-ups or prevent unit's follow-ups
    Pathfinder = 128  # 🔵 Unit's space costs 0 to move to by allies
    NullBonuses = 130  # 🔴 Neutralizes foe's bonuses in combat
    GrandStrategy = 131  # 🔴 If negative penalty is present on foe, grants atk/spd/def/res during combat equal to penalty * 2 for each stat
    EnGarde = 133  # 🔴 Neutralizes damage outside of combat, except AoE damage
    SpecialCharge = 134  # 🔴 Special charge +1 during combat
    Treachery = 135  # 🔴 Deal true damage = number of stat bonuses on unit (not including Panic + Bonus)
    WarpBubble = 136  # 🔵 Foes cannot warp onto spaces within 4 spaces of unit (does not affect pass skills)
    Charge = 137  # 🔵 Unit can move to any space up to 3 spaces away in cardinal direction, terrain/skills that halt (not slow) movement still apply, treated as warp movement
    Canto1 = 139  # 🔵 Can move 1 space after combat (not writing all the canto jargon here)
    FoePenaltyDoubler = 140  # 🔴 Inflicts atk/spd/def/res -X on foe equal to current penalty on each stat
    DualStrike = 143  # 🔴 If unit initiates combat and is adjacent to unit with DualStrike, unit attacks twice
    TraverseTerrain = 144  # 🔵 Ignores slow terrain (bushes/trenches)
    ReduceAoE = 145  # 🔴 Reduces non-Røkkr AoE damage taken by 80%
    NullPenalties = 146  # 🔴 Neutralizes unit's penalties in combat
    Hexblade = 147  # 🔴 Damage inflicted using lower of foe's def or res (applies to AoE skills)


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
naga = Weapon("Naga", "Effective against dragon foes. If foe initiates combat, grants Def/Res+2 during combat.", 14, 2, {"defStance": 1, "resStance": 1, "effDragon": 0})

almFalchion = Weapon("Falchion", "Effective against dragons. At the start of every third turn, unit recovers 10 HP.", 16, 1, {"effDragon": 0, "recover": 2})
ragnell = Weapon("Ragnell", "Unit can counterattack regardless of foe's range.", 16, 1, {"dCounter": 0})

nidhogg = Weapon("Nidhogg", "Effective against flying foes. During combat, boosts unit's Atk/Spd/Def/Res by number of adjacent allies × 2.", 14, 2, {"effFly": 0, "owlBoost": 2})

alondite = Weapon("Alondite", "Unit can counterattack regardless of foe's range.", 16, 1, {"dCounter": 0})
alonditeEff = Weapon("Alondite",
                     "Enables counterattack regardless of distance if this unit is attacked. Accelerates Special trigger (cooldown count-1). At start of combat, if unit's HP ≥ 25%, grants Atk/Spd/Def/Res+4.",
                     16, 1, {"dCounter": 0, "slaying": 1, "WILLYOUSURVIVE?": 4})

resoluteBlade = Weapon("Resolute Blade", "Grants Atk+3. Deals +10 damage when Special triggers.", 16, 1, {"atkBoost": 3, "spDmgAdd": 10})

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

squadAceA1 = Skill("Squad Ace A 1", "Grants HP+3.", {"HPBoost": 3})
squadAceA2 = Skill("Squad Ace A 2", "Grants HP+4.", {"HPBoost": 4})
squadAceA3 = Skill("Squad Ace A 3", "Grants HP+5.", {"HPBoost": 5})
squadAceB1 = Skill("Squad Ace B 1", "Grants Def+1.", {"defBoost": 1})
squadAceB2 = Skill("Squad Ace B 2", "Grants Def+2.", {"defBoost": 2})
squadAceB3 = Skill("Squad Ace B 3", "Grants Def+3.", {"defBoost": 3})
squadAceC1 = Skill("Squad Ace C 1", "Grants Res+1.", {"resBoost": 1})
squadAceC2 = Skill("Squad Ace C 2", "Grants Res+2.", {"resBoost": 2})
squadAceC3 = Skill("Squad Ace C 3", "Grants Res+3.", {"resBoost": 3})
squadAceD1 = Skill("Squad Ace D 1", "Grants Spd+1.", {"spdBoost": 1})
squadAceD2 = Skill("Squad Ace D 2", "Grants Spd+2.", {"spdBoost": 2})
squadAceD3 = Skill("Squad Ace D 3", "Grants Spd+3.", {"spdBoost": 3})
squadAceE1 = Skill("Squad Ace E 1", "Grants Atk+1.", {"atkBoost": 1})
squadAceE2 = Skill("Squad Ace E 2", "Grants Atk+2.", {"atkBoost": 2})
squadAceE3 = Skill("Squad Ace E 3", "Grants Atk+3.", {"atkBoost": 3})
squadAceF1 = Skill("Squad Ace F 1", "Grants HP+3.", {"HPBoost": 3})
squadAceF2 = Skill("Squad Ace F 2", "Grants HP+4.", {"HPBoost": 4})
squadAceF3 = Skill("Squad Ace F 3", "Grants HP+5.", {"HPBoost": 5})
squadAceG1 = Skill("Squad Ace G 1", "Grants Def+1.", {"defBoost": 1})
squadAceG2 = Skill("Squad Ace G 2", "Grants Def+2.", {"defBoost": 2})
squadAceG3 = Skill("Squad Ace G 3", "Grants Def+3.", {"defBoost": 3})
squadAceH1 = Skill("Squad Ace H 1", "Grants Res+1.", {"resBoost": 1})
squadAceH2 = Skill("Squad Ace H 2", "Grants Res+2.", {"resBoost": 2})
squadAceH3 = Skill("Squad Ace H 3", "Grants Res+3.", {"resBoost": 3})
squadAceI1 = Skill("Squad Ace I 1", "Grants Spd+1.", {"spdBoost": 1})
squadAceI2 = Skill("Squad Ace I 2", "Grants Spd+2.", {"spdBoost": 2})
squadAceI3 = Skill("Squad Ace I 3", "Grants Spd+3.", {"spdBoost": 3})
squadAceJ1 = Skill("Squad Ace J 1", "Grants Atk+1.", {"atkBoost": 1})
squadAceJ2 = Skill("Squad Ace J 2", "Grants Atk+2.", {"atkBoost": 2})
squadAceJ3 = Skill("Squad Ace J 3", "Grants Atk+3.", {"atkBoost": 3})
squadAceK1 = Skill("Squad Ace K 1", "Grants HP+3.", {"HPBoost": 3})
squadAceK2 = Skill("Squad Ace K 2", "Grants HP+4.", {"HPBoost": 4})
squadAceK3 = Skill("Squad Ace K 3", "Grants HP+5.", {"HPBoost": 5})
squadAceL1 = Skill("Squad Ace L 1", "Grants Def+1.", {"defBoost": 1})
squadAceL2 = Skill("Squad Ace L 2", "Grants Def+2.", {"defBoost": 2})
squadAceL3 = Skill("Squad Ace L 3", "Grants Def+3.", {"defBoost": 3})
squadAceM1 = Skill("Squad Ace M 1", "Grants Res+1.", {"resBoost": 1})
squadAceM2 = Skill("Squad Ace M 2", "Grants Res+2.", {"resBoost": 2})
squadAceM3 = Skill("Squad Ace M 3", "Grants Res+3.", {"resBoost": 3})
squadAceN1 = Skill("Squad Ace N 1", "Grants Spd+1.", {"spdBoost": 1})
squadAceN2 = Skill("Squad Ace N 2", "Grants Spd+2.", {"spdBoost": 2})
squadAceN3 = Skill("Squad Ace N 3", "Grants Spd+3.", {"spdBoost": 3})
squadAceO1 = Skill("Squad Ace O 1", "Grants Atk+1.", {"atkBoost": 1})
squadAceO2 = Skill("Squad Ace O 2", "Grants Atk+2.", {"atkBoost": 2})
squadAceO3 = Skill("Squad Ace O 3", "Grants Atk+3.", {"atkBoost": 3})
squadAceP1 = Skill("Squad Ace P 1", "Grants HP+3.", {"HPBoost": 3})
squadAceP2 = Skill("Squad Ace P 2", "Grants HP+4.", {"HPBoost": 4})
squadAceP3 = Skill("Squad Ace P 3", "Grants HP+5.", {"HPBoost": 5})
squadAceQ1 = Skill("Squad Ace Q 1", "Grants Def+1.", {"defBoost": 1})
squadAceQ2 = Skill("Squad Ace Q 2", "Grants Def+2.", {"defBoost": 2})
squadAceQ3 = Skill("Squad Ace Q 3", "Grants Def+3.", {"defBoost": 3})
squadAceR1 = Skill("Squad Ace R 1", "Grants Res+1.", {"resBoost": 1})
squadAceR2 = Skill("Squad Ace R 2", "Grants Res+2.", {"resBoost": 2})
squadAceR3 = Skill("Squad Ace R 3", "Grants Res+3.", {"resBoost": 3})
squadAceS1 = Skill("Squad Ace S 1", "Grants Spd+1.", {"spdBoost": 1})
squadAceS2 = Skill("Squad Ace S 2", "Grants Spd+2.", {"spdBoost": 2})
squadAceS3 = Skill("Squad Ace S 3", "Grants Spd+3.", {"spdBoost": 3})
squadAceT1 = Skill("Squad Ace T 1", "Grants Atk+1.", {"atkBoost": 1})
squadAceT2 = Skill("Squad Ace T 2", "Grants Atk+2.", {"atkBoost": 2})
squadAceT3 = Skill("Squad Ace T 3", "Grants Atk+3.", {"atkBoost": 3})
squadAceU1 = Skill("Squad Ace U 1", "Grants HP+3.", {"HPBoost": 3})
squadAceU2 = Skill("Squad Ace U 2", "Grants HP+4.", {"HPBoost": 4})
squadAceU3 = Skill("Squad Ace U 3", "Grants HP+5.", {"HPBoost": 5})
squadAceV1 = Skill("Squad Ace V 1", "Grants Def+1.", {"defBoost": 1})
squadAceV2 = Skill("Squad Ace V 2", "Grants Def+2.", {"defBoost": 2})
squadAceV3 = Skill("Squad Ace V 3", "Grants Def+3.", {"defBoost": 3})
squadAceW1 = Skill("Squad Ace W 1", "Grants Res+1.", {"resBoost": 1})
squadAceW2 = Skill("Squad Ace W 2", "Grants Res+2.", {"resBoost": 2})
squadAceW3 = Skill("Squad Ace W 3", "Grants Res+3.", {"resBoost": 3})
squadAceX1 = Skill("Squad Ace X 1", "Grants Spd+1.", {"spdBoost": 1})
squadAceX2 = Skill("Squad Ace X 2", "Grants Spd+2.", {"spdBoost": 2})
squadAceX3 = Skill("Squad Ace X 3", "Grants Spd+3.", {"spdBoost": 3})
squadAceY1 = Skill("Squad Ace Y 1", "Grants Atk+1.", {"atkBoost": 1})
squadAceY2 = Skill("Squad Ace Y 2", "Grants Atk+2.", {"atkBoost": 2})
squadAceY3 = Skill("Squad Ace Y 3", "Grants Atk+3.", {"atkBoost": 3})
squadAceZ1 = Skill("Squad Ace Z 1", "Grants HP+3.", {"HPBoost": 3})
squadAceZ2 = Skill("Squad Ace Z 2", "Grants HP+4.", {"HPBoost": 4})
squadAceZ3 = Skill("Squad Ace Z 3", "Grants HP+5.", {"HPBoost": 5})
squadAceAA1 = Skill("Squad Ace AA 1", "Grants Def+1.", {"defBoost": 1})
squadAceAA2 = Skill("Squad Ace AA 2", "Grants Def+2.", {"defBoost": 2})
squadAceAA3 = Skill("Squad Ace AA 3", "Grants Def+3.", {"defBoost": 3})
squadAceAB1 = Skill("Squad Ace AB 1", "Grants Res+1.", {"resBoost": 1})
squadAceAB2 = Skill("Squad Ace AB 2", "Grants Res+2.", {"resBoost": 2})
squadAceAB3 = Skill("Squad Ace AB 3", "Grants Res+3.", {"resBoost": 3})
squadAceAC1 = Skill("Squad Ace AC 1", "Grants Spd+1.", {"spdBoost": 1})
squadAceAC2 = Skill("Squad Ace AC 2", "Grants Spd+2.", {"spdBoost": 2})
squadAceAC3 = Skill("Squad Ace AC 3", "Grants Spd+3.", {"spdBoost": 3})
squadAceAD1 = Skill("Squad Ace AD 1", "Grants Atk+1.", {"atkBoost": 1})
squadAceAD2 = Skill("Squad Ace AD 2", "Grants Atk+2.", {"atkBoost": 2})
squadAceAD3 = Skill("Squad Ace AD 3", "Grants Atk+3.", {"atkBoost": 3})

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
sorceryBlade2 = Skill("Sorcery Blade 2", "At start of combat, if unit’s HP ≥ 50% and unit is adjacent to a magic ally, calculates damage using the lower of foe’s Def or Res.", {"sorceryBlade": 1})
sorceryBlade3 = Skill("Sorcery Blade 3", "At start of combat, if unit is adjacent to a magic ally, calculates damage using the lower of foe’s Def or Res.", {"sorceryBlade": 1})

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


abel = Hero("Abel", "Abel", 0, 1, 39, 33, 32, 25, 25, "Lance", 1, pantherLance, None, aegis, hp5, swordBreaker3, None, None, None)
alfonse = Hero("Alfonse", "Alfonse", 0, 0, 43, 35, 25, 32, 22, "Sword", 0, folkvangr, None, sol, deathBlow3, None, None, None, None)
anna = Hero("Anna", "Anna", 0, 0, 41, 29, 38, 22, 28, "Axe", 0, noatun, None, astra, None, vantage3, None, None, None)
arthur = Hero("Arthur", "F!Arthur", 0, 14, 43, 32, 29, 30, 24, "Axe", 0, arthurAxe, None, None, hp5, lanceBreaker3, None, None, None)
azama = Hero("Azama", "Azama", 0, 14, 43, 21, 26, 32, 25, "Staff", 0, painPlus, None, None, None, None, None, None, None)
azura = Hero("Azura", "Azura", 0, 14, 36, 31, 33, 21, 28, "Lance", 0, sapphireLancePlus, None, None, spd3, None, None, None, None)
barst = Hero("Barst", "Barst", 0, 1, 46, 33, 32, 30, 17, "Axe", 0, devilAxe, None, bonfire, None, None, None, None, None)
bartre = Hero("Bartre", "Bartre", 0, 6, 49, 36, 25, 33, 13, "Axe", 0, axeOfVirility, None, None, fury3, None, None, None, None)
beruka = Hero("Beruka", "Beruka", 0, 14, 46, 29, 23, 37, 22, "Axe", 2, berukaAxe, None, glimmer, None, None, None, None, None)
caeda = Hero("Caeda", "Caeda", 0, 1, 36, 25, 37, 24, 34, "Sword", 2, wingSword, None, None, dartingBlow3, None, None, None, None)
cain = Hero("Cain", "Cain", 0, 1, 42, 32, 32, 27, 21, "Sword", 1, bullBlade, None, None, None, None, None, None, None)
camilla = Hero("Camilla", "Camilla", 0, 14, 37, 30, 32, 28, 31, "Axe", 2, camillaAxe, None, draconicAura, dartingBlow3, None, None, None, None)
catria = Hero("Catria", "Catria", 0, 1, 39, 31, 34, 29, 25, "Lance", 2, whitewingLance, None, moonbow, armoredBlow3, None, None, None, None)
cecilia = Hero("Cecilia", "Cecilia", 0, 6, 36, 32, 25, 22, 29, "GTome", 1, tomeOfOrder, None, None, atk3, None, None, None, None)
cherche = Hero("Cherche", "Cherche", 0, 13, 46, 38, 25, 32, 16, "Axe", 2, chercheAxe, None, None, atk3, None, None, None, None)
chrom = Hero("Chrom", "Chrom", 0, 13, 47, 37, 25, 31, 17, "Sword", 0, awkFalchion, None, aether, None, None, None, None, None)
clarine = Hero("Clarine", "Clarine", 0, 6, 35, 25, 33, 22, 29, "Staff", 1, fearPlus, None, None, res3, None, None, None, None)
cordelia = Hero("Cordelia", "Cordelia", 0, 13, 40, 35, 35, 22, 25, "Lance", 2, cordeliaLance, None, moonbow, triangleAdept3, None, None, None, None)
corrinF = Hero("Corrin", "F!Corrin", 0, 14, 41, 27, 34, 34, 21, "BDragon", 0, gloomBreath, None, None, deathBlow3, None, None, None, None)
corrinM = Hero("Corrin", "M!Corrin", 0, 14, 42, 32, 32, 28, 24, "Sword", 0, yato, None, dragonFang, def3, None, None, None, None)
donnel = Hero("Donnel", "Donnel", 0, 13, 43, 35, 29, 32, 23, "Lance", 0, hewnLance, None, None, hp5, None, None, None, None)

eliwood = Hero("Eliwood", "Eliwood", 0, 7, 39, 31, 30, 23, 32, "Sword", 1, durandal, None, sacredCowl, None, axeBreaker3, None, None, None)
hawkeye = Hero("Hawkeye", "Hawkeye", 0, 6, 45, 33, 22, 28, 30, "Axe", 0, guardianAxe, None, None, deathBlow3, None, None, None, None)
hector = Hero("Hector", "Hector", 0, 7, 52, 36, 24, 37, 19, "Axe", 3, armads, None, pavise, distanctCounter, None, goadArmor, None, None)
henry = Hero("Henry", "Henry", 0, 13, 45, 23, 22, 32, 25, "RTome", 0, corvusTome, None, ignis, None, gtomeBreaker3, None, None, None)
lilina = Hero("Lilina", "Lilina", 0, 6, 35, 37, 25, 19, 31, "RTome", 0, forblaze, None, moonbow, atk3, None, None, None, None)
lonqu = Hero("Lon'qu", "Lon'qu", 0, 13, 45, 29, 39, 22, 22, "Sword", 0, solitaryBlade, None, glimmer, spd3, vantage3, None, None, None)
marth = Hero("Marth", "Marth", 0, 1, 41, 31, 34, 29, 23, "Sword", 0, marthFalchion, None, draconicAura, fury3, quickRiposte3, None, None, None)
nino = Hero("Nino", "Nino", 0, 7, 33, 33, 36, 19, 26, "GTome", 0, irisTome, None, None, res3, None, None, None, None)
nowi = Hero("Nowi", "Nowi", 0, 13, 45, 34, 27, 30, 27, "BDragon", 0, purifyingBreath, None, None, def3, None, None, None, None)
robinM = Hero("Robin", "M!Robin", 0, 13, 40, 29, 29, 29, 22, "BTome", 0, tacticalBolt, None, bonfire, None, None, None, None, None)
roy = Hero("Roy", "Roy", 0, 6, 44, 30, 31, 25, 28, "Sword", 0, bindingBlade, None, moonbow, triangleAdept3, None, None, None, None)
serra = Hero("Serra", "Serra", 0, 7, 33, 30, 31, 21, 33, "Staff", 0, absorbPlus, None, None, None, None, None, None, None)
sharena = Hero("Sharena", "Sharena", 0, 0, 43, 32, 32, 29, 22, "Lance", 0, fensalir, None, None, spd3, None, None, None, None)
takumi = Hero("Takumi", "Takumi", 0, 14, 40, 32, 33, 25, 18, "CBow", 0, fujinYumi, None, None, closeCounter, vantage3, None, None, None)
xander = Hero("Xander", "Xander", 0, 14, 44, 32, 24, 37, 17, "Sword", 1, siegfried, None, noontime, armoredBlow3, axeBreaker3, None, None, None)

eirika = Hero("Eirika", "Eirika", 0, 8, 40, 30, 34, 27, 23, "Sword", 0, marthFalchion, None, None, None, None, None, None, None)
ephraim = Hero("Ephraim", "Ephraim", 0, 8, 45, 35, 25, 32, 20, "Lance", 0, siegmundEff, None, moonbow, deathBlow3, None, None, None, None)
seliph = Hero("Seliph", "Seliph", 0, 4, 40, 30, 30, 30, 20, "Sword", 0, marthFalchion, None, None, None, None, None, None, None)
julia = Hero("Julia", "Julia", 0, 4, 38, 35, 26, 17, 32, "GTome", 0, naga, None, dragonFang, res3, None, None, None, None)

klein = Hero("Klein", "Klein", 0, 14, 37, 32, 35, 20, 24, "CBow", 1, argentBow, None, draconicAura, deathBlow3, quickRiposte3, None, None, None)
# sanaki = Hero("Sanaki", 30, 30, 30, 20, 20, "RTome", 0, None, None, None, None, None)
# NOT YET HE'S GONNA RUIN EVERYTHING reinhardt = Hero("")
# olwen = Hero("Olwen", 35, 30, 30, 20, 15, "BTome", 1, None, None, None, None, None)
# eldigan = Hero("Eldigan", 40, 30, 25, 30, 15, "Sword", 1, None, None, None, None, None)
# lachesis = Hero("Lachesis", 30, 30, 30, 15, 20, "Staff", 0, None, None, None, None, None)

alm = Hero("Alm", "Alm", 0, 15, 45, 33, 30, 28, 22, "Sword", 0, almFalchion, None, draconicAura, atk3, windsweep3, None, None, None)

ike = Hero("Ike", "Ike", 0, 9, 42, 35, 31, 32, 18, "Sword", 1, ragnell, None, aether, heavyBlade3, swordBreaker3, None, None, None)

berkut = Hero("Berkut", "Berkut", 0, 15, 43, 34, 22, 31, 24, "Lance", 1, darkRoyalSpear, None, None, waterBoost3, None, wardCavalry, None, None)

clive = Hero("Clive", "Clive", 0, 15, 45, 33, 25, 32, 19, "Lance", 1, lordlyLance, None, escutcheon, def3, None, None, None, None)

innes = Hero("Innes", "Innes", 0, 8, 35, 33, 34, 14, 31, "CBow", 0, nidhogg, None, iceberg, fortressRes3, cancelAffinity3, None, None, None)

mia = Hero("Mia", "Mia", 0, 9, 38, 32, 40, 28, 25, "Sword", 0, resoluteBlade, None, astra, flashingBlade3, vantage3, None, None, None)

shezM = Hero("Shez", "M!Shez", 0, 16, 40, 43, 41, 37, 26, "Sword", 0, crimsonBlades, None, moonbow, deathBlow3, vantage3, None, None, None)

# print(str(len(heroes)) + " Heroes present. " + str(927-len(heroes)) + " remain to be added.")

# noah.addSpecialLines("\"I'm sorry, but you're in our way!\"",
#                     "\"For the greater good!\"",
#                     "\"The time is now!\"",
#                     "\"We will seize our destiny!\"")

# mio.addSpecialLines("\"Your fate was sealed when you rose up against us!\"",
#                    "\"For the greater good!\"",
#                    "\"Oh, we're not done yet!\"",
#                    "\"We will seize our destiny!\"")

alfonse.addSpecialLines("\"Above all...the mission!\"",
                        "\"Let me through!\"",
                        "\"My apologies.\"",
                        "\"I'll open the way!\"")

hawkeye.addSpecialLines("\"WUU-OOHHH!\"",
                        "\"FIGHT!\"",
                        "\"I know NOTHING of fear!\"",
                        "\"I'm coming for YOU.\"")

clive.addSpecialLines("\"No hard feelings.\"",
                      "\"In the name of Zofia!\"",
                      "\"Make your peace!\"",
                      "\"Farewell!\"")

nino.addSpecialLines("\"Ahhhhhhh!\"",
                     "\"I won't lose! Not me!\"",
                     "\"I can do this!\"",
                     "\"I'll do my best!\"")

roy.addSpecialLines("\"I will win!\"",
                    "\"There's my opening!\"",
                    "\"By my blade!\"",
                    "\"I won't lose. I won't!\"")

takumi.addSpecialLines("\"Oh, that's it!\"",
                       "\"Die already!\"",
                       "\"I'll shoot you down!\"",
                       "\"You'll never hit this target!\"")

corrinF.addSpecialLines("\"We won't give up!\"",
                        "\"I've made my choice!\"",
                        "\"I won't surrender!\"",
                        "\"My path is certain!\"")

cordelia.addSpecialLines("\"I can do this...\"",
                         "\"Now you've angered me!\"",
                         "\"I must prevail.\"",
                         "\"I see an opening!\"")

hector.addSpecialLines("\"I don't back down!\"",
                       "\"Gutsy, aren't you?\"",
                       "\"Enough chitchat!\"",
                       "\"Here we go!\"")

ephraim.addSpecialLines("\"Coming through!\"",
                        "\"Wonderful!\"",
                        "\"Give me more—more!\"",
                        "\"All right. Let's fight!\"")

anna.addSpecialLines("\"This one's on the house!\"",
                     "\"More than you bargained for?\"",
                     "\"We will triumph!\"",
                     "\"Onward to victory!\"")

klein.addSpecialLines("\"I won't miss.\"",
                      "\"Such foolishness.\"",
                      "\"At this range...\"",
                      "\"Now, my turn.\"")

lonqu.addSpecialLines("\"No hard feelings.\"",
                      "\"Be silent!\"",
                      "\"You're no challenge.\"",
                      "\"Give up.\"")

mia.addSpecialLines("\"Today is a good day!\"",
                    "\"You're on!\"",
                    "\"Take that, foe!\"",
                    "\"Clash with me!\"")

xander.addSpecialLines("\"Right where I want you!\"",
                       "\"Prepare yourself!\"",
                       "\"Down on your knees!\"",
                       "\"You're going home—in pieces!\"")

catria.addSpecialLines("\"Here I go!\"",
                       "\"Finishing Blow!\"",
                       "\"This ought to do it!\"",
                       "\"No matter the cost!\"")

beruka.addSpecialLines("\"Time to play!\"",
                       "\"Finishing the mission.\"",
                       "\"This is over!\"",
                       "\"I will exterminate you!\"")

eliwood.addSpecialLines("\"Off with you, fiend!\"",
                        "\"This should do it!\"",
                        "\"Now, take this!\"",
                        "\"Watch me work!\"")

abel.addSpecialLines("\"Make your peace.\"",
                     "\"Back with you!\"",
                     "\"No mercy!\"",
                     "\"You've underestimated me.\"")

ike.addSpecialLines("\"I won't let anyone die!\"",
                    "\"Run while you can!\"",
                    "\"I will finish you!\"",
                    "\"Out of my way!\"")

# playerUnits = [marth, robinM, takumi, ephraim]
# enemyUnits = [nowi, alm, hector, bartre]

alpha = barst
omega = xander
omega.inflictDamage(12)

# alpha.inflict(Status.Panic)
# alpha.inflictStat(1,+7)
# alpha.inflictStat(3,-7)
#alpha.chargeSpecial(1)

badaboom = simulate_combat(alpha,omega,False)
print(badaboom)

# APPLY THE EFFECTS ON THE UNITS BEING AFFECTED AND NOT THE UNIT CAUSING THE EFFECT ON THE MAP
# IF MARTH IS FIGHTING EPHRAIM WITH THREATEN DEF 3, GIVE MARTH (IF UNIT IS WITHIN 2 SPACES WITHIN
# EPHRAIM, GIVE -7 DEF. I AM A GENIUS.

class HeroDirectory:
    def __init__(self):
        self.heroes = [abel, alfonse, anna, arthur, azama, azura, barst, bartre, beruka, caeda,
                       cain, camilla, catria, cherche, chrom, clarine, cordelia, corrinM, corrinF,
                       eliwood, hawkeye, hector, henry, lilina, lonqu, nino, nowi, robinM, roy, takumi,
                       xander,

                       ephraim, julia,
                       klein,
                       alm,
                       ike,
                       clive,
                       berkut,
                       innes,
                       mia]

    def getHeroes(self):
        return self.heroes


results = []
# for hero in HeroDirectory().getHeroes():
#    for hero2 in HeroDirectory().getHeroes():
#        results.append(simulate_combat(hero,hero2,False))
#        print(results[len(results)-1], "<---------------------------------------")
# print(results)

# ATK AND WEAPON SKILLS DO STACK W/ HOW PYTHON MERGES DICTIONARIES
# JUST KEEP IN MIND ONCE YOU GET TO THAT BRIDGE WITH SKILLS NOT MEANT TO STACK
