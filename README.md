# CleanIt Hub - Ubuntu Setup

## Requisitos

```bash
# Instalar GTK4 para Python
pip install pycairo PyGObject
sudo apt install libgirepository1.0-dev libcairo2-dev gir1.2-gtk-4.0
```

## Cambios realizados en cleanit.py

### 1. HeaderBar - set_title() eliminado (GTK4)
**Antes:**
```python
header = Gtk.HeaderBar()
header.set_title("CleanIt Hub")
```

**Después:**
```python
self.win.set_title("CleanIt Hub")
header = Gtk.HeaderBar()
```

Lo mismo para el diálogo de caché.

### 2. Mostrar ruta exacta en lista de limpieza
**Antes:**
```python
label = Gtk.Label(label=f"{name}\n{format_size(size)}", xalign=0)
```

**Después:**
```python
label = Gtk.Label(label=f"{name}\n{format_size(size)}\n{path}", xalign=0)
```

## Uso

```bash
python3 ~/.termux-cleaner/cleanit.py
```

## Notas

- Los warnings de DRI3 son informativos, no afectan el funcionamiento
- El script funciona con GTK4 (Ubuntu 22.04+)
