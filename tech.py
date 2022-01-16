from settings import advance_to_second_age_icon, advance_to_third_age_icon, advance_to_fourth_age_icon, sword_tech_icon, \
    arrow_tech_icon, horseshoe_tech_icon, cow_tech, improved_masonry_icon, fortified_masonry_icon, imbued_masonry_icon, \
    iron_sword_icon, steel_sword_icon, mithril_sword_icon, iron_armor_icon, steel_armor_icon, mithril_armor_icon


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

    def tech_increase_armor(self, player, for_building=False):
        if not for_building:
            for unit in player.unit_list:
                unit.armor += 2
        else:
            for building in player.building_list:
                building.armor += 3

    def tech_increase_dmg(self, player):
        for unit in player.unit_list:
            unit.attack_dmg += 5
            player.iron_swords_unlocked = True

    def tech_increase_max_health(self, player):
        for building in player.building_list:
            building.max_health += 75
            building.current_health += 75
            player.improved_masonry_unlocked = True


Age_II = Technology("Advance to Feudal Age", advance_to_second_age_icon,[0,500,0,0], ["House"], "In the Feudal Age, you can train a variety of new military units and construct new buildings such as the Barracks.")
Age_III = Technology("Advance to Castle Age", advance_to_third_age_icon,[0,800,200,0], ["House"], "Train powerful military units such as Knights and Siege Weapons. Diversify your strategies with advanced technologies and construct Castles.")
Age_IV = Technology("Advance to Imperial Age", advance_to_fourth_age_icon,[0,1000,800,0], ["House"], "Train the most advanced military units such as Paladins and dominating siege weapons like the mighty Trebuchet. Access powerful technologies such as ‘Chemistry’, allow training of Hand Cannoneers and Bombard Cannons, and construct your civilization’s Wonder if you’re pursuing a Wonder Victory.t new buildings such as the Barracks.")

iron_sword_tech = Technology("Research Iron swords", iron_sword_icon,[25,0,75,200], "2", " Increases Clubmen et Villagers' damages by 5.")
steel_sword_tech = Technology("Research Steel swords", steel_sword_icon,[50,0,150,300], "3", " Increases again Clubmen et Villagers' damages by 5.")
mithril_sword_tech = Technology("Research Mithril swords", mithril_sword_icon,[75,0,225,400], "4", " Increases yet another time Clubmen et Villagers' damages by 5.")

iron_armor_tech = Technology("Research Iron armors", iron_armor_icon,[25,0,75,200], "2", " Increases Clubmen et Villagers' armor by 2.")
steel_armor_tech = Technology("Research Steel armors", steel_armor_icon,[50,0,150,300], "3", " Increases again Clubmen et Villagers' armor by 2.")
mithril_armor_tech = Technology("Research Mithril armors", mithril_armor_icon,[75,0,225,400], "4", " Increases yet another time Clubmen et Villagers' armor by 2.")

improved_masonry_tech = Technology("Research Improved Masonry", improved_masonry_icon,[150,0,100,200], "2", " Increases the armor and hit points of buildings.")
reinforced_masonry_tech = Technology("Research Reinforced Masonry", fortified_masonry_icon,[350,0,125,250], "3", " Increases again the armor and hit points of buildings.")
imbued_masonry_tech = Technology("Research Imbued Masonry", imbued_masonry_icon,[500,0,150,300], "4", " Increases yet another time the armor and hit points of buildings")

arrow_tech = Technology("Research Iron arrows", arrow_tech_icon,[500,0,250,500], "1", " Increases Bowmen's damages by 5.")
horseshoe_tech = Technology("Research Iron horseshoes", horseshoe_tech_icon,[500,0,250,500], "1", " Does cool stuff to your non-existant horses")
food_production_tech = Technology("Research Super Cows", cow_tech,[500,0,250,500], "1", " Your farm now produces 5 wood every 10 secs.")
