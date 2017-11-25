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


from functools import partial

class Node(Widget):

#HEY NOTE: I'm sorry, but event bubbling's a pain, so just don't add children to this widget that need touch. It shouldn't have 'em anyways.
#ALSO: Always follow a pattern of create -> adjust relevant prev_node/next_node and head/tail -> add_widget, which calls setup, which relies on these
    
    def __init__(self, x, y):   #Pass in x,y of center of node, not corner like usual
        Widget.__init__(self)
        self.MIN_DRAG_DIST = 100
        self.SIZE = 0.05
        self.COLOR = Color(1,1,1)

        self.prev_node = None;  #Linked List. Should be handled by the layout.
        self.next_node = None;

        self.being_dragged = False      # < Various variables for implementing the drag behavior
        self.clicked_on = False             #These are mostly self-explanatory, but 'drag_node' is the new node
        self.drag_node = None               #   made on an 'insert before' op. last_pos becomes None for
        self.last_pos = (None, None)        #   the new one, which prevents delete or double on_touch_up

        self._setup = partial(self.setup, x, y) 
        self.bind(parent=self._setup)   #call setup ONCE when this is first attached to a thingy.

    def setup(self, x, y, _self, _parent): #DON'T unattach and reattach to anything
        self.unbind(parent=self._setup)         #We don't want to call this on deleting it
        self.size_hint = (self.SIZE, self.SIZE)
        self.conv_pos((x,y))    #set pos_hint
        self.canvas.add(self.COLOR)
        self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.canvas.add(self.bg_rect)
        self.head_sign = InstructionGroup()
        self.head_sign.add(Color(0,0,1))
        self.head_sign_rect = Rectangle(pos=(self.pos[0]+self.size[0]/4, self.pos[1]+self.size[1]/4), size=(self.size[0]/2, self.size[1]/2))
        self.head_sign.add(self.head_sign_rect)
        self.head_sign.add(self.COLOR)
        self.prev_line = Line(width=1)
        if self.prev_node is None:
            self.canvas.add(self.head_sign)
        else:
            self.prev_line.points=[self.prev_node.pos[0]+self.prev_node.size[0]/2, self.prev_node.pos[1]+self.prev_node.size[1]/2, x, y]
            self.canvas.add(self.prev_line)

        self.bind(pos=self.redraw, size=self.redraw)

    def conv_pos(self, pos):
        self.pos_hint = { 'x' : pos[0] / self.parent.size[0] - self.SIZE/2, 'y': pos[1] / self.parent.size[1] - self.SIZE/2 }

    def redraw(self, pointless_variable_because_apparently_self_is_getting_passed_twice_for_some_reason, other_args_question_mark):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.head_sign_rect.pos = (self.pos[0]+self.size[0]/4, self.pos[1]+self.size[1]/4)
        self.head_sign_rect.size = (self.size[0]/2, self.size[1]/2)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.clicked_on = True
            self.last_pos = touch.pos
            return True
        return False
    def on_touch_move(self, touch):
        if self.clicked_on:
            if not self.being_dragged and pow(touch.pos[0]-self.last_pos[0],2)+pow(touch.pos[1]-self.last_pos[1],2) >= self.MIN_DRAG_DIST:
                self.being_dragged = True
                if self.parent.click_type:
                    self.drag_node = Node(*touch.pos)
                    self.drag_node.being_dragged = True
                    self.drag_node.clicked_on = True

                    self.drag_node.next_node = self
                    self.drag_node.prev_node = self.prev_node
                    if self.prev_node is None:
                        self.parent.head = self.drag_node
                        self.canvas.remove(self.head_sign)
                        self.canvas.add(self.prev_line)
                    else:
                        self.prev_node.next_node = self.drag_node
                    self.prev_node = self.drag_node
                    self.parent.add_widget(self.drag_node)
            if self.being_dragged and (not self.parent.click_type or self.last_pos[0] is None):
                    self.conv_pos(touch.pos)
                    if self.prev_node is not None:
                        self.prev_line.points=[self.prev_node.pos[0]+self.prev_node.size[0]/2, self.prev_node.pos[1]+self.prev_node.size[1]/2, self.pos[0]+self.size[0]/2, self.pos[1]+self.size[1]/2]
                    if self.next_node is not None:
                        self.next_node.prev_line.points=[self.pos[0]+self.size[0]/2, self.pos[1]+self.size[1]/2, self.next_node.pos[0]+self.next_node.size[0]/2, self.next_node.pos[1]+self.next_node.size[1]/2]
            return True
        return False
    def on_touch_up(self, touch):
        if self.clicked_on and self.last_pos[0] is not None:
            if not self.being_dragged:
                if self.parent.click_type:
                    if self.prev_node is None:
                        self.parent.head = self.next_node
                    else:
                        self.prev_node.next_node = self.next_node
                    if self.next_node is None:
                        self.parent.tail = self.prev_node
                    else:
                        self.next_node.prev_node = self.prev_node
                        if self.prev_node is None:
                            self.next_node.canvas.remove(self.next_node.prev_line)
                            self.next_node.canvas.add(self.next_node.head_sign)
                        else:
                            self.next_node.prev_line.points=[self.prev_node.pos[0]+self.prev_node.size[0]/2, self.prev_node.pos[1]+self.prev_node.size[1]/2, self.next_node.pos[0]+self.next_node.size[0]/2, self.next_node.pos[1]+self.next_node.size[1]/2]
                            #self.next_node.canvas.ask_update()
                    self.parent.remove_widget(self)
                else:
                    print("select!")
            if self.drag_node is not None:
                self.drag_node.clicked_on = False
                self.drag_node.being_dragged = False
                self.drag_node = None
            self.clicked_on = False
            self.being_dragged = False
            self.last_pos = (None, None)
            return True
        return False


class MyScreen(FloatLayout):
    def __init__(self):
        FloatLayout.__init__(self)

        self.head = None#Node(0.2, 0.5)
        self.tail = self.head

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
                if self.tail is None:
                    self.tail = Node(*touch.pos)
                    if self.head is None:
                        self.head = self.tail
                else:
                    self.tail.next_node = Node(*touch.pos)  #sadly python has dumb chained assignments
                    self.tail.next_node.prev_node = self.tail
                    self.tail = self.tail.next_node
                self.add_widget(self.tail)
            else:
                print("deselect!")


class MyApp(App):

    def build(self):
        return MyScreen()

if __name__ == '__main__':
    MyApp().run()
