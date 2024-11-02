from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior


class ImageButton(ButtonBehavior,Image):       #weŕe creating a image, with button behavior
    pass

class LabelButton(ButtonBehavior, Label):       #weŕe creating a text, with button behavior too
    pass