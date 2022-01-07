from settings import stop_icon, action_menu


class ActionMenu:
    def __init__(self):
        self.buttons = []
        self.is_cancel_button_present = False

    def add_button(self, button):
        self.buttons.append(button)

    def remove_button(self, button_to_destroy_name: str):
        for button in self.buttons:
            if button.name == button_to_destroy_name:
                self.buttons.remove(button)

    def edit_button(self, info):
        ...

    #cancel_button is always at the bottom right of the action_panel
    def add_cancel_button(self, hud_height, ):
        action_button = ActionButton(11, hud_height,  name="Cancel", icon=stop_icon, description="Cancel the current action.")
        self.add_button(action_button)


#button_pos goes from 0 to 11
class ActionButton:
    icon_size = 50
    width_between_icons = 60

    def __init__(self, button_pos:int, hud_height, name=None, icon=None, description=None):
        self.name = name
        self.pos = button_pos
        render_pos_x = 0
        render_pos_y = 0
        if 0 <= button_pos <= 3:
            render_pos_y = hud_height - 182 + 7
        elif 4 <= button_pos <= 7:
            render_pos_y = hud_height - 182 + 62
        else:
            render_pos_y = hud_height - 182 + 115

        render_pos_x = 30 + self.width_between_icons * (button_pos % 4)
        self.render_pos = [render_pos_x, render_pos_y]
        self.icon = icon
        self.rect = self.icon.get_rect(topleft=self.render_pos)

        self.description = description
        self.enabled = True


