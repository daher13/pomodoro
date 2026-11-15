import gi

# Pin the GTK versions once, before any module imports gi.repository.Gtk/Gdk
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")