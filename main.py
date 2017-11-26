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

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner

from functools import partial

class Node(Widget):

#HEY NOTE: I'm sorry, but event bubbling's a pain, so just don't add children to this widget that need touch. It shouldn't have 'em anyways.
#ALSO: Always follow a pattern of create -> adjust relevant prev_node/next_node and head/tail -> add_widget, which calls setup, which relies on these
#And don't attach/remove/reattach to something. I haven't tried it but I bet things will break.
    
    def __init__(self, x, y):   #Pass in x,y of center of node, not corner like usual
        Widget.__init__(self)
        self.MIN_DRAG_VAL = (20)**2   #squared so I don't need to take a root later
        self.SIZE = 0.05
        self.COLOR = Color(1,1,1)

        self.prev_node = None;  #Linked List of nodes
        self.next_node = None;

        self.being_dragged = False      # < Various variables for implementing the drag behavior
        self.clicked_on = False             #These are mostly self-explanatory, but 'drag_node' is the new node
        self.drag_node = None               #   made on an 'insert before' op. last_pos becomes None for
        self.last_pos = (None, None)        #   the new one, which prevents deletion or doubled on_touch_up

        self.command_list = []

        self._setup = partial(self.setup, x, y) 
        self.bind(parent=self._setup)   #used to call setup ONCE when this is first attached to a thingy.

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
            if not self.being_dragged and pow(touch.pos[0]-self.last_pos[0],2)+pow(touch.pos[1]-self.last_pos[1],2) >= self.MIN_DRAG_VAL:
                self.being_dragged = True
                if self.parent.click_type:
                    self.drag_node = Node(*touch.pos)
                    self.drag_node.clicked_on = True
                    self.drag_node.being_dragged = True

                    self.drag_node.next_node = self
                    self.drag_node.prev_node = self.prev_node
                    if self.prev_node is None:
                        self.parent.head = self.drag_node
                        self.canvas.remove(self.head_sign)  #drag_node will add in its own constructor
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
                    if self.parent.command_menu is not None and self.parent.command_menu.node is self:
                        self.parent.remove_widget(self.parent.command_menu)
                        self.parent.command_menu.store_list()
                        self.parent.command_menu = None
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
                    self.parent.remove_widget(self)
                else:
                    if self.parent.command_menu is not None:
                        self.parent.remove_widget(self.parent.command_menu)
                        self.parent.command_menu.store_list()
                    self.parent.command_menu = CommandMenu(self)
                    self.parent.add_widget(self.parent.command_menu)
            if self.drag_node is not None:
                self.drag_node.clicked_on = False
                self.drag_node.being_dragged = False
                self.drag_node = None
            self.clicked_on = False
            self.being_dragged = False
            self.last_pos = (None, None)
            return True
        return False


class SideButtons(DragBehavior, BoxLayout):
    def __init__(self):
        DragBehavior.__init__(self)
        BoxLayout.__init__(self, orientation='vertical', size_hint=(None, None), width=75)
        self.bind(pos=self.drag_set, size=self.drag_set)

        self.switch = Button(text="Select");
        def switch_callback(instance):
            self.parent.click_type = not self.parent.click_type
            self.switch.text = "Create" if self.parent.click_type else "Select"
            #self.parent.dont_check = True
        self.switch.bind(on_press=switch_callback)
        self.add_widget(self.switch)

        self.herod = Button(text="Clear");
        def clear_callback(instance):
            #self.parent.dont_check = True
            while self.parent.head is not None:
                self.parent.remove_widget(self.parent.head)
                self.parent.head = self.parent.head.next_node
            self.parent.tail = None
        self.herod.bind(on_press=clear_callback)
        self.add_widget(self.herod)

        self.sizer = Button(text="Settings");
        def sizer_callback(instance):
            #self.parent.dont_check = True
            print("This should bring up a menu to set field boundaries")
        self.sizer.bind(on_press=sizer_callback)
        self.add_widget(self.sizer)

        self.encode = Button(text="Encode");
        def encode_callback(instance):
            #self.parent.dont_check = True
            print("Add the encode stuff here! Maybe specify a file?")
        self.encode.bind(on_press=encode_callback)
        self.add_widget(self.encode)

        self.importer = Button(text="Import");
        def importer_callback(instance):
            #self.parent.dont_check = True
            print("Definitely add a menu to allow for entering a target file here, then fancy stuff to recreate the tree.")
        self.importer.bind(on_press=importer_callback)
        self.add_widget(self.importer)

    def drag_set(self, _1, _2):
        self.drag_rectangle = [self.x, self.y, self.width, self.height]

class CommandMenu(BoxLayout):
    def __init__(self, node_):
        BoxLayout.__init__(self, orientation='vertical', size_hint=(0.25,1), pos_hint={'x': 0.75 if node_.pos_hint['x'] <= 0.5 else 0, 'y': 0})
        self.node = node_

        self.add_below = Button(text="dataquestionmark", size_hint=(1, None), height=0.36*self.height) 
        def add_below_callback(instance):
            self.parent.dont_check = True
        self.add_below.bind(on_press=add_below_callback)
        self.add_widget(self.add_below)

        self.scroller = ScrollView(size_hint=(1,1), do_scroll_y=True, do_scroll_x=False)
        self.add_widget(self.scroller)
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.scroller.add_widget(self.grid)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.bind(pos=self.redraw, size=self.redraw)

        if len(self.node.command_list) == 0:
            self.grid.add_widget(SetCommandButton())
        else:
            for i in self.node.command_list:
                self.grid.add_widget(SetCommandButton(val=i))

    def redraw(self, _1, _2):
        self.add_below.height=0.36*self.height
        for i in self.grid.children:
            i.height = 0.2*self.height

    def store_list(self):
        for i in self.grid.children:
            if i.command != "" and i.command != "(Set Command)":
                self.node.command_list.append(i.command)


class SetCommandButton(GridLayout):
    def __init__(self, val = "(Set Command)"):
        GridLayout.__init__(self, cols=1, spacing=10, size_hint_y=None)
        self.bind(minimum_height=self.setter('height'))
        self.bind(pos=self.redraw, size=self.redraw)

        class MiniButton(BoxLayout):
            def __init__(self, widget):
                BoxLayout.__init__(self, size_hint_y=None, height=40)
                self.widget = widget
                self.add_widget(Label(size_hint_x=0.3))
                self.add_widget(self.widget)

        self.b_open = False
        self.main = Button(text=val, size_hint_y=None, height=40)
        self.main.bind(on_press=self.main_callback)
        self.add_widget(self.main)

        self.edit = MiniButton(Button(text="Change Command:"))
        self.edit.widget.bind(on_press=self.edit_callback)
        self.remove = MiniButton(Button(text="Remove Command"))
        self.remove.widget.bind(on_press=self.remove_callback)
        self.add_up = MiniButton(Button(text="Add Command Above"))
        self.add_up.widget.bind(on_press=self.add_up_callback)
        self.add_down = MiniButton(Button(text="Add Command Below"))
        self.add_down.widget.bind(on_press=self.add_down_callback)

        self.command = ""

    def main_callback(self, instance):
        for i in self.parent.children:
            if i.b_open:
                i.remove_widget(i.edit)
                i.remove_widget(i.remove)
                i.remove_widget(i.add_up)
                i.remove_widget(i.add_down)
        self.b_open = not self.b_open
        if self.b_open:
            self.add_widget(self.edit)
            self.add_widget(self.remove)
            self.add_widget(self.add_up)
            self.add_widget(self.add_down)
    def edit_callback(self, instance):
        blah = Popup(title="Choose Command", content=Spinner(text=self.edit.widget.text, values=('Turn On Camera', 'Turn Off Camera')), size_hint=(0.5,0.5))
        def choose(inst, value):
            self.main.text = self.command = blah.content.text
            blah.dismiss()
        blah.content.bind(text=choose)
        blah.open()
    def add_up_callback(self, instance):
        self.parent.add_widget(SetCommandButton(), index=self.parent.children.index(self))
    def add_down_callback(self, instance):
        self.parent.add_widget(SetCommandButton(), index=self.parent.children.index(self))
    def remove_callback(self, instance):
        if len(self.parent.children) > 1:
            self.parent.remove_widget(self)

    def redraw(self, _1, _2):
        for i in self.children:
            i.height = 0.15*self.parent.parent.height
        

class MyScreen(FloatLayout):
    def __init__(self):
        FloatLayout.__init__(self)

        self.head = None#Node(0.2, 0.5)
        self.tail = self.head

        self.command_menu = None

        self.click_type = False #What mode it's in -- select or create
        self.dont_check = False #I think normal buttons pass on on_touch_up even when they took the event, so this prevents that from being processed

        self.buttons = SideButtons()
        self.add_widget(self.buttons)

    def on_touch_down(self, touch):
        if not super(MyScreen, self).on_touch_down(touch):
            pass
    def on_touch_up(self, touch):
        if not super(MyScreen, self).on_touch_up(touch): 
            if self.dont_check: #Note: Draggable seems to make this less of an issue now
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
                if self.command_menu is not None:
                    self.remove_widget(self.command_menu)
                    self.command_menu.store_list()
                    self.command_menu = None


class MyApp(App):

    def build(self):
        return MyScreen()

if __name__ == '__main__':
    MyApp().run()
