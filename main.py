import kivy

from kivy.app import App

from kivy.core.window import Window

from kivy.uix.floatlayout import FloatLayout 
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.behaviors import DragBehavior


class Node(DragBehavior, Button):
    def __init__(self, **kwargs):
        Button.__init__(self)
        DragBehavior.__init__(self)
        self.setup()
        
    def setup(self):
        self.dropdown = DropDown()
        self.dropdown.add_widget(Button(text='Reset', font_size='8sp', size_hint_y=None, height=20))
        self.dropdown.add_widget(Button(text='Add Command', font_size='8sp', size_hint_y=None, height=20))

        self.text='Node'
        self.font_size='8sp'

        self.drag_rect_x = 0
        self.drag_rect_y = 0
        self.drag_rect_height = Window.size[1]
        self.drag_rect_width = Window.size[0]

        self.size_hint = (None, None)
        self.size=(30,30)
        self.pos=(50, 70)
        self.bind(on_release=self.dropdown.open)


class MyScreen(FloatLayout):
    def __init__(self, **kwargs):
        super(MyScreen, self).__init__()
        self.setup()
        
    def setup(self):
        node = Node()
        self.add_widget(node)
        


class MyApp(App):

    def build(self):
        return MyScreen()

if __name__ == '__main__':
    MyApp().run()
