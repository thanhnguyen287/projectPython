from settings import advance_to_second_age_icon, advance_to_third_age_icon, advance_to_fourth_age_icon


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


Age_II = Technology("Advance to Feudal Age", advance_to_second_age_icon,[0,500,0,0], ["House"], "In the Feudal Age, you can train a variety of new military units and construct new buildings such as the Barracks.")
Age_III = Technology("Advance to Castle Age", advance_to_third_age_icon,[0,800,200,0], ["House"], "Train powerful military units such as Knights and Siege Weapons. Diversify your strategies with advanced technologies and construct Castles.")
Age_IV = Technology("Advance to Imperial Age", advance_to_fourth_age_icon,[0,1000,800,0], ["House"], "Train the most advanced military units such as Paladins and dominating siege weapons like the mighty Trebuchet. Access powerful technologies such as ‘Chemistry’, allow training of Hand Cannoneers and Bombard Cannons, and construct your civilization’s Wonder if you’re pursuing a Wonder Victory.t new buildings such as the Barracks.")
