from gi.repository import Gtk

from .state import load_history

class ReportDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Report", transient_for=parent, modal=True)
        self.add_button("Close", Gtk.ResponseType.CLOSE)
        self.set_default_size(280, 340)

        history = load_history()
        store = Gtk.ListStore(str, int)
        for day in sorted(history, reverse=True):
            store.append([day, history[day]])

        view = Gtk.TreeView(model=store)
        for index, title in enumerate(("Date", "Pomodoros")):
            view.append_column(Gtk.TreeViewColumn(title, Gtk.CellRendererText(), text=index))

        scroll = Gtk.ScrolledWindow(vexpand=True, margin=15)
        scroll.add(view)
        total = Gtk.Label(label=f"Total: {sum(history.values())}", margin_bottom=10)
        area = self.get_content_area()
        area.pack_start(scroll, True, True, 0)
        area.pack_start(total, False, False, 0)
        self.show_all()