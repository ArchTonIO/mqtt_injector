class page():
    def __init__(self):
        self.MAX_LINES=24
        self.cursor=str()
        self.right_cursor=str()
        self.cursor_position=int()
        self.options_lines=[str()]*self.MAX_LINES
        self.page_lines=[str()]*self.MAX_LINES
        self.page_id=int()
        self.is_leaf=bool()

    def build_page(self, curors_at_screen_border=False) -> None:
        for i in range(len(self.options_lines)):
            if i==self.cursor_position:
                num_spaces=int((16-(len(self.cursor)+len(self.options_lines[i])))/2)
                spaces=" "*num_spaces
                if len(self.options_lines[i])%2!=0:
                    spaces=" "*(num_spaces-1)
                if curors_at_screen_border:
                    self.page_lines[i]=(self.cursor
                                        +spaces
                                        +self.options_lines[i]
                                        +spaces
                                        +self.right_cursor)
                else:
                    self.page_lines[i]=(spaces
                                        +self.cursor
                                        +self.options_lines[i]
                                        +self.right_cursor
                                        +spaces)
            else:
                num_spaces=int((16-len(self.options_lines[i]))/2)
                spaces=" "*num_spaces
                self.page_lines[i]=spaces+self.options_lines[i]+spaces
    