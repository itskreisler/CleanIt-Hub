import gi
import os

os.environ["GSK_RENDERER"] = "cairo"
os.environ["GDK_BACKEND"] = "x11"
import sys
import shutil
import subprocess
import math

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

APT_DIR = "/var/cache/apt/archives"
CACHE_DIR = os.path.expanduser("~/.cache")
TEMP_DIRS = ["/tmp", os.path.expanduser("~/.cache")]
THUMBNAILS_DIR = os.path.expanduser(".cache/thumbnails")


def get_folder_size(path):
    total = 0
    if not os.path.exists(path):
        return 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                try:
                    total += os.path.getsize(fp)
                except:
                    pass
    return total


def format_size(size_bytes):
    if size_bytes >= (1024**3):
        return f"{size_bytes / (1024**3):.2f} GB"
    elif size_bytes >= (1024**2):
        return f"{size_bytes / (1024**2):.1f} MB"
    else:
        return f"{size_bytes / 1024:.0f} KB"


class CleanItApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.galestrike.hub")
        self.connect("activate", self.on_activate)
        self.check_map = {}

    def on_activate(self, app):
        self.win = Gtk.ApplicationWindow(application=app, title="CleanIt Hub")
        self.win.set_default_size(450, 700)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            .orange-btn { background: #FF4500; color: white; border-radius: 20px; padding: 12px 24px; font-weight: bold; }
            .orange-btn:hover { background: #FF5722; }
            .card { background: #2a2a2a; border-radius: 12px; padding: 16px; margin: 8px; }
            .title-big { font-size: 42px; font-weight: bold; color: white; }
        """)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

        self.build_ui()
        self.win.present()

    def build_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        self.win.set_child(main_box)

        self.win.set_title("CleanIt Hub")
        header = Gtk.HeaderBar()
        self.win.set_titlebar(header)

        disk_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            spacing=5,
        )
        disk_box.set_margin_top(30)
        disk_box.set_margin_bottom(30)
        main_box.append(disk_box)

        total, used, free = shutil.disk_usage("/")
        usage_label = Gtk.Label()
        usage_label.set_markup(
            f'<span size="46000" weight="bold" foreground="#FF4500">{format_size(used)}</span>'
        )
        disk_box.append(usage_label)

        subtitle = Gtk.Label(label="of disk space used")
        subtitle.set_css_classes(["dim-label"])
        disk_box.append(subtitle)

        sep = Gtk.Separator()
        main_box.append(sep)

        btn_cache = Gtk.Button(label="Cache Cleaner")
        btn_cache.set_css_classes(["orange-btn"])
        btn_cache.connect("clicked", self.open_cleaner)
        main_box.append(btn_cache)

        btn_temp = Gtk.Button(label="Temp Files")
        btn_temp.set_css_classes(["orange-btn"])
        btn_temp.connect("clicked", self.open_temp_cleaner)
        main_box.append(btn_temp)

        btn_thumb = Gtk.Button(label="Thumbnails")
        btn_thumb.set_css_classes(["orange-btn"])
        btn_thumb.connect("clicked", self.open_thumbnail_cleaner)
        main_box.append(btn_thumb)

        btn_large = Gtk.Button(label="Large Files")
        btn_large.set_css_classes(["orange-btn"])
        btn_large.connect("clicked", self.find_large_files)
        main_box.append(btn_large)

        btn_update = Gtk.Button(label="Update CleanIt")
        btn_update.connect("clicked", self.update_app)
        main_box.append(btn_update)

    def open_cleaner(self, btn):
        dialog = Gtk.Window(title="Cache Cleaner")
        dialog.set_default_size(400, 600)
        dialog.set_transient_for(self.win)
        dialog.set_modal(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        dialog.set_child(box)

        dialog.set_title("Select Caches to Clean")
        header = Gtk.HeaderBar()
        dialog.set_titlebar(header)

        self.check_map.clear()
        self.scanned_rows = []

        self.status_label = Gtk.Label(label="0 MB selected")
        box.append(self.status_label)

        scroller = Gtk.ScrolledWindow()
        scroller.set_vexpand(True)
        box.append(scroller)

        list_box = Gtk.ListBox()
        scroller.set_child(list_box)

        apt_size = get_folder_size(APT_DIR)
        self.add_row(list_box, "APT Packages", APT_DIR, apt_size)

        if os.path.exists(CACHE_DIR):
            folders = [
                (
                    i,
                    os.path.join(CACHE_DIR, i),
                    get_folder_size(os.path.join(CACHE_DIR, i)),
                )
                for i in os.listdir(CACHE_DIR)
                if os.path.isdir(os.path.join(CACHE_DIR, i))
                and get_folder_size(os.path.join(CACHE_DIR, i)) > 0
            ]
            for n, p, s in sorted(folders, key=lambda x: x[2], reverse=True)[:5]:
                self.add_row(list_box, n.capitalize() + " Cache", p, s)

        btn_clean = Gtk.Button(label="Clean System")
        btn_clean.set_css_classes(["orange-btn"])
        btn_clean.connect("clicked", lambda x: self.clean_selected(dialog))
        box.append(btn_clean)

        dialog.present()

    def open_temp_cleaner(self, btn):
        dialog = Gtk.Window(title="Temp Files")
        dialog.set_default_size(400, 500)
        dialog.set_transient_for(self.win)
        dialog.set_modal(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin(20)
        dialog.set_child(box)

        dialog.set_title("Clean Temp Files")
        header = Gtk.HeaderBar()
        dialog.set_titlebar(header)

        self.check_map.clear()

        self.status_label = Gtk.Label(label="0 MB selected")
        box.append(self.status_label)

        scroller = Gtk.ScrolledWindow()
        scroller.set_vexpand(True)
        box.append(scroller)

        list_box = Gtk.ListBox()
        scroller.set_child(list_box)

        for temp_path in TEMP_DIRS:
            if os.path.exists(temp_path):
                size = get_folder_size(temp_path)
                name = (
                    os.path.basename(temp_path)
                    if temp_path.startswith("/home")
                    else temp_path
                )
                self.add_row(list_box, name + " (" + temp_path + ")", temp_path, size)

        btn_clean = Gtk.Button(label="Clean Temp Files")
        btn_clean.set_css_classes(["orange-btn"])
        btn_clean.connect("clicked", lambda x: self.clean_selected(dialog))
        box.append(btn_clean)

        dialog.present()

    def open_thumbnail_cleaner(self, btn):
        dialog = Gtk.Window(title="Thumbnails")
        dialog.set_default_size(400, 400)
        dialog.set_transient_for(self.win)
        dialog.set_modal(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin(20)
        dialog.set_child(box)

        dialog.set_title("Clean Thumbnails")
        header = Gtk.HeaderBar()
        dialog.set_titlebar(header)

        self.check_map.clear()

        size = get_folder_size(THUMBNAILS_DIR)
        list_box = Gtk.ListBox()
        box.append(list_box)
        self.add_row(list_box, "Thumbnails Cache", THUMBNAILS_DIR, size)

        btn_clean = Gtk.Button(label="Clean Thumbnails")
        btn_clean.set_css_classes(["orange-btn"])
        btn_clean.connect("clicked", lambda x: self.clean_thumbnails(dialog))
        box.append(btn_clean)

        dialog.present()

    def clean_thumbnails(self, dialog):
        freed = 0
        for c, d in self.check_map.items():
            if c.get_active() and d["size"] > 0:
                try:
                    if os.path.exists(d["path"]):
                        shutil.rmtree(d["path"])
                        freed += d["size"]
                except:
                    pass
        dialog.close()
        dialog.destroy()
        self.show_summary(freed)

    def clean_selected(self, dialog):
        freed = 0
        for c, d in self.check_map.items():
            if c.get_active() and d["size"] > 0:
                try:
                    subprocess.run(["apt-get", "clean"], check=True)
                except:
                    pass
                try:
                    if os.path.exists(d["path"]):
                        shutil.rmtree(d["path"])
                        freed += d["size"]
                except:
                    pass
        dialog.close()
        dialog.destroy()
        self.show_summary(freed)

    def show_summary(self, freed):
        dialog = Gtk.Window(title="Cleanup Complete")
        dialog.set_default_size(350, 250)
        dialog.set_transient_for(self.win)
        dialog.set_modal(True)

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=15,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
        )
        box.set_margin(30)
        dialog.set_child(box)

        label = Gtk.Label()
        label.set_markup(
            f"<span size='28000' weight='bold'>✅ Cleaned</span>\n\n<span size='20000' foreground='#FF4500'>{format_size(freed)}</span>\n<span size='14000'>freed disk space</span>"
        )
        box.append(label)

        btn_close = Gtk.Button(label="Close")
        btn_close.connect("clicked", lambda x: dialog.close())
        box.append(btn_close)

        dialog.present()

    def find_large_files(self, btn):
        dialog = Gtk.Window(title="Large Files")
        dialog.set_default_size(500, 600)
        dialog.set_transient_for(self.win)
        dialog.set_modal(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin(20)
        dialog.set_child(box)

        dialog.set_title("Files > 100 MB")
        header = Gtk.HeaderBar()
        dialog.set_titlebar(header)

        scroller = Gtk.ScrolledWindow()
        scroller.set_vexpand(True)
        box.append(scroller)

        list_box = Gtk.ListBox()
        scroller.set_child(list_box)

        loading = Gtk.Label(label="Scanning...")
        box.append(loading)
        while Gtk.events_pending():
            Gtk.main_iteration()

        large_files = []
        for root, _, files in os.walk("/"):
            for f in files:
                try:
                    fp = os.path.join(root, f)
                    size = os.path.getsize(fp)
                    if size > 100 * 1024 * 1024:
                        large_files.append((fp, size))
                except:
                    pass

        large_files.sort(key=lambda x: x[1], reverse=True)
        large_files = large_files[:50]

        box.remove(loading)

        for fp, size in large_files:
            row = Gtk.ListBoxRow()
            row_box = Gtk.Box(spacing=10)
            row_box.set_margin(8)
            row.set_child(row_box)
            label = Gtk.Label(label=f"{format_size(size)}\n{fp}", xalign=0)
            label.set_hexpand(True)
            row_box.append(label)
            list_box.append(row)

        btn_close = Gtk.Button(label="Close")
        btn_close.connect("clicked", lambda x: dialog.close())
        box.append(btn_close)

        dialog.present()

    def update_app(self, btn):
        github_url = (
            "https://raw.githubusercontent.com/galestrikee/Cleaner/main/cleanit.py"
        )
        try:
            subprocess.run(
                ["curl", "-sL", github_url, "-o", os.path.abspath(__file__)], check=True
            )
            os.execv(sys.executable, ["python3"] + sys.argv)
        except:
            pass


if __name__ == "__main__":
    app = CleanItApp()
    app.run(None)
