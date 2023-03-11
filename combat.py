import math
import random

def simulate_combat(attacker,defender):
    atkSkills = attacker.getSkills()
    atkStats = attacker.getStats()
    defSkills = defender.getSkills()
    defStats = defender.getStats()


    atkStats[1] += attacker.getWeapon().getMT()
    defStats[1] += defender.getWeapon().getMT()

    triAdept = -1
    ignoreRng = False
    braveATKR = False
    braveDEFR = False

    flyEffA = False
    flyEffD = False
    armEffA = False
    armEffD = False

    atkFollowUps = 0
    defFollowUps = 0

    atkSpecialCounter = attacker.getCooldown()
    defSpecialCounter = defender.getCooldown()
    permASC = atkSpecialCounter
    permDSC = defSpecialCounter

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
        if key == "HPBoost":
            atkStats[0] += atkSkills["HPBoost"]
        if key == "spdBoost":
            atkStats[2] += atkSkills["spdBoost"]
        if key == "defBoost":
            atkStats[3] += atkSkills["defBoost"]
        if key == "resBoost":
            atkStats[4] += atkSkills["resBoost"]
        if key == "atkBlow":
            atkStats[1] += atkSkills["atkBlow"] * 2
        if key == "triAdeptS" or key == "triAdeptW":
            if atkSkills[key] > triAdept:
                triAdept = atkSkills[key]
        if key == "BraveAW" or key == "BraveAS" or key == "BraveBW":
            braveATKR = True
        if key == "effFly":
            flyEffA = True
        if key == "effArm":
            armEffA = True

        if key == "defReduce":
            ASpecialType = "Offense"
            ASpDefReduce = atkSkills[key]
            atkSpEffects.update({"defReduce":atkSkills[key]})

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

    defSpEffects = {}

    for key in defSkills:
        if key == "HPBoost":
            defStats[0] += defSkills["HPBoost"]
        if key == "spdBoost":
            defStats[2] += defSkills["spdBoost"]
        if key == "defBoost":
            defStats[3] += defSkills["defBoost"]
        if key == "resBoost":
            defStats[4] += defSkills["resBoost"]
        if key == "defStance":
            defStats[3] += defSkills["defStance"] * 2
        if key == "resStance":
            defStats[4] += defSkills["resStance"] * 2
        if key == "triAdeptS" or key == "triAdeptW":
            if defSkills[key] > triAdept:
                triAdept = defSkills[key]
        if key == "cCounter" or key == "dCounter":
            ignoreRng = True
        if key == "BraveDW" or key == "BraveBW":
            braveDEFR = True
        if key == "effFly":
            flyEffD = True
        if key == "effArm":
            armEffD = True
        if key == "QRW" or key == "QRS":
            defFollowUps += 1

        if key == "defReduce":
            DSpecialType = "Offense"
            DSpDefReduce = defSkills[key]
            defSpEffects.update({"defReduce":defSkills[key]})
        if key == "closeShield":
            DSpecialType = "Defense"
            defSpEffects.update({"closeShield":defSkills[key]})

    if flyEffA and defender.getMovement() == 2:
        atkStats[1] += math.trunc(atkStats[1] * 0.5)
    if flyEffD and attacker.getMovement() == 2:
        defStats[1] += math.trunc(defStats[1] * 0.5)

    if armEffA and defender.getMovement() == 3:
        atkStats[1] += math.trunc(atkStats[1] * 0.5)
    if armEffD and attacker.getMovement() == 3:
        defStats[1] += math.trunc(defStats[1] * 0.5)

    if (attacker.getColor() == "Red" and defender.getColor() == "Green") or (attacker.getColor() == "Green" and defender.getColor() == "Blue") or (attacker.getColor() == "Blue" and defender.getColor() == "Red"):
        atkStats[1] += math.trunc(atkStats[1] * (0.25 + .05 * triAdept))
        defStats[1] -= math.trunc(defStats[1] * (0.25 + .05 * triAdept))
    if (attacker.getColor() == "Blue" and defender.getColor() == "Green") or (attacker.getColor() == "Red" and defender.getColor() == "Blue") or (attacker.getColor() == "Green" and defender.getColor() == "Red"):
        atkStats[1] -= math.trunc(atkStats[1] * (0.25 + .05 * triAdept))
        defStats[1] += math.trunc(defStats[1] * (0.25 + .05 * triAdept))


    r = 0 #isResTargeted by atkr
    x = 0 #isResTargeted by defr
    if attacker.getTargetedDef() == 1:
        r += 1
    if attacker.getTargetedDef() == 0:
        if defender.getRange() == 2:
            if defStats[3] > defStats[4]:
                r += 1
            else:
                r += 0
        else:
            r += 1

    if defender.getTargetedDef() == 1:
        x += 1
    if defender.getTargetedDef() == 0:
        if attacker.getRange() == 2:
            if atkStats[3] > atkStats[4]:
                x += 1
            else:
                x += 0
        else:
            x += 1

    print(atkStats)
    print(defStats)

    if(atkStats[2] > defStats[2] + 4):
        atkFollowUps += 1

    if (atkStats[2] + 4 < defStats[2]):
        defFollowUps += 1

    atkAlive = True
    defAlive = True

    atkSpecialTriggered = False
    defSpecialTriggered = False

    # START OF COMBAT
    ###################################################################################################################

    # first attack by attacker

    atkInitStats = atkStats[:]
    defInitStats = defStats[:]

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

    defStats[0] = defStats[0] - atkrATK1
    print(attacker.getName() + " attacks " + defender.getName() + " for " + str(atkrATK1) + " damage.")

    if atkSpecialCounter > 0: atkSpecialCounter -= 1
    if defSpecialCounter > 0: defSpecialCounter -= 1

    if atkSpecialTriggered: atkSpecialCounter = permASC
    atkSpecialTriggered = False

    newHPA = atkStats[0]
    newHPD = defStats[0]

    atkStats = atkInitStats
    defStats = defInitStats

    atkStats[0] = newHPA
    defStats[0] = newHPD

    if defStats[0] <= 0:
        defStats[0] = 0
        defAlive = False
        print(defender.getName() + " falls.")
    if braveATKR and defAlive:
        braveATK1 = atkStats[1] - defStats[3+r]
        if braveATK1 < 0: braveATK1 = 0
        defStats[0] = defStats[0] - braveATK1
        print(attacker.getName() + " attacks " + defender.getName() + " for " + str(braveATK1) + " damage.")
        if atkSpecialCounter > 0: atkSpecialCounter -= 1
        if defSpecialCounter > 0: defSpecialCounter -= 1
        if defStats[0] <= 0:
            defStats[0] = 0
            defAlive = False
            print(defender.getName() + " falls.")


    # first counterattack by defender

    if (attacker.getRange() == defender.getRange() or ignoreRng) and defAlive:

        defrATK1 = defStats[1] - atkStats[3+x]
        if defrATK1 < 0: defrATK1 = 0
        atkStats[0] = atkStats[0] - defrATK1
        print(defender.getName() + " attacks " + attacker.getName() + " for " + str(defrATK1) + " damage.")
        if atkSpecialCounter > 0: atkSpecialCounter -= 1
        if defSpecialCounter > 0: defSpecialCounter -= 1
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
            if defSpecialCounter > 0: defSpecialCounter -= 1
            if atkStats[0] <= 0:
                atkStats[0] = 0
                atkAlive = False
                print(attacker.getName() + " falls.")

    # second attack by attacker
    if atkFollowUps > 0 and atkAlive and defAlive:

        if atkSpecialCounter == 0 and ASpecialType == "Offense":
            print(attacker.getName() + " procs " + attacker.getSpName() + ".")  # attack name
            print(attacker.getSpecialLine())
            for key in atkSpEffects:
                if key == "defReduce":
                    atkSpecialTriggered = True
                    defStats[3] -= math.trunc(defStats[3] * .10 * atkSpEffects["defReduce"])
                    defStats[4] -= math.trunc(defStats[4] * .10 * atkSpEffects["defReduce"])




        atkrATK2 = atkStats[1] - defStats[3+r]
        if atkrATK2 < 0: atkrATK2 = 0

        if defSpecialCounter == 0 and DSpecialType == "Defense" and attacker.getRange() == 1:
            print(defender.getName() + " procs " + defender.getSpName() + ".")
            print(defender.getSpecialLine())
            for key in defSpEffects:
                if key == "closeShield":
                    defSpecialTriggered = True
                    atkrATK2 -= math.trunc(atkrATK2 * 0.10 * defSpEffects["closeShield"])

        defStats[0] = defStats[0] - atkrATK2

        print(attacker.getName() + " attacks " + defender.getName() + " for " + str(atkrATK2) + " damage.")
        if atkSpecialCounter > 0: atkSpecialCounter -= 1
        if defSpecialCounter > 0: defSpecialCounter -= 1
        if atkSpecialTriggered: atkSpecialCounter = permASC
        if defSpecialTriggered: defSpecialCounter = permDSC

        atkSpecialTriggered = False
        defSpecialTriggered = False

        newHPA = atkStats[0]
        newHPD = defStats[0]

        atkStats = atkInitStats
        defStats = defInitStats

        atkStats[0] = newHPA
        defStats[0] = newHPD

        if defStats[0] <= 0:
            defStats[0] = 0
            defAlive = False
            print(defender.getName() + " falls.")
        if braveATKR and defAlive:
            braveATK2 = atkStats[1] - defStats[3 + r]
            if braveATK2 < 0: atkrATK2 = 0
            defStats[0] = defStats[0] - braveATK2
            print(attacker.getName() + " attacks " + defender.getName() + " for " + str(braveATK2) + " damage.")
            if defStats[0] <= 0:
                defStats[0] = 0
                defAlive = False
                print(defender.getName() + " falls.")

    # second counterattack by defender

    if (defFollowUps > 0 and (attacker.getRange() == defender.getRange() or ignoreRng)) and atkAlive and defAlive:

        if defSpecialCounter == 0 and DSpecialType == "Offensive":
            print(defender.getName() + " procs " + defender.getSpName() + ".")  # attack name
            print(defender.getSpecialLine())
            for key in defSpEffects:
                if key == "defReduce":
                    defSpecialTriggered = True
                    atkStats[3] -= math.trunc(atkStats[3] * .10 * defSpEffects["defReduce"])
                    atkStats[4] -= math.trunc(atkStats[4] * .10 * defSpEffects["defReduce"])

        defrATK2 = defStats[1] - atkStats[3+x]
        if defrATK2 < 0: defrATK2 = 0
        atkStats[0] = atkStats[0] - defrATK2

        print(defender.getName() + " attacks " + attacker.getName() + " for " + str(defrATK2) + " damage.")
        if atkSpecialCounter > 0: atkSpecialCounter -= 1
        if defSpecialCounter > 0: defSpecialCounter -= 1
        if defSpecialTriggered: defSpecialCounter = permDSC
        defSpecialTriggered = False

        newHPA = atkStats[0]
        newHPD = defStats[0]

        atkStats = atkInitStats
        defStats = defInitStats

        atkStats[0] = newHPA
        defStats[0] = newHPD

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



    return atkStats[0],defStats[0]

class Hero:
    def __init__(self,name,hp,at,sp,df,rs,wpnType,movement,weapon,special,askill,bskill,cskill):

        # base unit info
        self.name = name
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

    def setHP(self,damage):
        self.tempHP -= damage
        if self.tempHP < 0:
            self.tempHP = 0

    def getColor(self):
        if self.wpnType == "Sword" or self.wpnType == "RBow" or self.wpnType == "RDagger" or self.wpnType == "RTome" or self.wpnType == "RDragon" or self.wpnType == "RBeast":
            return "Red"
        if self.wpnType == "Axe" or self.wpnType == "GBow" or self.wpnType == "GDagger" or self.wpnType == "GTome" or self.wpnType == "GDragon" or self.wpnType == "GBeast":
            return "Green"
        if self.wpnType == "Lance" or self.wpnType == "BBow" or self.wpnType == "BDagger" or self.wpnType == "BTome" or self.wpnType == "BDragon" or self.wpnType == "BBeast":
            return "Blue"
        else:
            return "INVALID"

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

    def getWeapon(self):
        return self.weapon

    def getSkills(self):
        heroSkills = {}
        if self.weapon != None: heroSkills.update(self.weapon.getEffects())
        if self.special != None:
            heroSkills.update(self.special.getEffects())
        if self.askill != None: heroSkills.update(self.askill.getEffects())

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
noatun = Weapon("Nóatún","If unit's HP ≤ 40%, unit can move to a space adjacent to any ally.",16,1,{"escRoute": 2})
lordlyLance = Weapon("Lordly Lance", "Effective against armored foes.",16,1,{"effArm": 3})
guardianAxe = Weapon("Guardian's Axe", "Accelerates Special trigger (cooldown count-1)",16,1,{"slaying": 1})
irisTome = Weapon("Iris's Tome", "Grants bonus to unit’s Atk = total bonuses on unit during combat.",14,2,{"combAtk": 0})
bindingBlade = Weapon("Binding Blade","If foe initiates combat, grants Def/Res+2 during combat.",16,1,{"defStance":1,"resStance":1})
fujinYumi = Weapon("Fujin Yumi", "Effective against flying foes. If unit's HP ≥ 50%, unit can move through foes' spaces.",14,2,{"pass":2,"effFly":0})
gloomBreath = Weapon("Gloom Breath", "At start of turn, inflicts Atk/Spd-7 on foes within 2 spaces through their next actions. After combat, if unit attacked, inflicts Atk/Spd-7 on target and foes within 2 spaces of target through their next actions. If foe's Range = 2, calculates damage using the lower of foe's Def or Res.",16,1,{"threatAtk":3,"threatSpd":7,"sealAtk":3,"sealSpd":3,"atkSmoke":3,"spdSmoke":3})
cordeliaLance = Weapon("Cordelia's Lance","Inflicts Spd-2. If unit initiates combat, unit attacks twice.",10,1,{"spdBoost": -2,"BraveAW":1})
armads = Weapon("Armads","If unit's HP ≥ 80% and foe initiates combat, unit makes a guaranteed follow-up attack.",16,1,{"QRW":2})
siegmund = Weapon("Siegmund","At start of turn, grants Atk+3 to adjacent allies for 1 turn.",16,1,{"honeAtk":2})
pantherLance = Weapon("Panther Lance","During combat, boosts unit's Atk/Def by number of allies within 2 spaces × 2. (Maximum bonus of +6 to each stat.)",16,1,{"localBoost2Atk":2,"localBoost2Def":2})

#SPECIALS
moonbow = Special("Moonbow","Treats foe's Def/Res as if reduced by 30% during combat.",{"defReduce":3},2)
aether = Special("Aether","Treats foe's Def/Res as if reduced by 50% during combat. Restores HP = half of damage dealt.",{"defReduce":5,"healSelf":5},4)

nightSky = Special("Night Sky","Boosts damage dealt by 50%.",{"dmgBoost":1,},3)
glimmer = Special("Glimmer","Boosts damage dealt by 50%.",{"dmgBoost":1,},2)
astra = Special("Astra","Boosts damage dealt by 150%.",{"dmgBoost":3,},4)

bonfire = Special("Bonfire","Boosts damage by 50% of unit's Def.",{"defBoost":5},3)

#BASED ON POSITIONING, NOT FOE'S RANGE!!!!!
#CHANGE THIS ONCE YOU GET TO THE MAP!!!!!
pavise = Special("Pavise","Reduces damage from an adjacent foe's attack by 50%.",{"closeShield":5},3)
aegis = Special("Aegis","If foe is 2 spaces from unit, reduces damage from foe's attack by 50%.",{"distantShield":5},3)

deathBlow3 = Skill("Death Blow 3", "If unit initiates combat, grants Atk+6 during combat.",{"atkBlow": 3})
# HIGHEST TRIANGLE ADEPT LEVEL USED
# SMALLER LEVELS DO NOT STACK WITH ONE ANOTHER
# HIGHEST LEVEL IS BASICALLY MAX
triangleAdept3 = Skill("Triangle Adept 3","If unit has weapon-triangle advantage, boosts Atk by 20%. If unit has weapon-triangle disadvantage, reduces Atk by 20%.",{"triAdeptS":3})
hp5 = Skill ("HP +5", "Grants HP+5.",{"HPBoost":5})
def3 = Skill("Defense +3", "Grants Def+3.",{"defBoost": 3})
res3 = Skill("Resistance +3", "Grants Res+3.",{"resBoost":3})
closeCounter = Skill("Close Counter", "Unit can counterattack regardless of foe's range.",{"cCounter":0})
distanctCounter = Skill("Distant Counter", "Unit can counterattack regardless of foe's range.",{"dCounter":0})
goadArmor = Skill("Goad Armor","Grants Atk/Spd+4 to armored allies within 2 spaces during combat.",{"goad":3})

# PW Brave y
# EW Brave Y
# BW Brave Y
# PS Brave Y

#print(folkvangr)
#print(noatun)
#print(deathBlow3)
#print(guardianAxe)

alfonse = Hero("Alfonse",43,35,25,32,22,"Sword",0,folkvangr,None,deathBlow3,None,None)
hawkeye = Hero("Hawkeye",45,33,22,28,30,"Axe",0,guardianAxe,None,deathBlow3,None,None)
clive = Hero("Clive",45,33,25,32,19,"Lance",1,lordlyLance,None,def3,None,None)
nino = Hero("Nino",33,33,36,19,29,"GTome",0,irisTome,None,res3,None,None)
roy = Hero("Roy",44,30,31,25,28,"Sword",0,bindingBlade,moonbow,triangleAdept3,None,None)
takumi = Hero("Takumi",40,32,33,25,18,"CBow",0,fujinYumi,None,closeCounter,None,None)
corrin = Hero("Corrin",41,27,34,34,21,"BDragon",0,gloomBreath,None,deathBlow3,None,None)
cordelia = Hero("Cordelia",40,35,35,22,25,"Lance",2,cordeliaLance,None,triangleAdept3,None,None)
hector = Hero("Hector",52,36,24,37,19,"Axe",3,armads,pavise,distanctCounter,None,None)
ephraim = Hero("Ephraim",45,35,25,32,20,"Lance",0,siegmund,moonbow,deathBlow3,None,None)
abel = Hero("Abel",39,33,32,25,25,"Lance",1,pantherLance,None,hp5,None,None)

roy.addSpecialLines("\"I will win!\"",
                    "\"There's my opening!\"",
                    "\"By my blade!\"",
                    "\"I won't lose. I won't!\"")

hector.addSpecialLines("\"I don't back down!\"",
                       "\"Gutsy, aren't you?\"",
                       "\"Enough chitchat!\"",
                       "\"Here we go!\"")



r = simulate_combat(cordelia,abel)
print(r)



#ATK AND WEAPON SKILLS DO STACK W/ HOW PYTHON MERGES DICTIONARIES
#JUST KEEP IN MIND ONCE YOU GET TO THAT BRIDGE WITH SKILLS NOT MEANT TO STACK