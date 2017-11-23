import kivy

from kivy.app import App

from kivy.core.window import Window

from kivy.graphics import *

from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout 
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.behaviors import DragBehavior

class Node(Widget):

#HEY NOTE: I'm sorry, but event bubbling's a pain, so just don't add children to this widget. It shouldn't have 'em anyways.

    def __init__(self, x, y):
        Widget.__init__(self)
        self.MIN_DRAG_DIST = 100        # < Constants
        self.being_dragged = False      # < Various variables for implementing the drag behavior
        self.clicked_on = False             #These are mostly self-explanatory, but 'node' is the new node
        self.node = None                    #   made on an 'insert before' op. last_pos becomes None for
        self.last_pos = (None, None)        #   the new one, which prevents delete or double on_touch_up
        self.text='Node'                # < Appearance
        self.font_size='8sp'
        self.size_hint = (None, None)
        self.size=(30,30)
        self.pos=(x, y)
        with self.canvas:
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.redraw, size=self.redraw)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.clicked_on = True
            self.last_pos = touch.pos
            return True
        return False
    def on_touch_move(self, touch):
        if self.clicked_on:
            if not self.being_dragged and pow(touch.pos[0]-self.last_pos[0],2)+pow(touch.pos[1]-self.last_pos[1],2) <= self.MIN_DRAG_DIST:
                self.being_dragged = True
                if self.parent.click_type:
                    self.node = Node(touch.pos[0]-30/2, touch.pos[1]-30/2)
                    self.node.being_dragged = True
                    self.node.clicked_on = True
                    self.parent.add_widget(self.node)   #Note: use the linked list in the future
            if self.being_dragged and (not self.parent.click_type or self.last_pos[0] is None):
                    self.pos = (touch.pos[0]-30/2, touch.pos[1]-30/2)
            return True
        return False
    def on_touch_up(self, touch):
        if self.clicked_on and self.last_pos[0] is not None:
            if self.parent.click_type:
                if self.being_dragged:
                    print("make new uberconnected dude!")
                else:
                    self.parent.remove_widget(self)
            else:
                if self.being_dragged:
                    pass
                else:
                    print("select!")
            if self.node is not None:
                self.node.clicked_on = False
                self.node.being_dragged = False
                self.node = None
            self.clicked_on = False
            self.being_dragged = False
            self.last_pos = (None, None)
            return True
        return False

    def redraw(self, pointless_variable_because_apparently_self_is_getting_passed_twice_for_some_reason, other_args_question_mark):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos


class MyScreen(FloatLayout):
    def __init__(self):
        FloatLayout.__init__(self)

        self.click_type = False #What mode it's in -- select or create
        self.dont_check = False #I think normal buttons pass on on_touch_up even when they took the event, so this prevents that from being processed
        self.button = Button(text="Select", size_hint=(0.05,0.05));
        def callback(instance):
            self.click_type = not self.click_type
            self.button.text = "Create" if self.click_type else "Select"
            self.dont_check = True
        self.button.bind(on_press=callback)
        self.add_widget(self.button)

    def on_touch_down(self, touch):
        if not super(MyScreen, self).on_touch_down(touch):
            pass
    def on_touch_up(self, touch):
        if not super(MyScreen, self).on_touch_up(touch): 
            if self.dont_check:
                self.dont_check = False
            elif self.click_type:
                self.add_widget(Node(touch.pos[0]-30/2, touch.pos[1]-30/2))
            else:
                print("deselect!")


class MyApp(App):

    def build(self):
        return MyScreen()

if __name__ == '__main__':
    MyApp().run()
