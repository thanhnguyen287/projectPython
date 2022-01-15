from settings import advance_to_second_age_icon, advance_to_third_age_icon, advance_to_fourth_age_icon, sword_tech_icon, \
    arrow_tech_icon, horseshoe_tech_icon, cow_tech


class Technology:
    #costs de la forme : [{]"WOOD": 100, "FOOD": 100, "GOLD": 100, "STONE":100]
    # requirements contains the name of buildings/techs/ages needed to unlock this technology
    def __init__(self, name, icon, costs, requirements, description):
        self.name = name
        self.icon = icon
        self.construction_costs = costs
        self.requirements = requirements
        self.description = description
        self.has_been_researched = False
        self.affordable = False
        # in secs
        self.research_time = 30

    def tech_increase_armor(self, player):
        for unit in player.unit_list:
            unit.armor += type(unit).armor_age_bonus

    def tech_increase_dmg(self, player):
        for unit in player.unit_list:
            unit.attack_dmg += 5


Age_II = Technology("Advance to Feudal Age", advance_to_second_age_icon,[0,500,0,0], ["House"], "In the Feudal Age, you can train a variety of new military units and construct new buildings such as the Barracks.")
Age_III = Technology("Advance to Castle Age", advance_to_third_age_icon,[0,800,200,0], ["House"], "Train powerful military units such as Knights and Siege Weapons. Diversify your strategies with advanced technologies and construct Castles.")
Age_IV = Technology("Advance to Imperial Age", advance_to_fourth_age_icon,[0,1000,800,0], ["House"], "Train the most advanced military units such as Paladins and dominating siege weapons like the mighty Trebuchet. Access powerful technologies such as ‘Chemistry’, allow training of Hand Cannoneers and Bombard Cannons, and construct your civilization’s Wonder if you’re pursuing a Wonder Victory.t new buildings such as the Barracks.")
iron_sword_tech = Technology("Research Iron swords", sword_tech_icon,[500,0,250,500], "None", " Increases Clubmen et Villagers' damages by 5.")
arrow_tech = Technology("Research Iron arrows", arrow_tech_icon,[500,0,250,500], "None", " Increases Bowmen's damages by 5.")
horseshoe_tech = Technology("Research Iron horseshoes", horseshoe_tech_icon,[500,0,250,500], "None", " Does cool stuff to your non-existant horses")
food_production_tech = Technology("Research Super Cows", cow_tech,[500,0,250,500], "None", " Your farm now produces 5 wood every 10 secs.")