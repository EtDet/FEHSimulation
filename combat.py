import math
import random

def startOfTurn(attackers,defenders):
    return 7

def simulate_combat(attacker,defender):
    atkSkills = attacker.getSkills()
    atkStats = attacker.getStats()
    defSkills = defender.getSkills()
    defStats = defender.getStats()


    atkStats[1] += attacker.getWeapon().getMT()
    defStats[1] += defender.getWeapon().getMT()



    triAdept = -1
    atkCA = 0
    defCA = 0
    ignoreRng = False
    cannotCounter = False
    doWindsweepCheck = False
    doWatersweepCheck = False

    AColorlessEff = False
    DColorlessEff = False

    braveATKR = False
    braveDEFR = False

    colorlessAdvAtk = False
    colorlessAdvDef = False

    cavEffA = False
    cavEffD = False
    flyEffA = False
    flyEffD = False
    armEffA = False
    armEffD = False
    drgEffA = False
    drgEffD = False

    atkFollowUps = 0
    defFollowUps = 0

    # for if range = 2 lower def/res dragonstones
    dragonCheckA = False
    dragonCheckD = False

    atkSpecialCounter = attacker.getCooldown()
    defSpecialCounter = defender.getCooldown()
    permASC = atkSpecialCounter
    permDSC = defSpecialCounter

    atkSCCB = 0 # special cooldown charge boost (heavy blade, flashing blade, etc.)
    defSCCB = 0
    atkDoHeavyBladeCheck = False
    defDoHeavyBladeCheck = False
    atkDoFlashingBladeCheck = False
    defDoFlashingBladeCheck = False

    atkFixedSpDmgBoost = 0
    defFixedSpDmgBoost = 0

    atkDoSelfDmgCheck = False
    defDoSelfDmgCheck = False
    atkDoOtherDmgCheck = False
    defDoOtherDmgCheck = False
    atkSelfDmg = 0
    defSelfDmg = 0
    atkOtherDmg = 0
    defOtherDmg = 0

    atkAbsorb = False
    defAbsorb = False

    ASpDefReduce = 0
    ASpDmgIncrease = 0
    ASpDmgTargetedStat = -1 #0-HP,1-ATK,2-SPD,3-DEF,4-RES,5-FOERES,6-FOEATK
    ASpDmgPlus = 0
    ASpShield = 0
    ASpHeal = 0
    ASpIDR = 0 # ignore damage reduction
    ASpRetaliateB = 0 # negating fang, godlike reflexes, etc.
    AspRetaliateV = 0 # ice mirror 1, fjorm moment
    ASpecialType = ""

    atkSpEffects = {}


    for key in atkSkills:
        if key == "HPBoost":  atkStats[0] += atkSkills["HPBoost"]
        if key == "atkBoost": atkStats[1] += atkSkills["atkBoost"]
        if key == "spdBoost": atkStats[2] += atkSkills["spdBoost"]
        if key == "defBoost": atkStats[3] += atkSkills["defBoost"]
        if key == "resBoost": atkStats[4] += atkSkills["resBoost"]

        if key == "atkBlow": atkStats[1] += atkSkills["atkBlow"] * 2
        if key == "spdBlow": atkStats[2] += atkSkills["spdBlow"] * 2
        if key == "defBlow": atkStats[3] += atkSkills["defBlow"] * 2
        if key == "resBlow": atkStats[4] += atkSkills["resBlow"] * 2

        if key == "waterBoost":
            if atkStats[0] >= defStats[0] + 3:
                atkStats[4] += atkSkills["waterBoost"] * 2

        if key == "heavyBlade":
            atkDoHeavyBladeCheck = True
        if key == "flashingBlade":
            atkDoFlashingBladeCheck = True
        if key == "selfDmg":
            atkSelfDmg += atkSkills[key]
        if key == "atkOnlySelfDmg":
            atkDoSelfDmgCheck = True
        if key == "atkOnlyOtherDmg":
            atkDoOtherDmgCheck = True


        if key == "slaying":
            atkSpecialCounter -= atkSkills["slaying"]
            permASC -= atkSkills["slaying"]
        if key == "colorlessAdv": colorlessAdvAtk = True
        if key == "spDmgAdd":
            atkFixedSpDmgBoost += atkSkills[key]

        if key == "dragonCheck":
            dragonCheckA = True

        if key == "triAdeptS" or key == "triAdeptW":
            if atkSkills[key] > triAdept:
                triAdept = atkSkills[key]

        if key == "owlBoost":
            numAlliesNearby = 0
            atkStats[1] += 2 * numAlliesNearby
            atkStats[2] += 2 * numAlliesNearby
            atkStats[3] += 2 * numAlliesNearby
            atkStats[4] += 2 * numAlliesNearby
        if key == "FollowUpEph":
            if atkStats[0]/atkStats[0] > .90:
                atkFollowUps += 1
        if key == "berkutBoost":
            if defStats[0] == defStats[0]:
                atkStats[1] += 5
                atkStats[3] += 5
                atkStats[4] += 5


        if key == "BraveAW" or key == "BraveAS" or key == "BraveBW":
            braveATKR = True

        if key == "effCav":
            cavEffA = True
        if key == "effFly":
            flyEffA = True
        if key == "effArm":
            armEffA = True
        if key == "effDragon":
            drgEffA = True

        if key == "absorb":
            atkAbsorb = True

        if key == "swordBreak" and defender.getWeaponType() == "Sword":
            atkFollowUps += 1
            defFollowUps -= 1
        if key == "lanceBreak" and defender.getWeaponType() == "Lance":
            atkFollowUps += 1
            defFollowUps -= 1
        if key == "axeBreak" and defender.getWeaponType() == "Axe":
            atkFollowUps += 1
            defFollowUps -= 1
        if key == "gtomeBreak" and defender.getWeaponType() == "GTome":
            atkFollowUps += 1
            defFollowUps -= 1
        if key == "windsweep":
            doWindsweepCheck = True
            atkFollowUps -= 1
        if key == "cancelTA":
            atkCA = atkSkills[key]


        if key == "healSelf":
            ASpecialType = "Offense"
            atkSpEffects.update({"healSelf":atkSkills[key]})
        if key == "defReduce":
            ASpecialType = "Offense"
            ASpDefReduce = atkSkills[key]
            atkSpEffects.update({"defReduce":atkSkills[key]})
        if key == "dmgBoost":
            ASpecialType = "Offense"
            atkSpEffects.update({"dmgBoost": atkSkills[key]})
        if key == "atkBoostSp":
            ASpecialType = "Offense"
            atkSpEffects.update({"atkBoost": atkSkills[key]})
        if key == "defBoostSp":
            ASpecialType = "Offense"
            atkSpEffects.update({"defBoost": atkSkills[key]})
        if key == "resBoostSp":
            ASpecialType = "Offense"
            atkSpEffects.update({"resBoost": atkSkills[key]})
        if key == "closeShield":
            ASpecialType = "Defense"
            atkSpEffects.update({"closeShield":atkSkills[key]})

    DSpecialType = ""
    DSpDefReduce = 0
    DSpDmgIncrease = 0
    DSpDmgTargetedStat = -1  # 0-HP,1-ATK,2-SPD,3-DEF,4-RES,5-FOERES,6-FOEATK
    DSpDmgPlus = 0
    DSpShield = 0
    DSpHeal = 0
    DSpIDR = 0  # ignore damage reduction
    DSpRetaliateB = 0  # strikes back with boosted stat amount (negating fang, godlike reflexes, etc.)
    DSpRetaliateV = 0  # strikes back with health boosted amount (ice mirror)
    vantageEnabled = False

    defSpEffects = {}

    for key in defSkills:
        if key == "HPBoost":  defStats[0] += defSkills["HPBoost"]
        if key == "atkBoost": defStats[1] += defSkills["atkBoost"]
        if key == "spdBoost": defStats[2] += defSkills["spdBoost"]
        if key == "defBoost": defStats[3] += defSkills["defBoost"]
        if key == "resBoost": defStats[4] += defSkills["resBoost"]

        if key == "atkStance": defStats[1] += defSkills["atkStance"] * 2
        if key == "spdStance": defStats[2] += defSkills["spdStance"] * 2
        if key == "defStance": defStats[3] += defSkills["defStance"] * 2
        if key == "resStance": defStats[4] += defSkills["resStance"] * 2

        if key == "waterBoost":
            if defStats[0] >= atkStats[0] + 3:
                defStats[4] += defSkills["waterBoost"] * 2

        if key == "heavyBlade":
            defDoHeavyBladeCheck = True
        if key == "flashingBlade":
            defDoFlashingBladeCheck = True

        if key == "slaying":
            defSpecialCounter -= 1
            permDSC -= 1
        if key == "colorlessAdv": colorlessAdvDef = True
        if key == "spDmgAdd":
            defFixedSpDmgBoost += defSkills[key]
        if key == "dragonCheck":
            dragonCheckD = True

        if key == "triAdeptS" or key == "triAdeptW":
            if defSkills[key] > triAdept:
                triAdept = defSkills[key]
        if key == "cCounter" or key == "dCounter":
            ignoreRng = True
        if key == "berkutBoost":
            defStats[1] += 5
            defStats[3] += 5
            defStats[4] += 5
        if key == "BraveDW" or key == "BraveBW":
            braveDEFR = True

        if key == "effCav":
            cavEffD = True
        if key == "effFly":
            flyEffD = True
        if key == "effArm":
            armEffD = True
        if key == "effDragon":
            drgEffD = True
        if key == "absorb":
            defAbsorb = True
        if key == "atkOnlySelfDmg":
            defDoSelfDmgCheck = True
        if key == "atkOnlyOtherDmg":
            defDoOtherDmgCheck = True
        if key == "selfDmg":
            defSelfDmg += defSkills[key]

        if key == "QRW" or key == "QRS":
            defFollowUps += 1

        if key == "swordBreak" and attacker.getWeaponType() == "Sword":
            atkFollowUps -= 1
            defFollowUps += 1
        if key == "lanceBreak" and attacker.getWeaponType() == "Lance":
            atkFollowUps -= 1
            defFollowUps += 1
        if key == "axeBreak" and attacker.getWeaponType() == "Axe":
            atkFollowUps -= 1
            defFollowUps += 1
        if key == "gtomeBreak" and attacker.getWeaponType() == "GTome":
            atkFollowUps -= 1
            defFollowUps += 1
        if key == "vantage":
            if defStats[0]/defStats[0] >= 0.75 - (0.25 * (3-defSkills["vantage"])):
                vantageEnabled = True
        if key == "cancelTA":
            defCA = defSkills[key]

        if key == "healSelf":
            DSpecialType = "Offense"
            defSpEffects.update({"healSelf":defSkills[key]})
        if key == "defReduce":
            DSpecialType = "Offense"
            DSpDefReduce = defSkills[key]
            defSpEffects.update({"defReduce":defSkills[key]})
        if key == "dmgBoost":
            DSpecialType = "Offense"
            defSpEffects.update({"dmgBoost": defSkills[key]})
        if key == "closeShield":
            DSpecialType = "Defense"
            defSpEffects.update({"closeShield":defSkills[key]})
        if key == "resBoostSp":
            DSpecialType = "Offense"
            defSpEffects.update({"resBoost": defSkills[key]})

    # just used for draconic aura/dragon fang/etc. specials
    atkTempAtk = atkStats[1]
    defTempAtk = defStats[1]

    # HEAVY BLADE CHECK

    if atkDoHeavyBladeCheck and atkStats[1] > defStats[1] + (-2 * atkSkills["heavyBlade"] + 7):
        atkSCCB += 1

    if defDoHeavyBladeCheck and defStats[1] > atkStats[1] + (-2 * defSkills["heavyBlade"] + 7):
        defSCCB += 1

    if atkDoFlashingBladeCheck and atkStats[2] > defStats[2] + (-2 * atkSkills["flashingBlade"] + 7):
        atkSCCB += 1

    if defDoFlashingBladeCheck and defStats[2] > atkStats[2] + (-2 * defSkills["flashingBlade"] + 7):
        atkSCCB += 1

    if atkSCCB > 1: atkSCCB = 1
    if defSCCB > 1: defSCCB = 1

    # WINDSWEEP CHECK

    if doWindsweepCheck and atkStats[2] > defStats[2] + (-2 * atkSkills["windsweep"] + 7) and defender.getTargetedDef() == -1:
        cannotCounter = True

    # EFFECTIVENESS CHECK

    if cavEffA and defender.getMovement() == 1:
        atkStats[1] += math.trunc(atkStats[1] * 0.5)
    if cavEffD and attacker.getMovement() == 1:
        defStats[1] += math.trunc(defStats[1] * 0.5)

    if flyEffA and defender.getMovement() == 2:
        atkStats[1] += math.trunc(atkStats[1] * 0.5)
    if flyEffD and attacker.getMovement() == 2:
        defStats[1] += math.trunc(defStats[1] * 0.5)

    if armEffA and defender.getMovement() == 3:
        atkStats[1] += math.trunc(atkStats[1] * 0.5)
    if armEffD and attacker.getMovement() == 3:
        defStats[1] += math.trunc(defStats[1] * 0.5)

    if drgEffA and defender.getTargetedDef() == 0:
        atkStats[1] += math.trunc(atkStats[1] * 0.5)
    if drgEffD and attacker.getTargetedDef() == 0:
        defStats[1] += math.trunc(defStats[1] * 0.5)

    # COLOR ADVANTAGE CHECK

    if (attacker.getColor() == "Red" and defender.getColor() == "Green") or \
            (attacker.getColor() == "Green" and defender.getColor() == "Blue") or \
            (attacker.getColor() == "Blue" and defender.getColor() == "Red") or \
            (defender.getColor() == "Colorless" and colorlessAdvAtk):

        if (atkCA == 1 or defCA == 1) and triAdept != -1: triAdept = -1
        if defCA == 2 and triAdept != -1: triAdept = -1
        if atkCA == 3 and triAdept != -1: triAdept = -5
        atkStats[1] += math.trunc(atkStats[1] * (0.25 + .05 * triAdept))
        defStats[1] -= math.trunc(defStats[1] * (0.25 + .05 * triAdept))

    if (attacker.getColor() == "Blue" and defender.getColor() == "Green") or \
            (attacker.getColor() == "Red" and defender.getColor() == "Blue") or \
            (attacker.getColor() == "Green" and defender.getColor() == "Red") or \
            (attacker.getColor() == "Colorless" and colorlessAdvDef):

        if (atkCA == 1 or defCA == 1) and triAdept != -1: triAdept = -1
        if atkCA == 2 and triAdept != -1: triAdept = -1
        if atkCA == 3 and triAdept != -1: triAdept = -5
        atkStats[1] -= math.trunc(atkStats[1] * (0.25 + .05 * triAdept))
        defStats[1] += math.trunc(defStats[1] * (0.25 + .05 * triAdept))



    r = 0 #isResTargeted by atkr
    x = 0 #isResTargeted by defr
    if attacker.getTargetedDef() == 1:
        r += 1
    if attacker.getTargetedDef() == 0 and dragonCheckA:
        if defender.getRange() == 2:
            if defStats[3] > defStats[4]:
                r += 1
            else:
                r += 0
        else:
            r += 1

    if defender.getTargetedDef() == 1:
        x += 1
    if defender.getTargetedDef() == 0 and dragonCheckD:
        if attacker.getRange() == 2:
            if atkStats[3] > atkStats[4]:
                x += 1
            else:
                x += 0
        else:
            x += 1

    print(atkStats)
    print(defStats)

    # additional follow-up granted by outspeeding
    if(atkStats[2] > defStats[2] + 4):
        atkFollowUps += 1

    if (atkStats[2] + 4 < defStats[2]):
        defFollowUps += 1

    atkAlive = True
    defAlive = True

    #define in method?
    atkSpecialTriggered = False
    defSpecialTriggered = False

    # START OF COMBAT
    ###################################################################################################################

    # first attack by attacker

    atkInitStats = atkStats[:]
    defInitStats = defStats[:]



    if atkDoSelfDmgCheck == True: atkSelfDmg += atkSkills["atkOnlySelfDmg"]
    if atkDoOtherDmgCheck == True: atkOtherDmg += atkSkills["atkOnlyOtherDmg"]

    # if attacker can attack *always true, initiator always attacks in combat at least once
    # under the assumption that they survive any hits given by the defender*

    # attacker - unit attacking
    # defender - unit defending
    # atkStats[] - stats of attacker
    # defStats[]
    # atkInitStats[] - base stats of attacker (base hp, stats before bonfire boost (wait do we need to modify that?))
    # defInitStats[]
    # atkSpecialCounter - current special cooldown (pointer perhaps?)
    # defSpecialCounter
    # permASC - permanent special counter
    # permDSC
    # ASpecialType - Attacker, Defender, AOE, Staff, Other Weird Gimmicky Thing
    # DSpecialType
    # atkSpecialEffects - List of effects (dmgBoost, resBoost, selfHeal)
    # defSpecialEffects
    # atkSCCB - (Heavy Blade, Guard, etc. effects)
    # defSCCB
    # atkFixedSpDmgBoost (wo dao, etc.)
    # defFixedSpDmgBoost
    # atkAbsorb (absorb staff skill)
    # defAbsorb
    # braveATKR (brave weapons)
    # braveDEFR

    if atkSpecialCounter == 0 and ASpecialType == "Offense":
        print(attacker.getName() + " procs " + attacker.getSpName() + ".")  # attack name
        print(attacker.getSpecialLine())
        for key in atkSpEffects:
            if key == "defReduce":
                atkSpecialTriggered = True
                defStats[3] -= math.trunc(defStats[3] * .10 * atkSpEffects["defReduce"])
                defStats[4] -= math.trunc(defStats[4] * .10 * atkSpEffects["defReduce"])

    atkrATK1 = atkStats[1] - defStats[3+r]
    if atkrATK1 < 0: atkrATK1 = 0
    if attacker.getWeaponType() == "Staff": atkrATK1 = math.trunc(atkrATK1 * 0.5)


    defStats[0] = defStats[0] - atkrATK1
    print(attacker.getName() + " attacks " + defender.getName() + " for " + str(atkrATK1) + " damage.")

    if atkSpecialCounter > 0: atkSpecialCounter -= (1 + atkSCCB)
    if defSpecialCounter > 0: defSpecialCounter -= 1
    if atkSpecialCounter < 0: atkSpecialCounter = 0
    if defSpecialCounter < 0: defSpecialCounter = 0
    if atkSpecialTriggered: atkSpecialCounter = permASC
    atkSpecialTriggered = False

    newHPA = atkStats[0]
    newHPD = defStats[0]

    atkStats = atkInitStats[:]
    defStats = defInitStats[:]

    atkStats[0] = newHPA
    defStats[0] = newHPD

    if atkAbsorb and atkStats[0] < atkInitStats[0]:
        amountHealed = math.trunc(atkrATK1 * 0.5)
        atkStats[0] += amountHealed
        print(attacker.getName() + " absorbs " + str(amountHealed) + " HP.")
        if atkStats[0] > atkInitStats[0]: atkStats[0] = atkInitStats[0]

    if defStats[0] <= 0:
        defStats[0] = 0
        defAlive = False
        print(defender.getName() + " falls.")

    if braveATKR and defAlive:
        braveATK1 = atkStats[1] - defStats[3+r]
        if braveATK1 < 0: braveATK1 = 0
        defStats[0] = defStats[0] - braveATK1
        print(attacker.getName() + " attacks " + defender.getName() + " for " + str(braveATK1) + " damage.")
        if atkSpecialCounter > 0: atkSpecialCounter -= (1 + + atkSCCB)
        if defSpecialCounter > 0: defSpecialCounter -= 1
        if atkSpecialCounter < 0: atkSpecialCounter = 0
        if defSpecialCounter < 0: defSpecialCounter = 0
        if atkSpecialTriggered: atkSpecialCounter = permASC
        if defSpecialTriggered: defSpecialCounter = permDSC

        if defStats[0] <= 0:
            defStats[0] = 0
            defAlive = False
            print(defender.getName() + " falls.")


    # first counterattack by defender

    if (attacker.getRange() == defender.getRange() or ignoreRng) and defAlive and not cannotCounter:

        if defDoSelfDmgCheck == True: defSelfDmg += defSkills["atkOnlySelfDmg"]
        if defDoOtherDmgCheck == True: defOtherDmg += defSkills["atkOnlyOtherDmg"]

        dmgBoost = 0
        extraDmg = 0
        if defSpecialCounter == 0 and DSpecialType == "Offense":
            print(defender.getName() + " procs " + defender.getSpName() + ".")  # attack name
            print(defender.getSpecialLine())
            for key in defSpEffects:
                if key == "defReduce":
                    defSpecialTriggered = True
                    atkStats[3] -= math.trunc(atkStats[3] * .10 * defSpEffects["defReduce"])
                    atkStats[4] -= math.trunc(atkStats[4] * .10 * defSpEffects["defReduce"])
                if key == "dmgBoost":
                    defSpecialTriggered = True
                    dmgBoost = defSpEffects["dmgBoost"] * 0.1
                if key == "resBoost":
                    defSpecialTriggered = True
                    extraDmg = math.trunc(defStats[4] * 0.1 * defSpEffects["resBoost"])
                #if key == "heal":

        defrATK1 = defStats[1] - atkStats[3+x] + extraDmg
        if defrATK1 < 0: defrATK1 = 0
        defrATK1 += math.trunc(defrATK1 * dmgBoost)
        if defender.getWeaponType() == "Staff": defrATK1 = math.trunc(defrATK1 * 0.5)


        atkStats[0] = atkStats[0] - defrATK1
        print(defender.getName() + " attacks " + attacker.getName() + " for " + str(defrATK1) + " damage.")

        if atkSpecialCounter > 0: atkSpecialCounter -= 1
        if defSpecialCounter > 0: defSpecialCounter -= (1 + defSCCB)
        if atkSpecialCounter < 0: atkSpecialCounter = 0
        if defSpecialCounter < 0: defSpecialCounter = 0
        if atkSpecialTriggered: atkSpecialCounter = permASC
        if defSpecialTriggered: defSpecialCounter = permDSC
        defSpecialTriggered = False

        newHPA = atkStats[0]
        newHPD = defStats[0]

        atkStats = atkInitStats[:]
        defStats = defInitStats[:]

        atkStats[0] = newHPA
        defStats[0] = newHPD

        print(atkStats)

        if defAbsorb:
            amountHealed = math.trunc(defrATK1 * 0.5)
            defStats[0] += amountHealed
            print(defender.getName() + " absorbs " + str(amountHealed) + " HP.")
            if defStats[0] > defInitStats[0]: defStats[0] = defInitStats[0]

        if atkStats[0] <= 0:
            atkStats[0] = 0
            atkAlive = False
            print(attacker.getName() + " falls.")

        if braveDEFR and atkAlive:
            braveDEF1 = defStats[1] - atkStats[3+x]
            if braveDEF1 < 0: braveDEF1 = 0
            atkStats[0] = atkStats[0] - braveDEF1
            print(defender.getName() + " attacks " + attacker.getName() + " for " + str(braveDEF1) + " damage.")
            if atkSpecialCounter > 0: atkSpecialCounter -= 1
            if defSpecialCounter > 0: defSpecialCounter -= (1 + defSCCB)
            if atkStats[0] <= 0:
                atkStats[0] = 0
                atkAlive = False
                print(attacker.getName() + " falls.")

    # second attack by attacker


    if atkFollowUps > 0 and atkAlive and defAlive:
        dmgBoost = 0
        extraDmg = 0
        selfHeal = False

        #OFFENSIVE SPECIAL CHECK BY ATTACKER
        if atkSpecialCounter == 0 and ASpecialType == "Offense":
            print(attacker.getName() + " procs " + attacker.getSpName() + ".")  # attack name
            print(attacker.getSpecialLine())
            for key in atkSpEffects:
                if key == "healSelf":
                    atkSpecialTriggered = True
                    selfHeal = True
                if key == "defReduce":
                    atkSpecialTriggered = True
                    defStats[3] -= math.trunc(defStats[3] * .10 * atkSpEffects["defReduce"])
                    defStats[4] -= math.trunc(defStats[4] * .10 * atkSpEffects["defReduce"])
                if key == "dmgBoost":
                    atkSpecialTriggered = True
                    dmgBoost = atkSpEffects["dmgBoost"] * 0.1
                if key == "atkBoost":
                    atkSpecialTriggered = True
                    extraDmg = math.trunc(atkTempAtk * 0.1 * atkSpEffects["atkBoost"])
                    # needs to use atk before weapon triangle
                if key == "defBoost":
                    atkSpecialTriggered = True
                    extraDmg = math.trunc(atkStats[3] * 0.1 * atkSpEffects["defBoost"])
                if key == "resBoost":
                    atkSpecialTriggered = True
                    extraDmg = math.trunc(atkStats[4] * 0.1 * atkSpEffects["resBoost"])

        atkrATK2 = (atkStats[1] - defStats[3+r]) + extraDmg
        if atkrATK2 < 0: atkrATK2 = 0

        atkrATK2 += math.trunc(atkrATK2 * dmgBoost)

        if atkSpecialTriggered: atkrATK2 += atkFixedSpDmgBoost

        if attacker.getWeaponType() == "Staff": atkrATK2 = math.trunc(atkrATK2 * 0.5)


        #DEFENSIVE SPECIAL CHECK BY DEFENDER
        if defSpecialCounter == 0 and DSpecialType == "Defense" and attacker.getRange() == 1:
            print(defender.getName() + " procs " + defender.getSpName() + ".")
            print(defender.getSpecialLine())
            for key in defSpEffects:
                if key == "closeShield":
                    defSpecialTriggered = True
                    atkrATK2 -= math.trunc(atkrATK2 * 0.10 * defSpEffects["closeShield"])



        defStats[0] = defStats[0] - atkrATK2

        print(attacker.getName() + " attacks " + defender.getName() + " for " + str(atkrATK2) + " damage.")
        if atkSpecialCounter > 0: atkSpecialCounter -= (1 + atkSCCB)
        if defSpecialCounter > 0: defSpecialCounter -= 1
        if atkSpecialCounter < 0: atkSpecialCounter = 0
        if defSpecialCounter < 0: defSpecialCounter = 0
        if atkSpecialTriggered: atkSpecialCounter = permASC
        if defSpecialTriggered: defSpecialCounter = permDSC


        atkSpecialTriggered = False
        defSpecialTriggered = False

        newHPA = atkStats[0]
        newHPD = defStats[0]

        atkStats = atkInitStats[:]
        defStats = defInitStats[:]

        atkStats[0] = newHPA
        defStats[0] = newHPD

        if (atkAbsorb or selfHeal) and atkStats[0] < atkInitStats[0]:
            # need to consider case where special defeats foe, init hp-dmg is used
            if atkAbsorb: amountHealed = math.trunc(atkrATK2 * 0.5)
            if selfHeal: amountHealed = math.trunc(atkrATK2 * 0.1 * atkSpEffects["healSelf"])
            atkStats[0] += amountHealed
            if atkAbsorb: print(attacker.getName() + " absorbs " + str(amountHealed) + " HP.")
            if selfHeal: print(attacker.getName() + " restores " + str(amountHealed) + " HP.")
            if atkStats[0] > atkInitStats[0]: atkStats[0] = atkInitStats[0]

        selfHeal = False

        if defStats[0] <= 0:
            defStats[0] = 0
            defAlive = False
            print(defender.getName() + " falls.")

        if braveATKR and defAlive:
            if atkSpecialCounter == 0 and ASpecialType == "Offense":
                print(attacker.getName() + " procs " + attacker.getSpName() + ".")  # attack name
                print(attacker.getSpecialLine())
                for key in atkSpEffects:
                    if key == "defReduce":
                        atkSpecialTriggered = True
                        defStats[3] -= math.trunc(defStats[3] * .10 * atkSpEffects["defReduce"])
                        defStats[4] -= math.trunc(defStats[4] * .10 * atkSpEffects["defReduce"])
                    if key == "resBoost":
                        atkSpecialTriggered = True
                        extraDmg = math.trunc(atkStats[4] * 0.1 * atkSpEffects["resBoost"])


            braveATK2 = atkStats[1] - defStats[3 + r] + extraDmg
            if braveATK2 < 0: atkrATK2 = 0

            #DEFENSIVE SPECIAL CHECK BY DEFENDER
            if defSpecialCounter == 0 and DSpecialType == "Defense" and attacker.getRange() == 1:
                print(defender.getName() + " procs " + defender.getSpName() + ".")
                print(defender.getSpecialLine())
                for key in defSpEffects:
                    if key == "closeShield":
                        defSpecialTriggered = True
                        braveATK2 -= math.trunc(atkrATK2 * 0.10 * defSpEffects["closeShield"])

            defStats[0] = defStats[0] - braveATK2

            print(attacker.getName() + " attacks " + defender.getName() + " for " + str(braveATK2) + " damage.")

            if atkSpecialCounter > 0: atkSpecialCounter -= (1 + atkSCCB)
            if defSpecialCounter > 0: defSpecialCounter -= 1
            if atkSpecialCounter < 0: atkSpecialCounter = 0
            if defSpecialCounter < 0: defSpecialCounter = 0
            if atkSpecialTriggered: atkSpecialCounter = permASC
            if defSpecialTriggered: defSpecialCounter = permDSC

            atkSpecialTriggered = False
            defSpecialTriggered = False

            newHPA = atkStats[0]
            newHPD = defStats[0]

            atkStats = atkInitStats[:]
            defStats = defInitStats[:]

            atkStats[0] = newHPA
            defStats[0] = newHPD

            if defStats[0] <= 0:
                defStats[0] = 0
                defAlive = False
                print(defender.getName() + " falls.")

    # second counterattack by defender


    if (defFollowUps > 0 and (attacker.getRange() == defender.getRange() or ignoreRng)) and atkAlive and defAlive and not cannotCounter:
        dmgBoost = 0 # used for night sky, glimmer, astra, and deadeye
        if defSpecialCounter == 0 and DSpecialType == "Offense":
            print(defender.getName() + " procs " + defender.getSpName() + ".")  # attack name
            print(defender.getSpecialLine())
            for key in defSpEffects:
                if key == "defReduce":
                    defSpecialTriggered = True
                    atkStats[3] -= math.trunc(atkStats[3] * .10 * defSpEffects["defReduce"])
                    atkStats[4] -= math.trunc(atkStats[4] * .10 * defSpEffects["defReduce"])
                if key == "dmgBoost":
                    defSpecialTriggered = True
                    dmgBoost = 0.10 * defSpEffects["dmgBoost"]

        defrATK2 = defStats[1] - atkStats[3+x]
        if defrATK2 < 0: defrATK2 = 0

        defrATK2 += math.trunc(defrATK2 * dmgBoost)

        if atkSpecialCounter == 0 and ASpecialType == "Defense" and attacker.getRange() == 1:
            print(attacker.getName() + " procs " + attacker.getSpName() + ".")
            print(attacker.getSpecialLine())
            for key in atkSpEffects:
                if key == "closeShield":
                    atkSpecialTriggered = True
                    defrATK2 -= math.trunc(defrATK2 * 0.10 * atkSpEffects["closeShield"])

        atkStats[0] = atkStats[0] - defrATK2

        print(defender.getName() + " attacks " + attacker.getName() + " for " + str(defrATK2) + " damage.")

        if atkSpecialCounter > 0: atkSpecialCounter -= 1
        if defSpecialCounter > 0: defSpecialCounter -= 1
        if atkSpecialTriggered: atkSpecialCounter = permASC
        if defSpecialTriggered: defSpecialCounter = permDSC

        atkSpecialTriggered = True
        defSpecialTriggered = False

        newHPA = atkStats[0]
        newHPD = defStats[0]

        atkStats = atkInitStats
        defStats = defInitStats

        atkStats[0] = newHPA
        defStats[0] = newHPD

        if defAbsorb:
            amountHealed = math.trunc(defrATK1 * 0.5)
            defStats[0] += amountHealed
            print(defender.getName() + " absorbs " + str(amountHealed) + " HP.")
            if defStats[0] > defInitStats[0]: defStats[0] = defInitStats[0]

        if atkStats[0] <= 0:
            atkStats[0] = 0
            atkAlive = False
            print(attacker.getName() + " falls.")

        if braveDEFR and atkAlive:
            braveDEF2 = defStats[1] - atkStats[3+x]
            if braveDEF2 < 0: braveDEF2 = 0
            atkStats[0] = atkStats[0] - braveDEF2
            print(defender.getName() + " attacks " + attacker.getName() + " for " + str(braveDEF2) + " damage.")
            if atkStats[0] <= 0:
                atkStats[0] = 0
                atkAlive = False
                print(attacker.getName() + " falls.")

    if atkAlive and atkSelfDmg != 0 or defOtherDmg != 0:
        atkStats[0] -= (atkSelfDmg + defOtherDmg)
        print(attacker.getName() + " takes " + str(atkSelfDmg + defOtherDmg) + " damage after combat.")
        if atkStats[0] < 1: atkStats[0] = 1


    if defAlive and defSelfDmg != 0 or atkOtherDmg != 0:
        defStats[0] -= (defSelfDmg + atkOtherDmg)
        print(defender.getName() + " takes " + str(defSelfDmg + atkOtherDmg) + " damage after combat.")
        if defStats[0] < 1: defStats[0] = 1


    return atkStats[0],defStats[0]

class Hero:
    def __init__(self,name,hp,at,sp,df,rs,wpnType,movement,weapon,special,askill,bskill,cskill):

        # base unit info
        self.name = name
        self.intName = name
        self.hp=hp
        self.at=at
        self.sp=sp
        self.df=df
        self.rs=rs
        self.wpnType = wpnType
        self.move = movement  # 0 - inf, 1 - cav, 2 - fly, 3 - arm

        #specific unit skills
        self.weapon = weapon
        self.special = special
        self.askill = askill
        self.bskill = bskill
        self.cskill = cskill

    def getColor(self):
        if self.wpnType == "Sword" or self.wpnType == "RBow" or self.wpnType == "RDagger" or self.wpnType == "RTome" or self.wpnType == "RDragon" or self.wpnType == "RBeast":
            return "Red"
        if self.wpnType == "Axe" or self.wpnType == "GBow" or self.wpnType == "GDagger" or self.wpnType == "GTome" or self.wpnType == "GDragon" or self.wpnType == "GBeast":
            return "Green"
        if self.wpnType == "Lance" or self.wpnType == "BBow" or self.wpnType == "BDagger" or self.wpnType == "BTome" or self.wpnType == "BDragon" or self.wpnType == "BBeast":
            return "Blue"
        else:
            return "Colorless"

    def getMovement(self):
        return self.move

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
        return self.weapon

    def getSkills(self):
        heroSkills = {}
        if self.weapon != None: heroSkills.update(self.weapon.getEffects())
        if self.special != None:
            heroSkills.update(self.special.getEffects())
        if self.askill != None: heroSkills.update(self.askill.getEffects())
        if self.bskill != None: heroSkills.update(self.bskill.getEffects())

        return heroSkills

    def getCooldown(self):
        if self.special != None: return self.special.getCooldown()
        else: return -1


    def getStats(self):
        return [self.hp,self.at,self.sp,self.df,self.rs]

    def getName(self):
        return self.name

    def getSpName(self):
        return self.special.getName()

    def addSpecialLines(self,line0,line1,line2,line3):
        self.spLines = [""] * 4
        self.spLines[0] = line0
        self.spLines[1] = line1
        self.spLines[2] = line2
        self.spLines[3] = line3

    def getSpecialLine(self):
        x = random.randint(0,3)
        return self.spLines[x]

class Weapon:
    def __init__(self,name,desc,mt,range,effects):
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
        print(self.name + " \nMt: " + str(self.mt)  + " Rng: " + str(self.range) + "\n" + self.desc)
        return ""

class Skill:
    def __init__(self,name,desc,effects):
        self.name = name
        self.desc = desc
        self.effects = effects

    def getEffects(self):
        return self.effects

    def __str__(self):
        print(self.name + "\n" + self.desc)
        return ""

class Special (Skill):
    def __init__(self,name,desc,effects,cooldown):
        self.name = name
        self.desc = desc
        self.effects = effects
        self.cooldown = cooldown

    def getCooldown(self):
        return self.cooldown

    def getName(self):
        return self.name


folkvangr = Weapon("Fólkvangr","At start of turn, if unit's HP ≤ 50%, grants Atk+5 for 1 turn.",16,1,{"defiantAtk": 2})
fensalir = Weapon("Fensalir","At start of turn, inflicts Atk-4 on foes within 2 spaces through their next actions.",16,1,{"threatDef":2})
noatun = Weapon("Nóatún","If unit's HP ≤ 40%, unit can move to a space adjacent to any ally.",16,1,{"escRoute": 2})
lordlyLance = Weapon("Lordly Lance", "Effective against armored foes.",16,1,{"effArm": 3})
guardianAxe = Weapon("Guardian's Axe", "Accelerates Special trigger (cooldown count-1)",16,1,{"slaying": 1})
irisTome = Weapon("Iris's Tome", "Grants bonus to unit’s Atk = total bonuses on unit during combat.",14,2,{"combAtk": 0})
bindingBlade = Weapon("Binding Blade","If foe initiates combat, grants Def/Res+2 during combat.",16,1,{"defStance":1,"resStance":1})
fujinYumi = Weapon("Fujin Yumi", "Effective against flying foes. If unit's HP ≥ 50%, unit can move through foes' spaces.",14,2,{"pass":2,"effFly":0})
gloomBreath = Weapon("Gloom Breath", "At start of turn, inflicts Atk/Spd-7 on foes within 2 spaces through their next actions. After combat, if unit attacked, inflicts Atk/Spd-7 on target and foes within 2 spaces of target through their next actions. If foe's Range = 2, calculates damage using the lower of foe's Def or Res.",16,1,{"threatAtk":3,"threatSpd":7,"sealAtk":3,"sealSpd":3,"atkSmoke":3,"spdSmoke":3,"dragonCheck":0})
cordeliaLance = Weapon("Cordelia's Lance","Inflicts Spd-2. If unit initiates combat, unit attacks twice.",10,1,{"spdBoost": -2,"BraveAW":1})
armads = Weapon("Armads","If unit's HP ≥ 80% and foe initiates combat, unit makes a guaranteed follow-up attack.",16,1,{"QRW":2})
pantherLance = Weapon("Panther Lance","During combat, boosts unit's Atk/Def by number of allies within 2 spaces × 2. (Maximum bonus of +6 to each stat.)",16,1,{"localBoost2Atk":2,"localBoost2Def":2})
bullBlade = Weapon("Bull Blade","During combat, boosts unit's Atk/Def by number of allies within 2 spaces × 2. (Maximum bonus of +6 to each stat.)",16,1,{"localBoost2Atk":2,"localBoost2Def":2})
darkRoyalSpear = Weapon("Dark Royal Spear","If foe initiates combat or if foe's HP = 100% at start of combat, grants Atk/Def/Res+5 to unit during combat.",16,1,{"berkutBoost":5})
chercheAxe = Weapon("Cherche's Axe","Inflicts Spd-5. If unit initiates combat, unit attacks twice.",11,1,{"spdBoost": -5,"BraveAW":1})
durandal = Weapon("Durandal","If unit initiates combat, grants Atk+4 during combat.",16,1,{"atkBlow":2})
argentBow = Weapon("Argent Bow","Effective against flying foes. Inflicts Spd-2. If unit initiates combat, unit attacks twice.",8,2,{"effFly":0,"spdBoost": -2,"BraveAW":1})
solitaryBlade = Weapon("Solitary Blade","Accelerates Special trigger (cooldown count-1).",16,1,{"slaying":1})
purifyingBreath = Weapon("Purifying Breath","Slows Special trigger (cooldown count+1). Unit can counterattack regardless of foe's range. If foe's Range = 2, calculates damage using the lower of foe's Def or Res.",14,1,{"slaying":-1,"dragonCheck":0,"dCounter":0})
tomeOfOrder = Weapon("Tome of Order","Effective against flying foes. Grants weapon-triangle advantage against colorless foes, and inflicts weapon-triangle disadvantage on colorless foes during combat.",14,2,{"effFly":0,"colorlessAdv":0})
devilAxe = Weapon("Devil Axe","Grants Atk/Spd/Def/Res+4 during combat, but if unit attacked, deals 4 damage to unit after combat.",16,1,{"atkBlow":2,"spdBlow":2,"defBlow":2,"resBlow":2,"atkStance":2,"spdStance":2,"defStance":2,"resStance":2,"atkOnlySelfDmg":4})
forblaze = Weapon("Forblaze","At start of turn, inflicts Res-7 on foe on the enemy team with the highest Res through its next action.",14,2,{"atkChill":3})
corvusTome = Weapon("Corvus Tome","Grants weapon-triangle advantage against colorless foes, and inflicts weapon-triangle disadvantage on colorless foes during combat.",14,2,{"colorlessAdv":0})
tacticalBolt = Weapon("Tactical Bolt","Grants weapon-triangle advantage against colorless foes, and inflicts weapon-triangle disadvantage on colorless foes during combat.",14,2,{"colorlessAdv":0})
arthurAxe = Weapon("Arthur's Axe","If a bonus granted by a skill like Rally or Hone is active on unit, grants Atk/Spd/Def/Res+3 during combat.",16,1,{"buffGrantsAtk":3,"buffGrantsSpd":3,"buffGrantsDef":3,"buffGrantsRes":3})
axeOfVirility = Weapon("Axe of Virility","Effective against armored foes.",16,1,{"effArm":0})
siegfried = Weapon("Siegfried","Unit can counterattack regardless of foe's range.",16,1,{"dCounter":0})
berukaAxe = Weapon("Beruka's Axe","Accelerates Special trigger (cooldown count-1).",16,1,{"slaying":1})
wingSword = Weapon("Wing Sword","Effective against armored and cavalry foes.",16,1,{"effArm":0,"effCav":0})
camillaAxe = Weapon("Camilla's Axe","If unit is within 2 spaces of a cavalry or flying ally, grants Atk/Spd+4 during combat.",16,1,{"camillaBoost":0})
whitewingLance = Weapon("Whitewing Lance","Accelerates Special trigger (cooldown count-1).",16,1,{"slaying":1})
marthFalchion = Weapon("Falchion","Effective against dragon foes. At the start of every third turn, restores 10 HP.",16,1,{"effDragon":0,"recover":3})
awkFalchion = Weapon("Falchion","Effective against dragon foes. At the start of every third turn, restores 10 HP.",16,1,{"effDragon":0,"recover":3})

assault = Weapon("Assault","",10,2,{})
pain = Weapon("Pain","Deals 10 damage to target after combat.",3,2,{"atkOnlyOtherDmg":10})
painPlus = Weapon("Pain+","Deals 10 damage to target and foes within 2 spaces of target after combat.",10,2,{"atkOnlyOtherDmg":10,"savageBlow":4.5})
absorb = Weapon("Absorb","Restores HP = 50% of damage dealt.",3,2,{"absorb":0})
absorbPlus = Weapon("Absorb+","Restores HP = 50% of damage dealt. After combat, if unit attacked, restores 7 HP to allies within 2 spaces of unit.",7,2,{"absorb":0})

sapphireLance = Weapon("Sapphire Lance","If unit has weapon-triangle advantage, boosts Atk by 20%. If unit has weapon-triangle disadvantage, reduces Atk by 20%.",8,1,{"triangleAdeptW":3})
sapphireLancePlus = Weapon("Sapphire Lance+","If unit has weapon-triangle advantage, boosts Atk by 20%. If unit has weapon-triangle disadvantage, reduces Atk by 20%.",12,1,{"triangleAdeptW":3})



siegmund = Weapon("Siegmund","At start of turn, grants Atk+3 to adjacent allies for 1 turn.",16,1,{"honeAtk":2})
siegmundEff = Weapon("Siegmund","At start of turn, grants Atk+4 to adjacent allies for 1 turn. If unit's HP ≥ 90% and unit initiates combat, unit makes a guaranteed follow-up attack",16,1,{"HPBoost":3,"FollowUpEph":0})
naga = Weapon("Naga","Effective against dragon foes. If foe initiates combat, grants Def/Res+2 during combat.",14,2,{"defStance":1,"resStance":1,"effDragon":0})

almFalchion = Weapon("Falchion","Effective against dragons. At the start of every third turn, unit recovers 10 HP.",16,1,{"effDragon":0,"recover":3})
ragnell = Weapon("Ragnell","Unit can counterattack regardless of foe's range.",16,1,{"dCounter":0})

nidhogg = Weapon("Nidhogg","Effective against flying foes. During combat, boosts unit's Atk/Spd/Def/Res by number of adjacent allies × 2.",14,2,{"effFly":0,"owlBoost":2})

resoluteBlade = Weapon("Resolute Blade","Grants Atk+3. Deals +10 damage when Special triggers.",16,1,{"atkBoost":3,"spDmgAdd":10})
#pointyDemonspanker = Weapon ("Falchion")

#SPECIALS
noontime = Special("Noontime","Restores HP = 30% of damage dealt.",{"healSelf":3},2)
sol = Special("Sol","Restores HP = 50% of damage dealt.",{"healSelf":5},3)

moonbow = Special("Moonbow","Treats foe's Def/Res as if reduced by 30% during combat.",{"defReduce":3},2)
luna = Special("Luna","Treats foe's Def/Res as if reduced by 50% during combat.",{"defReduce":5},3)
aether = Special("Aether","Treats foe's Def/Res as if reduced by 50% during combat. Restores HP = half of damage dealt.",{"defReduce":5,"healSelf":5},5)

nightSky = Special("Night Sky","Boosts damage dealt by 50%.",{"dmgBoost":5,},3)
glimmer = Special("Glimmer","Boosts damage dealt by 50%.",{"dmgBoost":5,},2)
astra = Special("Astra","Boosts damage dealt by 150%.",{"dmgBoost":15,},4)


dragonGaze = Special("Dragon Gaze","Boosts damage by 30% of unit's Atk.",{"atkBoostSp":3},4)
draconicAura = Special("Draconic Aura","Boosts damage by 30% of unit's Atk.",{"atkBoostSp":3},3)
dragonFang = Special("Dragon Fang","Boosts damage by 50% of unit's Atk.",{"atkBoostSp":5},4)

bonfire = Special("Bonfire","Boosts damage by 50% of unit's Def.",{"defBoostSp":5},3)
ignis = Special("Ignis","Boost damage by 80% of unit's Def.",{"defBoostSp":8},4)

chillingWind = Special("Chilling Wind","Boosts damage by 50% of unit's Res.",{"resBoostSp":5},4)
iceberg = Special("Iceberg","Boosts damage by 50% of unit's Res.",{"resBoostSp":5},3)
glacies = Special("Glacies","Boosts damage by 80% of unit's Res.",{"resBoostSp":8},4)

#BASED ON POSITIONING, NOT FOE'S RANGE!!!!!
#CHANGE THIS ONCE YOU GET TO THE MAP!!!!!
pavise = Special("Pavise","Reduces damage from an adjacent foe's attack by 50%.",{"closeShield":5},3)
escutcheon = Special("Escutcheon","Reduces damage from an adjacent foe's attack by 30%.",{"closeShield":3},2)
sacredCowl = Special("Sacred Cowl","If foe is 2 spaces from unit, reduces damage from foe's attack by 30%.",{"distantShield":3},2)
aegis = Special("Aegis","If foe is 2 spaces from unit, reduces damage from foe's attack by 50%.",{"distantShield":5},3)


hp3 = Skill ("HP +3", "Grants HP+3.",{"HPBoost":3})
hp4 = Skill ("HP +4", "Grants HP+4.",{"HPBoost":4})
hp5 = Skill ("HP +5", "Grants HP+5.",{"HPBoost":5})
atk1 = Skill ("Attack +1","Grants Atk+1",{"atkBoost":1})
atk2 = Skill ("Attack +2","Grants Atk+2",{"atkBoost":2})
atk3 = Skill ("Attack +3","Grants Atk+3",{"atkBoost":3})
spd1 = Skill ("Speed +1","Grants Spd+1",{"spdBoost":1})
spd2 = Skill ("Speed +2","Grants Spd+2",{"spdBoost":2})
spd3 = Skill ("Speed +3","Grants Spd+3",{"spdBoost":3})
def1 = Skill("Defense +1", "Grants Def+1.",{"defBoost": 1})
def2 = Skill("Defense +2", "Grants Def+2.",{"defBoost": 2})
def3 = Skill("Defense +3", "Grants Def+3.",{"defBoost": 3})
res1 = Skill("Resistance +1", "Grants Res+1.",{"resBoost":1})
res2 = Skill("Resistance +2", "Grants Res+2.",{"resBoost":2})
res3 = Skill("Resistance +3", "Grants Res+3.",{"resBoost":3})

fortressDef1 = Skill("Fortress Def 1","Grants Def+3. Inflicts Atk-3.",{"defBoost":3,"atkBoost":-3})
fortressDef2 = Skill("Fortress Def 2","Grants Def+4. Inflicts Atk-3.",{"defBoost":4,"atkBoost":-3})
fortressDef3 = Skill("Fortress Def 3","Grants Def+5. Inflicts Atk-3.",{"defBoost":5,"atkBoost":-3})

fortressRes1 = Skill("Fortress Res 1","Grants Res+3. Inflicts Atk-3.",{"resBoost":3,"atkBoost":-3})
fortressRes2 = Skill("Fortress Res 2","Grants Res+4. Inflicts Atk-3.",{"resBoost":4,"atkBoost":-3})
fortressRes3 = Skill("Fortress Res 3","Grants Res+5. Inflicts Atk-3.",{"resBoost":5,"atkBoost":-3})

fury3 = Skill("Fury 3","Grants Atk/Spd/Def/Res+3. After combat, deals 6 damage to unit.",{"atkBoost":3,"spdBoost":3,"defBoost":3,"resBoost":3,"selfDmg":6})

waterBoost3 = Skill("Water Boost 3","At start of combat, if unit's HP ≥ foe's HP+3, grants Res+6 during combat.",{"waterBoost":3})

heavyBlade3 = Skill("Heavy Blade 3","If unit's Atk > foe's Atk, grants Special cooldown charge +1 per unit's attack. (Only highest value applied. Does not stack.)",{"heavyBlade":3})
flashingBlade3 = Skill("Flashing Blade 3","If unit's Spd > foe's Spd, grants Special cooldown charge +1 per unit's attack. (Only highest value applied. Does not stack.)",{"flashingBlade":3})
# HIGHEST TRIANGLE ADEPT LEVEL USED
# SMALLER LEVELS DO NOT STACK WITH ONE ANOTHER
# HIGHEST LEVEL IS BASICALLY MAX
deathBlow1 = Skill("Death Blow 1", "If unit initiates combat, grants Atk+2 during combat.",{"atkBlow": 1})
deathBlow2 = Skill("Death Blow 2", "If unit initiates combat, grants Atk+4 during combat.",{"atkBlow": 2})
deathBlow3 = Skill("Death Blow 3", "If unit initiates combat, grants Atk+6 during combat.",{"atkBlow": 3})
dartingBlow1 = Skill("Darting Blow 1", "If unit initiates combat, grants Spd+2 during combat.",{"spdBlow":1})
dartingBlow2 = Skill("Darting Blow 2", "If unit initiates combat, grants Spd+4 during combat.",{"spdBlow":2})
dartingBlow3 = Skill("Darting Blow 3", "If unit initiates combat, grants Spd+6 during combat.",{"spdBlow":3})
armoredBlow1 = Skill("Armored Blow 1", "If unit initiates combat, grants Def+2 during combat.",{"defBlow":1})
armoredBlow2 = Skill("Armored Blow 2", "If unit initiates combat, grants Def+4 during combat.",{"defBlow":2})
armoredBlow3 = Skill("Armored Blow 3", "If unit initiates combat, grants Def+6 during combat.",{"defBlow":3})
wardingBlow1 = Skill("Warding Blow 1", "If unit initiates combat, grants Res+2 during combat.",{"resBlow":1})
wardingBlow2 = Skill("Warding Blow 2", "If unit initiates combat, grants Res+4 during combat.",{"resBlow":2})
wardingBlow3 = Skill("Warding Blow 3", "If unit initiates combat, grants Res+6 during combat.",{"resBlow":3})

fierceStance1 = Skill("Fierce Stance 1", "If foe initiates combat, grants Atk+2 during combat.",{"atkStance":1})
fierceStance2 = Skill("Fierce Stance 2", "If foe initiates combat, grants Atk+4 during combat.",{"atkStance":2})
fierceStance3 = Skill("Fierce Stance 3", "If foe initiates combat, grants Atk+6 during combat.",{"atkStance":3})
dartingStance1 = Skill("Darting Stance 1", "If foe initiates combat, grants Spd+2 during combat.",{"spdStance":1})
dartingStance2 = Skill("Darting Stance 2", "If foe initiates combat, grants Spd+4 during combat.",{"spdStance":2})
dartingStance3 = Skill("Darting Stance 3", "If foe initiates combat, grants Spd+6 during combat.",{"spdStance":3})
steadyStance1 = Skill("Steady Stance 1", "If foe initiates combat, grants Def+2 during combat.",{"defStance":1})
steadyStance2 = Skill("Steady Stance 2", "If foe initiates combat, grants Def+4 during combat.",{"defStance":2})
steadyStance3 = Skill("Steady Stance 3", "If foe initiates combat, grants Def+6 during combat.",{"defStance":3})
wardingStance1 = Skill("Warding Stance 1", "If foe initiates combat, grants Res+2 during combat.",{"resStance":1})
wardingStance2 = Skill("Warding Stance 2", "If foe initiates combat, grants Res+4 during combat.",{"resStance":2})
wardingStance3 = Skill("Warding Stance 3", "If foe initiates combat, grants Res+6 during combat.",{"resStance":3})


triangleAdept3 = Skill("Triangle Adept 3","If unit has weapon-triangle advantage, boosts Atk by 20%. If unit has weapon-triangle disadvantage, reduces Atk by 20%.",{"triAdeptS":3})

closeCounter = Skill("Close Counter", "Unit can counterattack regardless of foe's range.",{"cCounter":0})
distanctCounter = Skill("Distant Counter", "Unit can counterattack regardless of foe's range.",{"dCounter":0})

swordBreaker3 = Skill("Swordbreaker 3", "If unit's HP ≥ 50% in combat against a sword foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.",{"swordBreak":3})
lanceBreaker3 = Skill("Lancebreaker 3", "If unit's HP ≥ 50% in combat against a lance foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.",{"lanceBreak":3})
axeBreaker3 = Skill("Axebreaker 3","If unit's HP ≥ 50% in combat against an axe foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.",{"axeBreak":3})
gtomeBreaker3 = Skill("G Tomebreaker 3","If unit's HP ≥ 50% in combat against a green tome foe, unit makes a guaranteed follow-up attack and foe cannot make a follow-up attack.",{"gtomeBreak":3})
vantage3 = Skill("Vantage 3","If unit's HP ≤ 75% and foe initiates combat, unit can counterattack before foe's first attack.",{"vantage":3})
quickRiposte = Skill("Quick Riposte 3", "If unit's HP ≥ 70% and foe initiates combat, unit makes a guaranteed follow-up attack.",{"QRS":3})
windsweep3 = Skill("Windsweep 3","If unit initiates combat, unit cannot make a follow-up attack. If unit’s Spd > foe’s Spd and foe uses sword, lance, axe, bow, dagger, or beast damage, foe cannot counterattack.",{"windsweep":3})
cancelAffinity1 = Skill("Cancel Affinity 1","Neutralizes all weapon-triangle advantage granted by unit's and foe's skills.",{"cancelTA":1})
cancelAffinity2 = Skill("Cancel Affinity 2","Neutralizes weapon-triangle advantage granted by unit's skills. If unit has weapon-triangle disadvantage, neutralizes weapon-triangle advantage granted by foe's skills.",{"cancelTA":2})
cancelAffinity3 = Skill("Cancel Affinity 3","Neutralizes weapon-triangle advantage granted by unit's skills. If unit has weapon-triangle disadvantage, reverses weapon-triangle advantage granted by foe's skills.",{"cancelTA":3})

spurRes = Skill("Spur Res 3", "Grants Res+4 to adjacent allies during combat.",{"spurRes":3})
wardCavalry = Skill("Ward Cavalry","Grants Def/Res+4 to cavalry allies within 2 spaces during combat.",{"ward":1})
goadArmor = Skill("Goad Armor","Grants Atk/Spd+4 to armored allies within 2 spaces during combat.",{"goad":3})

# PW Brave y
# EW Brave Y
# BW Brave Y
# PS Brave Y

#print(folkvangr)
#print(noatun)
#print(deathBlow3)
#print(guardianAxe)

abel = Hero("Abel",39,33,32,25,25,"Lance",1,pantherLance,None,hp5,swordBreaker3,None)
anna = Hero("Anna",41,29,38,22,28,"Axe",0,noatun,astra,None,vantage3,None)
alfonse = Hero("Alfonse",43,35,25,32,22,"Sword",0,folkvangr,None,deathBlow3,None,None)
arthur = Hero("Arthur",43,32,29,30,24,"Axe",0,arthurAxe,None,hp5,lanceBreaker3,None)
azama = Hero("Azama",43,21,26,32,25,"Staff",0,painPlus,None,None,None,None)
azura = Hero("Azura",36,31,33,21,28,"Lance",0,sapphireLancePlus,None,spd3,None,None)
barst = Hero("Barst",46,33,32,30,17,"Axe",0,devilAxe,None,None,None,None)
bartre = Hero("Bartre",49,36,25,33,13,"Axe",0,axeOfVirility,None,fury3,None,None)
beruka = Hero("Beruka",46,29,23,37,22,"Axe",2,berukaAxe,glimmer,None,None,None)
caeda = Hero("Caeda",36,25,37,24,34,"Sword",2,wingSword,None,dartingBlow3,None,None)
cain = Hero("Cain",42,32,32,27,21,"Sword",1,bullBlade,None,None,None,None)
camilla = Hero("Camilla",37,30,32,28,31,"Axe",2,camillaAxe,draconicAura,dartingBlow3,None,None)
catria = Hero("Catria",39,31,34,29,25,"Lance",2,whitewingLance,luna,armoredBlow3,None,None)
cecilia = Hero("Cecilia",36,32,25,22,29,"GTome",1,tomeOfOrder,None,atk3,None,None)
cherche = Hero("Cherche",46,38,25,32,16,"Axe",2,chercheAxe,None,atk3,None,None)
chrom = Hero("Chrom",47,37,25,31,17,"Sword",0,awkFalchion,aether,None,None,None)
cordelia = Hero("Cordelia",40,35,35,22,25,"Lance",2,cordeliaLance,None,triangleAdept3,None,None)
corrinF = Hero("Corrin",41,27,34,34,21,"BDragon",0,gloomBreath,None,deathBlow3,None,None)
eliwood = Hero("Eliwood",39,31,30,23,32,"Sword",1,durandal,sacredCowl,None,axeBreaker3,None)
hawkeye = Hero("Hawkeye",45,33,22,28,30,"Axe",0,guardianAxe,None,deathBlow3,None,None)
hector = Hero("Hector",52,36,24,37,19,"Axe",3,armads,pavise,distanctCounter,None,goadArmor)
henry = Hero("Henry",45,23,22,32,25,"RTome",0,corvusTome,ignis,None,gtomeBreaker3,None)
lilina = Hero("Lilina",35,37,25,19,31,"RTome",0,forblaze,moonbow,atk3,None,None)
lonqu = Hero("Lon'qu",45,29,39,22,22,"Sword",0,solitaryBlade,glimmer,spd3,vantage3,None)
marth = Hero("Marth",41,31,34,29,23,"Sword",0,marthFalchion,draconicAura,fury3,quickRiposte,None)
nino = Hero("Nino",33,33,36,19,26,"GTome",0,irisTome,None,res3,None,None)
nowi = Hero("Nowi",45,34,27,30,27,"BDragon",0,purifyingBreath,None,def3,None,None)
robinM = Hero("Robin",40,29,29,29,22,"BTome",0,tacticalBolt,bonfire,None,None,None)
roy = Hero("Roy",44,30,31,25,28,"Sword",0,bindingBlade,moonbow,triangleAdept3,None,None)
serra = Hero("Serra",33,30,31,21,33,"Staff",0,absorbPlus,None,None,None,None)
sharena = Hero("Sharena",43,32,32,29,22,"Lance",0,fensalir,None,spd3,None,None)
takumi = Hero("Takumi",40,32,33,25,18,"CBow",0,fujinYumi,None,closeCounter,None,None)
xander = Hero("Xander",44,32,24,37,17,"Sword",1,siegfried,noontime,armoredBlow3,axeBreaker3,None)

eirika = Hero("Eirika",40,30,34,27,23,"Sword",0,None,None,None,None,None)
ephraim = Hero("Ephraim",45,35,25,32,20,"Lance",0,siegmundEff,moonbow,deathBlow3,None,None)
seliph = Hero("Seliph",40,30,30,30,20,"Sword",0,None,None,None,None,None)
julia = Hero("Julia",38,35,26,17,32,"GTome",0,naga,dragonFang,res3,None,None)

klein = Hero("Klein",40,31,33,20,24,"CBow",0,argentBow,glacies,deathBlow3,quickRiposte,None)
sanaki = Hero("Sanaki",30,30,30,20,20,"RTome",0,None,None,None,None,None)
#NOT YET HE'S GONNA RUIN EVERYTHING reinhardt = Hero("")
olwen = Hero("Olwen",35,30,30,20,15,"BTome",1,None,None,None,None,None)
eldigan = Hero("Eldigan",40,30,25,30,15,"Sword",1,None,None,None,None,None)
lachesis = Hero("Lachesis",30,30,30,15,20,"Staff",0,None,None,None,None,None)

alm = Hero("Alm",45,33,30,28,22,"Sword",0,almFalchion,draconicAura,atk3,windsweep3,None)

ike = Hero("Ike",42,35,31,32,18,"Sword",1,ragnell,aether,heavyBlade3,swordBreaker3,None)

berkut = Hero("Berkut",43,34,22,31,24,"Lance",1,darkRoyalSpear,None,waterBoost3,None,wardCavalry)
clive = Hero("Clive",45,33,25,32,19,"Lance",1,lordlyLance,escutcheon,def3,None,None)

innes = Hero("Innes",35,33,34,14,31,"CBow",0,nidhogg,iceberg,fortressRes3,cancelAffinity3,None)

mia = Hero("Mia",38,32,40,28,25,"Sword",0,resoluteBlade,noontime,flashingBlade3,vantage3,None)

#print(str(len(heroes)) + " Heroes present. " + str(927-len(heroes)) + " remain to be added.")

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

playerUnits = [marth,robinM,takumi,ephraim]
enemyUnits = [nowi,alm,hector,bartre]

#r = simulate_combat(ephraim,takumi)
#print(r)

#APPLY THE EFFECTS ON THE UNITS BEING AFFECTED AND NOT THE UNIT CAUSING THE EFFECT ON THE MAP
#IF MARTH IS FIGHTING EPHRAIM WITH THREATEN DEF 3, GIVE MARTH (IF UNIT IS WITHIN 2 SPACES WITHIN
#EPHRAIM, GIVE -7 DEF. I AM A GENIUS.

class HeroDirectory:

    def __init__(self):
        self.heroes = [cordelia,alfonse,corrinF,hawkeye,clive,nino,roy,hector,ephraim,abel,takumi,anna,berkut,
        cherche,eliwood,klein,lonqu,nowi,alm,innes,ike,julia,barst,lilina,mia,henry,robinM,
        arthur,azama,azura,bartre,xander,beruka,caeda,cain,camilla,catria]

    def getHeroes(self):
        return self.heroes


results = []
#for hero in heroes:
#    results.append(simulate_combat(xander,hero))
#print(results)

#ATK AND WEAPON SKILLS DO STACK W/ HOW PYTHON MERGES DICTIONARIES
#JUST KEEP IN MIND ONCE YOU GET TO THAT BRIDGE WITH SKILLS NOT MEANT TO STACK
