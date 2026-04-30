from Option import Option


class Menu:
    """
    Each Menu instance represents a list of options.  Each option is just
    a prompt, and an action (text string) to take if that option is selected.
    menu_prompt displays the options, assigns each a successive number, and
    returns the action text for the selection — the caller uses exec() to run it.
    """

    def __init__(self, name: str, prompt: str, options: list):
        self.name    = name
        self.prompt  = prompt
        self.options = options

    def menu_prompt(self) -> str:
        results:   bool = False
        final:     int  = -1
        n_options: int  = len(self.options)
        while not results:
            print(self.prompt)
            index: int = 0
            for option in self.options:
                index += 1
                print("%3d - %s" % (index, option.get_prompt()))
            try:
                final = int(input('-->'))
                if final < 1 or final > n_options:
                    print("Choice is out of range, try again.")
                    results = False
                else:
                    results = True
            except ValueError:
                print("Not a valid integer, try again.")
        return self.options[final - 1].get_action()

    def last_action(self):
        """Return the action of the very last option (conventionally the exit option)."""
        return self.options[len(self.options) - 1].get_action()
